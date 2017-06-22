CREATE DATABASE etrace OWNER postgres;
GRANT ALL PRIVILEGES ON DATABASE etrace to postgres;

\c etrace
CREATE TABLE records(
    id SERIAL NOT NULL,
    record_time timestamp default now(),
    node VARCHAR(30) NOT NULL,

  CONSTRAINT PK_records_id PRIMARY KEY (id)
);

CREATE TABLE nearby(
    id SERIAL NOT NULL,
    record_id int not null,
    mac VARCHAR(30) NOT NULL,
    rssi int,

  CONSTRAINT PK_nearby_id PRIMARY KEY (id),
  CONSTRAINT FK_record_id FOREIGN KEY (record_id) REFERENCES records(id)
);


CREATE INDEX nearby_record_id_index ON nearby(record_id);
CLUSTER nearby_record_id_index on nearby;--¾Û¼¯Ë÷Òý

CREATE INDEX nearby_rssi_index ON nearby(rssi);