-- Create the rustici user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'rustici') THEN

      CREATE ROLE rustici LOGIN PASSWORD 'rustici_password';
   END IF;
END
$do$;

-- Create the rustici_engine database if it doesn't exist
CREATE DATABASE rustici_engine
    WITH 
    OWNER = rustici
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Grant all privileges on the database to the rustici user
GRANT ALL PRIVILEGES ON DATABASE rustici_engine TO rustici;

-- Connect to the rustici_engine database
\c rustici_engine

-- Grant all privileges on all tables in the public schema to the rustici user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rustici;

-- Grant all privileges on all sequences in the public schema to the rustici user
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rustici;

-- Grant all privileges on the public schema to the rustici user
GRANT ALL PRIVILEGES ON SCHEMA public TO rustici;
