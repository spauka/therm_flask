DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS fridges_supplementary;
DROP TABLE IF EXISTS fridges;

CREATE TABLE fridges (
        id INTEGER GENERATED ALWAYS AS IDENTITY,
        name VARCHAR(255) NOT NULL,
        fridge_table_name VARCHAR(255) NOT NULL,
        label VARCHAR(255) NOT NULL,
        comment TEXT NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (name),
        UNIQUE (fridge_table_name)
);
INSERT INTO fridges
        (name, label, fridge_table_name, comment)
        SELECT name, name, name, comment FROM "Fridges"
        ORDER BY id ASC;


CREATE TABLE fridges_supplementary (
        id INTEGER GENERATED ALWAYS AS IDENTITY,
        fridge_id INTEGER NOT NULL REFERENCES fridges(id),
        name VARCHAR(255) NOT NULL,
        supp_table_name VARCHAR(1024) NOT NULL,
        label VARCHAR(255) NOT NULL,
        comment TEXT NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (supp_table_name)
);
INSERT INTO fridges_supplementary
        (fridge_id, name, supp_table_name, label, comment)
        SELECT nf.id, fs.name, fs.table_name, fs.label, fs.comment
                FROM "Fridges_Supplementary" as fs
                JOIN "Fridges" f ON fs.fridge_id = f.id
                JOIN fridges as nf ON f.name = nf.label
                ORDER BY nf.id ASC, fs.id ASC;
UPDATE fridges_supplementary SET label='Cryomech Compressor' WHERE label='Comp Suppl';
UPDATE fridges_supplementary SET comment='Cryomech Compressor' WHERE comment='Comp Suppl';
UPDATE fridges_supplementary SET comment='Maxi Gauge' WHERE comment='Maxci Gauge';

CREATE TABLE sensors (
        id INTEGER GENERATED ALWAYS AS IDENTITY,
        fridge_id INTEGER NOT NULL REFERENCES fridges(id),
        column_name VARCHAR(1024) NOT NULL,
        display_name VARCHAR(1024) NOT NULL,
        view_order INTEGER NOT NULL DEFAULT 1,
        visible INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (id)
);
INSERT INTO sensors
        (fridge_id, column_name, display_name, view_order, visible)
        SELECT nf.id, s.column_name, s.name, s.view_order, s.visible
        FROM "Sensors" as s
        JOIN "Fridges" f ON s.fridge_id = f.id
        JOIN fridges as nf ON f.name = nf.label
        ORDER BY nf.id, s.id ASC;

CREATE TABLE sensors_supplementary (
        id INTEGER GENERATED ALWAYS AS IDENTITY,
        fridge_supp_id INTEGER NOT NULL REFERENCES fridges_supplementary(id),
        column_name VARCHAR(1024) NOT NULL,
        display_name VARCHAR(1024) NOT NULL,
        view_order INTEGER NOT NULL DEFAULT 1,
        visible INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (id)
);
INSERT INTO sensors_supplementary
        (fridge_supp_id, column_name, display_name, view_order, visible)
        SELECT nfs.id, s.column_name, s.name, s.view_order, s.visible
        FROM "Sensors_Supplementary" as s
        JOIN "Fridges_Supplementary" fs ON s.fridge_suppl_id = fs.id
        JOIN fridges_supplementary as nfs ON fs.table_name = nfs.supp_table_name
        ORDER BY nfs.id ASC, s.id ASC;
