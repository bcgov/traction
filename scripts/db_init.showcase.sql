CREATE DATABASE showcase;
CREATE USER showcaseadminuser PASSWORD 'showcaseadminPass';
CREATE USER showcaseuser PASSWORD 'showcasePass';
ALTER DATABASE showcase OWNER TO showcaseadminuser;
\connect showcase
CREATE EXTENSION IF NOT EXISTS pgcrypto;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO showcaseadminuser;
GRANT USAGE ON SCHEMA public TO showcaseuser;
GRANT ALL ON SCHEMA public TO showcaseadminuser;
ALTER DEFAULT PRIVILEGES FOR USER showcaseadminuser IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO showcaseuser;
ALTER DEFAULT PRIVILEGES FOR USER showcaseadminuser IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO showcaseuser;
ALTER DEFAULT PRIVILEGES FOR USER showcaseadminuser IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO showcaseuser;

