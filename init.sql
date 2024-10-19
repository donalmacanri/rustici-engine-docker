DO $$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'rustici') THEN
      CREATE ROLE rustici LOGIN PASSWORD 'rustici_password';
   END IF;
END $$;

CREATE DATABASE rustici_engine
    WITH 
    OWNER = rustici
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

\c rustici_engine

GRANT ALL PRIVILEGES ON DATABASE rustici_engine TO rustici;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rustici;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rustici;
GRANT ALL PRIVILEGES ON SCHEMA public TO rustici;
