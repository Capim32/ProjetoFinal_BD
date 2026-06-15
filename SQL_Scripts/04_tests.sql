-- ====================================
-- JOIN
-- ====================================

SELECT
p.nome AS paciente,
m.nome AS medico,
c.data_hora
FROM consulta c
INNER JOIN paciente p
ON c.paciente_id = p.paciente_id
INNER JOIN medico m
ON c.medico_id = m.medico_id;

-- ====================================
-- GROUP BY + AGREGAÇÃO
-- ====================================

SELECT
medico_id,
COUNT(*) AS total_consultas
FROM consulta
GROUP BY medico_id;

-- ====================================
-- HAVING
-- ====================================

SELECT
medico_id,
COUNT(*) AS total_consultas
FROM consulta
GROUP BY medico_id
HAVING COUNT(*) > 1;

-- ====================================
-- SUBCONSULTA
-- ====================================

SELECT *
FROM medico
WHERE medico_id IN (
SELECT medico_id
FROM consulta
GROUP BY medico_id
HAVING COUNT(*) > 1
);

-- ====================================
-- VIEW
-- ====================================

SELECT *
FROM vw_consultas_detalhadas;

-- ====================================
-- CONSULTA UTILIZANDO ÍNDICE
-- ====================================

SELECT *
FROM consulta
WHERE data_hora >= '2025-06-01'
AND data_hora < '2025-07-01';

-- ====================================
-- TESTE DE RESTRIÇÃO CHECK
-- ====================================

INSERT INTO consulta
VALUES
(100,1,1,'2025-07-01 09:00','101','Pendente');

-- Deve gerar erro.

-- ====================================
-- TESTE DE GATILHO
-- ====================================

INSERT INTO pagamento
VALUES
(100,1,-50.00,'Pix');

-- Deve gerar erro.

-- ====================================
-- TRANSAÇÃO
-- ====================================

BEGIN;

INSERT INTO consulta
VALUES
(101,1,1,'2025-07-10 08:00','101','Agendada');

ROLLBACK;

BEGIN;

INSERT INTO consulta
VALUES
(102,1,1,'2025-07-10 09:00','101','Agendada');

COMMIT;
