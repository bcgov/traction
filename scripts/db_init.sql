CREATE DATABASE traction;
CREATE USER tractionadminuser PASSWORD 'tractionadminPass';
CREATE USER tractionuser PASSWORD 'tractionPass';
ALTER DATABASE traction OWNER TO tractionadminuser;
\connect traction
CREATE EXTENSION IF NOT EXISTS pgcrypto;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO tractionadminuser;
GRANT USAGE ON SCHEMA public TO tractionuser;
GRANT ALL ON SCHEMA public TO tractionadminuser;
ALTER DEFAULT PRIVILEGES FOR USER tractionadminuser IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO tractionuser;

