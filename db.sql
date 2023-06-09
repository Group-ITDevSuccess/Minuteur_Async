--
-- Fichier généré par SQLiteStudio v3.4.4 sur ven. juin 9 09:14:17 2023
--
-- Encodage texte utilisé : System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Tableau : Emails
CREATE TABLE IF NOT EXISTS Emails (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT (250));
INSERT INTO Emails (id, email) VALUES (1, 'antsa.raminosoa@agrivet.mg');
INSERT INTO Emails (id, email) VALUES (2, 'clarck.rakotobe@interkem.mg');
INSERT INTO Emails (id, email) VALUES (3, 'fidy.rasoanaivo@savonysalama.com');
INSERT INTO Emails (id, email) VALUES (4, 'heri.raoelina@first-energy.mg');
INSERT INTO Emails (id, email) VALUES (5, 'miguel.a@fly-technologies.com');
INSERT INTO Emails (id, email) VALUES (6, 'miary.razafiharinaivo@idrental.mg');
INSERT INTO Emails (id, email) VALUES (7, 'raphael.rakotonanahary@lacityimmobilier.com');
INSERT INTO Emails (id, email) VALUES (8, 'radomilanto.rafanomezantsoa@bovima.mg');
INSERT INTO Emails (id, email) VALUES (9, 'santatra.rasolonjatovo@mabel.mg');
INSERT INTO Emails (id, email) VALUES (10, 'tantely.rakotondrabary@agrikoba.com');
INSERT INTO Emails (id, email) VALUES (11, 'vololomboahangy.rasolomanana@inviso-group.com');

-- Tableau : EmailSociete
CREATE TABLE IF NOT EXISTS EmailSociete (id_societe INTEGER REFERENCES Societes (id), id_email INTEGER REFERENCES Emails (id));
INSERT INTO EmailSociete (id_societe, id_email) VALUES (1, 11);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (2, 8);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (3, 1);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (4, 1);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (5, 1);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (6, 1);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (7, 5);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (8, 8);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (9, 6);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (10, 5);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (11, 5);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (12, 4);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (13, 7);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (14, 4);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (15, 2);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (16, 9);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (17, 10);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (18, 3);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (19, 8);
INSERT INTO EmailSociete (id_societe, id_email) VALUES (20, 11);

-- Tableau : Societes
CREATE TABLE IF NOT EXISTS Societes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT (250) UNIQUE);
INSERT INTO Societes (id, name) VALUES (1, 'AGRICORP');
INSERT INTO Societes (id, name) VALUES (2, 'AGRIFEED');
INSERT INTO Societes (id, name) VALUES (3, 'AGRIMOTORS');
INSERT INTO Societes (id, name) VALUES (4, 'AGRIVET ANTSIRABE');
INSERT INTO Societes (id, name) VALUES (5, 'AGRIVET FIANARANTSOA');
INSERT INTO Societes (id, name) VALUES (6, 'AGRIVET TAMATAVE');
INSERT INTO Societes (id, name) VALUES (7, 'BLAST');
INSERT INTO Societes (id, name) VALUES (8, 'BOVIMA');
INSERT INTO Societes (id, name) VALUES (9, 'FIRST ENERGY');
INSERT INTO Societes (id, name) VALUES (10, 'FLY LEASE');
INSERT INTO Societes (id, name) VALUES (11, 'FLY TECHNOLOGIES');
INSERT INTO Societes (id, name) VALUES (12, 'ID RENTAL');
INSERT INTO Societes (id, name) VALUES (13, 'IDF2010');
INSERT INTO Societes (id, name) VALUES (14, 'IDMOTORS');
INSERT INTO Societes (id, name) VALUES (15, 'INTERKEM');
INSERT INTO Societes (id, name) VALUES (16, 'MABEL2');
INSERT INTO Societes (id, name) VALUES (17, 'NUTRIFOOD');
INSERT INTO Societes (id, name) VALUES (18, 'SALAMA');
INSERT INTO Societes (id, name) VALUES (19, 'SCIFD');
INSERT INTO Societes (id, name) VALUES (20, 'UNITED MALAGASY');

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
