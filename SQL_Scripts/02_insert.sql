-- ESPECIALIDADES

INSERT INTO especialidade VALUES
(1,'Cardiologia'),
(2,'Pediatria'),
(3,'Ortopedia'),
(4,'Dermatologia');

-- HOSPITAIS

INSERT INTO hospital VALUES
(1,'12.345.678/0001-10','Hospital Central','Rua A, 100','85999990001'),
(2,'23.456.789/0001-20','Hospital São Lucas','Rua B, 200','85999990002');

-- PACIENTES

INSERT INTO paciente VALUES
(1,'111.111.111-11','João Silva','85988880001'),
(2,'222.222.222-22','Maria Souza','85988880002'),
(3,'333.333.333-33','Carlos Lima','85988880003'),
(4,'444.444.444-44','Ana Costa','85988880004'),
(5,'555.555.555-55','Pedro Alves','85988880005');

-- CONVENIADOS

INSERT INTO conveniado VALUES
(1,'Unimed','U001'),
(2,'Hapvida','H002'),
(3,'Unimed','U003');

-- PARTICULARES

INSERT INTO particular VALUES
(4,1000.00),
(5,500.00);

-- DEPENDENTES

INSERT INTO dependente VALUES
('Lucas Silva',1,'2015-03-10','85997770001'),
('Julia Souza',2,'2018-05-15','85997770002');

-- MÉDICOS

INSERT INTO medico VALUES
(1,'CRM1001','Dr. Roberto',1,1),
(2,'CRM1002','Dra. Fernanda',2,1),
(3,'CRM1003','Dr. Marcelo',3,2),
(4,'CRM1004','Dra. Camila',4,2);

-- ATENDE

INSERT INTO atende VALUES
(1,1),
(2,1),
(3,2),
(4,2);

-- CONSULTAS

INSERT INTO consulta VALUES
(1,1,1,'2025-06-01 09:00','101','Realizada'),
(2,1,2,'2025-06-02 10:00','101','Realizada'),
(3,2,3,'2025-06-03 14:00','102','Agendada'),
(4,3,4,'2025-06-04 15:00','201','Realizada'),
(5,3,5,'2025-06-05 16:00','201','Cancelada'),
(6,4,1,'2025-06-06 11:00','202','Realizada'),
(7,1,3,'2025-06-07 08:00','101','Realizada');

-- PAGAMENTOS

INSERT INTO pagamento VALUES
(1,1,250.00,'Pix'),
(2,2,250.00,'Cartão'),
(3,4,300.00,'Dinheiro'),
(4,6,180.00,'Pix'),
(5,7,220.00,'Cartão');

-- PRESCRIÇÕES

INSERT INTO prescricao VALUES
(1,1,'Losartana','50mg'),
(2,2,'AAS','100mg'),
(3,4,'Ibuprofeno','600mg'),
(4,6,'Pomada XYZ','2x ao dia'),
(5,7,'Atorvastatina','20mg');
