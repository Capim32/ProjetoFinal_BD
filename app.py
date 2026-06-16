from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import errors
import os
from dotenv import load_dotenv

app = Flask(__name__)

URL_DO_BANCO = os.getenv("URL_DO_BANCO")

def conectar_banco():
    return psycopg2.connect(URL_DO_BANCO)

# ====================================================
# 1. ROTA DE LISTAGEM (Página Inicial Completa)
# ====================================================
@app.route('/')
def tela_inicial():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    termo_busca = request.args.get('busca')
    if termo_busca:
        cursor.execute("""
            SELECT p.paciente_id, p.nome, p.cpf, p.telefone, 
                   c.nome_convenio, c.num_carteira, 
                   part.limite_credito
            FROM paciente p
            LEFT JOIN conveniado c ON p.paciente_id = c.paciente_id
            LEFT JOIN particular part ON p.paciente_id = part.paciente_id
            WHERE p.nome ILIKE %s ORDER BY p.paciente_id;
        """, (f"%{termo_busca}%",))
    else:
        cursor.execute("""
            SELECT p.paciente_id, p.nome, p.cpf, p.telefone, 
                   c.nome_convenio, c.num_carteira, 
                   part.limite_credito
            FROM paciente p
            LEFT JOIN conveniado c ON p.paciente_id = c.paciente_id
            LEFT JOIN particular part ON p.paciente_id = part.paciente_id
            ORDER BY p.paciente_id;
        """)
    lista_pacientes = cursor.fetchall()

    cursor.execute("SELECT nome_dependente, paciente_id, data_nascimento, telefone FROM dependente;")
    lista_dependentes = cursor.fetchall()
    
    cursor.execute("""
        SELECT m.medico_id, m.nome, m.crm, e.nome 
        FROM medico m
        LEFT JOIN especialidade e ON m.espec_id = e.espec_id
        ORDER BY m.medico_id;
    """)
    lista_medicos = cursor.fetchall()
    
    cursor.execute("SELECT espec_id, nome FROM especialidade ORDER BY nome;")
    lista_especialidades = cursor.fetchall()
    
    cursor.execute("SELECT hospital_id, nome, cnpj FROM hospital ORDER BY nome;")
    lista_hospitais = cursor.fetchall()
    
    erro = request.args.get('erro') 
    
    cursor.close()
    conexao.close()
    
    return render_template('index.html', 
                           pacientes=lista_pacientes, 
                           dependentes=lista_dependentes, 
                           medicos=lista_medicos, 
                           especialidades=lista_especialidades,
                           hospitais=lista_hospitais,
                           erro=erro, 
                           busca_atual=termo_busca)

# ====================================================
# ROTAS DE PACIENTE
# ====================================================
@app.route('/inserir_paciente', methods=['POST'])
def inserir_paciente():
    nome_digitado = request.form['nome']
    cpf_puro = request.form['cpf']
    telefone_digitado = request.form['telefone']
    tipo_paciente = request.form['tipo_paciente']

    cpf_limpo = cpf_puro.replace('.', '').replace('-', '').replace(' ', '')
    if len(cpf_limpo) == 11:
        cpf_formatado = f"{cpf_limpo[0:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:11]}"
    else:
        cpf_formatado = cpf_limpo

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(paciente_id), 0) + 1 FROM paciente;")
        novo_id = cursor.fetchone()[0]
        
        # Insere na tabela base (Superclasse)
        cursor.execute("INSERT INTO paciente (paciente_id, nome, cpf, telefone) VALUES (%s, %s, %s, %s);", 
                       (novo_id, nome_digitado, cpf_formatado, telefone_digitado))
        
        # Insere na tabela especializada correspondente (Subclasse)
        if tipo_paciente == 'conveniado':
            nome_convenio = request.form['nome_convenio']
            num_carteira = request.form['num_carteira']
            cursor.execute("INSERT INTO conveniado (paciente_id, nome_convenio, num_carteira) VALUES (%s, %s, %s);",
                           (novo_id, nome_convenio, num_carteira))
        elif tipo_paciente == 'particular':
            limite_credito = request.form['limite_credito']
            if not limite_credito: 
                limite_credito = 0.00
            cursor.execute("INSERT INTO particular (paciente_id, limite_credito) VALUES (%s, %s);",
                           (novo_id, limite_credito))
        
        # Comita ambas as tabelas juntas na mesma transação
        conexao.commit()
    except errors.UniqueViolation:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Erro de Integridade: Este CPF já está cadastrado no sistema!"))
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro ao salvar especialização do paciente: {e}"))
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('tela_inicial'))

# ====================================================
# ROTAS DE DEPENDENTE
# ====================================================
@app.route('/inserir_dependente', methods=['POST'])
def inserir_dependente():
    nome_dependente = request.form['nome_dependente']
    paciente_id = request.form['paciente_id']
    data_nascimento = request.form['data_nascimento']
    telefone = request.form['telefone']

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            INSERT INTO dependente (nome_dependente, paciente_id, data_nascimento, telefone) 
            VALUES (%s, %s, %s, %s);
        """, (nome_dependente, paciente_id, data_nascimento, telefone))
        conexao.commit()
    except errors.UniqueViolation:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Erro de Integridade: Este paciente já possui um dependente com esse nome!"))
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro ao inserir dependente: {e}"))
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('tela_inicial'))

@app.route('/deletar_dependente/<int:id_paciente>/<string:nome_dependente>')
def deletar_dependente(id_paciente, nome_dependente):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM dependente WHERE paciente_id = %s AND nome_dependente = %s;", 
                       (id_paciente, nome_dependente))
        conexao.commit()
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro ao apagar dependente: {e}"))
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('tela_inicial'))

# ====================================================
# ROTAS DE MÉDICO
# ====================================================
@app.route('/inserir_medico', methods=['POST'])
def inserir_medico():
    nome_digitado = request.form['nome']
    crm_puro = request.form['crm']
    espec_id_selecionado = request.form['espec_id']

    crm_formatado = f"CRM{crm_puro.strip()}"

    if espec_id_selecionado == '0':
        espec_id_selecionado = None

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(medico_id), 0) + 1 FROM medico;")
        novo_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO medico (medico_id, nome, crm, espec_id) VALUES (%s, %s, %s, %s);", 
                       (novo_id, nome_digitado, crm_formatado, espec_id_selecionado))
        conexao.commit()
    except errors.UniqueViolation:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Erro de Integridade: Este CRM já está cadastrado!"))
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('tela_inicial'))

@app.route('/deletar_medico/<int:id_medico>')
def deletar_medico(id_medico):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM medico WHERE medico_id = %s;", (id_medico,))
        conexao.commit()
    except errors.ForeignKeyViolation:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Erro de Integridade: Não é possível apagar este médico pois ele já possui consultas agendadas no sistema."))
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro inesperado: {e}"))
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('tela_inicial'))

# ====================================================
# ROTAS DE HOSPITAIS E ATENDIMENTOS
# ====================================================
@app.route('/inserir_hospital', methods=['POST'])
def inserir_hospital():
    nome = request.form['nome']
    cnpj = request.form['cnpj']
    endereco = request.form['endereco']
    telefone = request.form['telefone']

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(hospital_id), 0) + 1 FROM hospital;")
        novo_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO hospital (hospital_id, cnpj, nome, endereco, telefone) 
            VALUES (%s, %s, %s, %s, %s);
        """, (novo_id, cnpj, nome, endereco, telefone))
        conexao.commit()
    except errors.UniqueViolation:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Erro: Já existe um hospital cadastrado com este CNPJ!"))
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro ao cadastrar hospital: {e}"))
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('tela_inicial'))

@app.route('/vincular_hospital', methods=['POST'])
def vincular_hospital():
    medico_id = request.form['medico_id']
    hospital_id = request.form['hospital_id']

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            INSERT INTO atende (medico_id, hospital_id) 
            VALUES (%s, %s);
        """, (medico_id, hospital_id))
        conexao.commit()
    except errors.UniqueViolation:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Vínculo duplicado: Este médico já está cadastrado neste hospital!"))
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro ao vincular médico: {e}"))
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('tela_inicial'))

# ====================================================
# ROTA DE CONSULTA
# ====================================================
@app.route('/inserir_consulta', methods=['POST'])
def inserir_consulta():
    medico_id = request.form['medico_id']
    paciente_id = request.form['paciente_id']
    data_hora_raw = request.form['data_hora']
    sala = request.form['sala']

    # Formata a string de data vinda do HTML para o formato aceito pelo timestamp do PostgreSQL
    data_hora = data_hora_raw.replace('T', ' ')

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(consulta_id), 0) + 1 FROM consulta;")
        novo_id = cursor.fetchone()[0]
        
        # Faz a inserção utilizando as FKs selecionadas e define o status inicial
        cursor.execute("""
            INSERT INTO consulta (consulta_id, medico_id, paciente_id, data_hora, sala, status) 
            VALUES (%s, %s, %s, %s, %s, 'Agendada');
        """, (novo_id, medico_id, paciente_id, data_hora, sala))
        conexao.commit()
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro ao agendar consulta: {e}"))
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('tela_inicial'))

# ====================================================
# ATUALIZAR STATUS DA CONSULTA (UPDATE)
# ====================================================
@app.route('/atualizar_status_consulta', methods=['POST'])
def atualizar_status_consulta():
    consulta_id = request.form['consulta_id']
    novo_status = request.form['novo_status'] # 'Agendada', 'Realizada' ou 'Cancelada'
    
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("UPDATE consulta SET status = %s WHERE consulta_id = %s;", (novo_status, consulta_id))
        conexao.commit()
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro ao atualizar: {e}"))
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('tela_inicial'))

# ====================================================
# ROTA DE PRESCRIÇÃO MÉDICA (Relação 1:1)
# ====================================================
@app.route('/inserir_prescricao', methods=['POST'])
def inserir_prescricao():
    consulta_id = request.form['consulta_id']
    medicamento = request.form['medicamento']
    dosagem = request.form['dosagem']

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(presc_id), 0) + 1 FROM prescricao;")
        novo_id = cursor.fetchone()[0]

        # Tenta inserir a prescrição atrelada à consulta
        cursor.execute("""
            INSERT INTO prescricao (presc_id, consulta_id, medicamento, dosagem) 
            VALUES (%s, %s, %s, %s);
        """, (novo_id, consulta_id, medicamento, dosagem))
        conexao.commit()
        
    except errors.UniqueViolation:
        # O banco bloqueia se já existir uma prescrição para este ID de consulta
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Segurança Clínica: Esta consulta já possui uma prescrição médica ativa! Não é possível emitir duplicidade."))
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro ao emitir prescrição: {e}"))
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('tela_inicial'))

# ====================================================
# TESTE DO GATILHO E PAGAMENTOS
# ====================================================
@app.route('/inserir_pagamento', methods=['POST'])
def inserir_pagamento():
    consulta_id = request.form['consulta_id']
    valor = request.form['valor']

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(pgto_id), 0) + 1 FROM pagamento;")
        novo_id = cursor.fetchone()[0]
        
        cursor.execute("INSERT INTO pagamento (pgto_id, consulta_id, valor, metodo) VALUES (%s, %s, %s, 'Pix');", 
                       (novo_id, consulta_id, valor))
        conexao.commit()
        
    except errors.RaiseException as e:
        # 1. Valor menor ou igual a zero
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Gatilho do Banco Acionado: {e}"))
        
    except errors.UniqueViolation:
        # 2. UNIQUE: Consulta já tem pagamento associado
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro de Integridade: A Consulta {consulta_id} já foi paga! O sistema bloqueou o pagamento duplicado."))
        
    except errors.ForeignKeyViolation:
        # 3. Chave Estrangeira: A consulta não existe
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro de Integridade: A Consulta {consulta_id} não existe no sistema. Verifique o ID."))
        
    except Exception as e:
        # Qualquer outro erro genérico
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro inesperado: {e}"))
        
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('tela_inicial'))

from flask import render_template_string

# ====================================================
# CENTRAL DE RELATÓRIOS (Master + Produtividade)
# ====================================================
@app.route('/relatorios')
def relatorios():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        # Mega Query (Junção de 9 Tabelas)
        cursor.execute("""
            SELECT 
                c.consulta_id, 
                TO_CHAR(c.data_hora, 'DD/MM/YYYY HH24:MI') AS data_hora, 
                c.status,
                p.nome AS paciente_nome,
                CASE 
                    WHEN conv.paciente_id IS NOT NULL THEN 'Conveniado (' || conv.nome_convenio || ')'
                    WHEN part.paciente_id IS NOT NULL THEN 'Particular'
                    ELSE 'Padrão'
                END AS tipo_paciente,
                m.nome AS medico_nome,
                e.nome AS especialidade,
                COALESCE(h.nome, 'Não vinculado') AS hospital,
                COALESCE('R$ ' || pg.valor::text, 'Aguardando Pagamento') AS valor,
                COALESCE(pg.metodo, '-') AS metodo,
                COALESCE(pr.medicamento || ' (' || pr.dosagem || ')', 'Nenhuma') AS prescricao
            FROM consulta c
            INNER JOIN paciente p ON c.paciente_id = p.paciente_id
            LEFT JOIN conveniado conv ON p.paciente_id = conv.paciente_id
            LEFT JOIN particular part ON p.paciente_id = part.paciente_id
            INNER JOIN medico m ON c.medico_id = m.medico_id
            LEFT JOIN especialidade e ON m.espec_id = e.espec_id
            LEFT JOIN hospital h ON m.hospital_id = h.hospital_id
            LEFT JOIN pagamento pg ON c.consulta_id = pg.consulta_id
            LEFT JOIN prescricao pr ON c.consulta_id = pr.consulta_id
            ORDER BY c.data_hora DESC, c.consulta_id DESC;
        """)
        dados_master = cursor.fetchall()

        # Relatório de Produtividade (Exigência de GROUP BY + HAVING)
        cursor.execute("""
            SELECT m.nome, COUNT(c.consulta_id) AS total_consultas
            FROM medico m
            JOIN consulta c ON m.medico_id = c.medico_id
            GROUP BY m.medico_id, m.nome
            HAVING COUNT(c.consulta_id) > 0
            ORDER BY total_consultas DESC;
        """)
        sobrecarregados = cursor.fetchall()
        
    except Exception as e:
        return f"Erro ao gerar relatórios: {e}"
    finally:
        cursor.close()
        conexao.close()

    erro = request.args.get('erro')

    return render_template('relatorios.html', 
                           dados_master=dados_master, 
                           sobrecarregados=sobrecarregados,
                           erro=erro)

if __name__ == '__main__':
    app.run(debug=True)