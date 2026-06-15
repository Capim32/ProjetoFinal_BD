-- VIEW

CREATE OR REPLACE VIEW vw_consultas_detalhadas AS
SELECT
c.consulta_id,
c.data_hora,
c.status,
p.nome AS paciente,
m.nome AS medico,
e.nome AS especialidade
FROM consulta c
INNER JOIN paciente p
ON c.paciente_id = p.paciente_id
INNER JOIN medico m
ON c.medico_id = m.medico_id
INNER JOIN especialidade e
ON m.espec_id = e.espec_id;

-- ÍNDICE

CREATE INDEX idx_consulta_data_hora
ON consulta(data_hora);

-- FUNÇÃO DO GATILHO

CREATE OR REPLACE FUNCTION fn_validar_pagamento()
RETURNS TRIGGER
AS $$
BEGIN


IF NEW.valor <= 0 THEN
	RAISE EXCEPTION
	'Valor do pagamento deve ser maior que zero.';
END IF;

RETURN NEW;

END;
$$ LANGUAGE plpgsql;

-- GATILHO

CREATE TRIGGER trg_validar_pagamento
BEFORE INSERT OR UPDATE
ON pagamento
FOR EACH ROW
EXECUTE FUNCTION fn_validar_pagamento();
