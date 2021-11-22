CREATE USER tractionuser CREATEDB;
CREATE USER holderuser PASSWORD 'holderPass'; 
CREATE USER verifieruser PASSWORD 'verifierPass';

CREATE DATABASE traction;
\connect traction

CREATE SCHEMA IF NOT EXISTS holder AUTHORIZATION holderuser;
CREATE SCHEMA IF NOT EXISTS verifier AUTHORIZATION verifieruser;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA holder TO holderuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA verifier TO verifieruser;