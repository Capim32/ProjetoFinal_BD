DROP SCHEMA IF EXISTS public CASCADE;

CREATE SCHEMA public AUTHORIZATION pg_database_owner;

-- public.especialidade definição

-- Drop table

-- DROP TABLE especialidade;

CREATE TABLE especialidade (
espec_id int4 NOT NULL,
nome varchar(100) NOT NULL,
CONSTRAINT especialidade_pkey PRIMARY KEY (espec_id)
);

-- public.hospital definição

-- Drop table

-- DROP TABLE hospital;

CREATE TABLE hospital (
hospital_id int4 NOT NULL,
cnpj varchar(18) NOT NULL,
nome varchar(100) NOT NULL,
endereco varchar(200) NULL,
telefone varchar(20) NULL,
CONSTRAINT hospital_cnpj_key UNIQUE (cnpj),
CONSTRAINT hospital_pkey PRIMARY KEY (hospital_id)
);

-- public.paciente definição

-- Drop table

-- DROP TABLE paciente;

CREATE TABLE paciente (
paciente_id int4 NOT NULL,
cpf varchar(14) NOT NULL,
nome varchar(100) NOT NULL,
telefone varchar(20) NULL,
CONSTRAINT paciente_cpf_key UNIQUE (cpf),
CONSTRAINT paciente_pkey PRIMARY KEY (paciente_id)
);

-- public.conveniado definição

-- Drop table

-- DROP TABLE conveniado;

CREATE TABLE conveniado (
paciente_id int4 NOT NULL,
nome_convenio varchar(100) NOT NULL,
num_carteira varchar(50) NOT NULL,
CONSTRAINT conveniado_pkey PRIMARY KEY (paciente_id),
CONSTRAINT conveniado_paciente_id_fkey FOREIGN KEY (paciente_id) REFERENCES paciente(paciente_id)
);

-- public.dependente definição

-- Drop table

-- DROP TABLE dependente;

CREATE TABLE dependente (
nome_dependente varchar(100) NOT NULL,
paciente_id int4 NOT NULL,
data_nascimento date NULL,
telefone varchar(20) NULL,
CONSTRAINT dependente_pkey PRIMARY KEY (nome_dependente, paciente_id),
CONSTRAINT dependente_paciente_id_fkey FOREIGN KEY (paciente_id) REFERENCES paciente(paciente_id)
);

-- public.medico definição

-- Drop table

-- DROP TABLE medico;

CREATE TABLE medico (
medico_id int4 NOT NULL,
crm varchar(20) NOT NULL,
nome varchar(100) NULL,
espec_id int4 NULL,
hospital_id int4 NULL,
CONSTRAINT medico_crm_key UNIQUE (crm),
CONSTRAINT medico_pkey PRIMARY KEY (medico_id),
CONSTRAINT medico_espec_id_fkey FOREIGN KEY (espec_id) REFERENCES especialidade(espec_id),
CONSTRAINT medico_hospital_id_fkey FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
);

-- public.particular definição

-- Drop table

-- DROP TABLE particular;

CREATE TABLE particular (
paciente_id int4 NOT NULL,
limite_credito numeric(10, 2) DEFAULT 0.00 NULL,
CONSTRAINT particular_limite_credito_chk CHECK (limite_credito >= 0),
CONSTRAINT particular_pkey PRIMARY KEY (paciente_id),
CONSTRAINT particular_paciente_id_fkey FOREIGN KEY (paciente_id) REFERENCES paciente(paciente_id)
);

-- public.atende definição

-- Drop table

-- DROP TABLE atende;

CREATE TABLE atende (
medico_id int4 NOT NULL,
hospital_id int4 NOT NULL,
CONSTRAINT atende_pkey PRIMARY KEY (medico_id, hospital_id),
CONSTRAINT atende_hospital_id_fkey FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id),
CONSTRAINT atende_medico_id_fkey FOREIGN KEY (medico_id) REFERENCES medico(medico_id)
);

-- public.consulta definição

-- Drop table

-- DROP TABLE consulta;

CREATE TABLE consulta (
consulta_id int4 NOT NULL,
medico_id int4 NULL,
paciente_id int4 NULL,
data_hora timestamp NULL,
sala varchar(20) NULL,
status varchar(30) DEFAULT 'Agendada' NULL,
CONSTRAINT consulta_status_chk CHECK (status IN ('Agendada', 'Realizada', 'Cancelada')),
CONSTRAINT consulta_pkey PRIMARY KEY (consulta_id),
CONSTRAINT consulta_medico_id_fkey FOREIGN KEY (medico_id) REFERENCES medico(medico_id),
CONSTRAINT consulta_paciente_id_fkey FOREIGN KEY (paciente_id) REFERENCES paciente(paciente_id)
);

-- public.pagamento definição

-- Drop table

-- DROP TABLE pagamento;

CREATE TABLE pagamento (
pgto_id int4 NOT NULL,
consulta_id int4 NOT NULL,
valor numeric(10, 2) NULL,
metodo varchar(50) NULL,
-- CONSTRAINT pagamento_valor_chk CHECK (valor > 0), redundante com o check de 03_objects
CONSTRAINT pagamento_consulta_id_key UNIQUE (consulta_id),
CONSTRAINT pagamento_pkey PRIMARY KEY (pgto_id),
CONSTRAINT pagamento_consulta_id_fkey FOREIGN KEY (consulta_id) REFERENCES consulta(consulta_id)
);

-- public.prescricao definição

-- Drop table

-- DROP TABLE prescricao;

CREATE TABLE prescricao (
presc_id int4 NOT NULL,
consulta_id int4 NOT NULL,
medicamento varchar(150) NOT NULL,
dosagem varchar(100) NULL,
CONSTRAINT prescricao_consulta_id_key UNIQUE (consulta_id),
CONSTRAINT prescricao_pkey PRIMARY KEY (presc_id),
CONSTRAINT prescricao_consulta_id_fkey FOREIGN KEY (consulta_id) REFERENCES consulta(consulta_id)
);
