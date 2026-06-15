from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import errors
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Substitua pela sua URL real do Neon (mantenha o ?sslmode=require no final)
URL_DO_BANCO = os.getenv("URL_DO_BANCO")

def conectar_banco():
    return psycopg2.connect(URL_DO_BANCO)

# ----------------------------------------------------
# 1. ROTA DE LISTAGEM (Página Inicial Completa)
# ----------------------------------------------------
@app.route('/')
def tela_inicial():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # 1. Busca de Pacientes (com ou sem filtro de substring)
    termo_busca = request.args.get('busca')
    if termo_busca:
        cursor.execute("SELECT paciente_id, nome, cpf, telefone FROM paciente WHERE nome ILIKE %s ORDER BY paciente_id;", 
                       (f"%{termo_busca}%",))
    else:
        cursor.execute("SELECT paciente_id, nome, cpf, telefone FROM paciente ORDER BY paciente_id;")
    lista_pacientes = cursor.fetchall()
    
    # ====================================================
    # GATILHO DE CORREÇÃO: BUSCA DE DEPENDENTES
    # ====================================================
    cursor.execute("SELECT nome_dependente, paciente_id, data_nascimento, telefone FROM dependente;")
    lista_dependentes = cursor.fetchall()
    
    # 2. Busca de Médicos
    cursor.execute("""
        SELECT m.medico_id, m.nome, m.crm, e.nome 
        FROM medico m
        LEFT JOIN especialidade e ON m.espec_id = e.espec_id
        ORDER BY m.medico_id;
    """)
    lista_medicos = cursor.fetchall()
    
    # 3. Busca de Especialidades
    cursor.execute("SELECT espec_id, nome FROM especialidade ORDER BY nome;")
    lista_especialidades = cursor.fetchall()
    
    erro = request.args.get('erro') 
    
    cursor.close()
    conexao.close()
    
    # GARANTA QUE 'dependentes=lista_dependentes' ESTÁ NA LINHA ABAIXO:
    return render_template('index.html', 
                           pacientes=lista_pacientes, 
                           dependentes=lista_dependentes, 
                           medicos=lista_medicos, 
                           especialidades=lista_especialidades, 
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
        cursor.execute("INSERT INTO paciente (paciente_id, nome, cpf, telefone) VALUES (%s, %s, %s, %s);", 
                       (novo_id, nome_digitado, cpf_formatado, telefone_digitado))
        conexao.commit()
    except errors.UniqueViolation:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Erro de Integridade: Este CPF já está cadastrado no sistema!"))
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('tela_inicial'))

@app.route('/deletar_paciente/<int:id_paciente>')
def deletar_paciente(id_paciente):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM paciente WHERE paciente_id = %s;", (id_paciente,))
        conexao.commit()
    except errors.ForeignKeyViolation:
        # Captura o erro da Chave Estrangeira e avisa o usuário!
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro="Erro de Integridade: Não é possível apagar este paciente pois ele possui vínculos (convênio, dependentes ou consultas agendadas)."))
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro inesperado: {e}"))
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
        # Usa a Chave Primária Composta exata para deletar
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
# ROTA PARA ATUALIZAR STATUS DA CONSULTA (NOVA)
# ====================================================
@app.route('/atualizar_status_consulta', methods=['POST'])
def atualizar_status_consulta():
    consulta_id = request.form['consulta_id']
    novo_status = request.form['status']

    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        # Executa a atualização respeitando a restrição CHECK do banco
        cursor.execute("""
            UPDATE consulta 
            SET status = %s 
            WHERE consulta_id = %s;
        """, (novo_status, consulta_id))
        conexao.commit()
    except Exception as e:
        conexao.rollback()
        return redirect(url_for('relatorios', erro=f"Erro ao atualizar status: {e}"))
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('relatorios'))

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
        # 1. Regra do Gatilho: Valor menor ou igual a zero
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Gatilho do Banco Acionado: {e}"))
        
    except errors.UniqueViolation:
        # 2. Regra UNIQUE: Consulta já tem pagamento associado
        conexao.rollback()
        return redirect(url_for('tela_inicial', erro=f"Erro de Integridade: A Consulta {consulta_id} já foi paga! O sistema bloqueou o pagamento duplicado."))
        
    except errors.ForeignKeyViolation:
        # 3. Regra de Chave Estrangeira: A consulta não existe
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

# ====================================================
# ROTA DE RELATÓRIOS (Corrigida com Ordem Cronológica)
# ====================================================
@app.route('/relatorios')
def relatorios():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT consulta_id, data_hora, status, paciente, medico, especialidade 
        FROM vw_consultas_detalhadas 
        ORDER BY data_hora;
    """)
    view_consultas = cursor.fetchall()
    
    cursor.execute("""
        SELECT m.nome, COUNT(c.consulta_id) AS total_consultas 
        FROM consulta c
        INNER JOIN medico m ON c.medico_id = m.medico_id
        GROUP BY m.nome 
        HAVING COUNT(c.consulta_id) > 1;
    """)
    medicos_sobrecarregados = cursor.fetchall()
    
    # Captura mensagens de erro específicas para a tela de relatórios
    erro = request.args.get('erro') 
    
    cursor.close()
    conexao.close()
    return render_template('relatorios.html', consultas=view_consultas, sobrecarregados=medicos_sobrecarregados, erro=erro)

if __name__ == '__main__':
    app.run(debug=True)