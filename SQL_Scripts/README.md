# README - Sistema Hospitalar

---

## 1. Nome do sistema

**Sistema Hospitalar**

---

## 2. Integrantes da equipe

* Victor Hugo Silva Dos Santos
* Eduardo Perotti Riberiro
* Adrielli da Silva Barbosa
* João Felipe Marques Sena

---

## 3. Ambiente PostgreSQL utilizado

* PostgreSQL 
* Sistema operacional: Windows / Linux 
* Ferramenta de execução: pgAdmin 4

---

## 4. Ferramenta utilizada para execução dos scripts

* pgAdmin 4
* Query Tool do PostgreSQL

---

## 5. Ordem de execução dos scripts

1. `01_create.sql` → Criação das estruturas do banco
2. `02_insert.sql` → Inserção de dados
3. `03_objects.sql` → Criação de VIEW, índice e gatilho
4. `04_tests.sql` → Execução dos testes SQL

---

## 6. Justificativa da VIEW criada

A VIEW `vw_consultas_detalhadas` foi criada para facilitar a visualização consolidada das consultas, permitindo acessar em uma única consulta:

* dados da consulta
* nome do paciente
* nome do médico
* especialidade médica

Isso evita joins repetitivos e melhora a legibilidade das consultas analíticas.

---

## 7. Justificativa do índice criado

O índice `idx_consulta_data_hora` foi criado sobre a coluna `data_hora` da tabela `consulta` com o objetivo de:

* otimizar consultas filtradas por data
* melhorar desempenho em relatórios e buscas por período
* reduzir tempo de resposta em consultas com grande volume de registros

---

## 8. Descrição do gatilho implementado

O gatilho `trg_validar_pagamento` foi implementado para garantir integridade dos dados financeiros.

### Funcionamento:

* Executa a função `fn_validar_pagamento()`
* É acionado antes de INSERT ou UPDATE na tabela `pagamento`
* Impede valores menores ou iguais a zero

### Regra de negócio:

Todo pagamento deve possuir valor positivo, garantindo consistência financeira no sistema.

---

## 9. Instruções para recriar o banco do zero

### Passo 1

Executar o script:

```sql
01_create.sql
```

### Passo 2

Executar:

```sql
02_insert.sql
```

### Passo 3

Executar:

```sql
03_objects.sql
```

### Passo 4

Executar:

```sql
04_tests.sql
```

---

## 10. Observações finais

O sistema foi desenvolvido com base em um modelo relacional hospitalar, contemplando:

* controle de pacientes
* gerenciamento de médicos e especialidades
* agendamento de consultas
* controle de pagamentos e prescrições
* integridade referencial entre entidades
