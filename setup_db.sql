-- Setup script for DevOps Knowledge Base
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'devops_user') THEN
      CREATE USER devops_user WITH PASSWORD 'devops_pass';
   END IF;
END
$$;

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'devops_kb') THEN
      CREATE DATABASE devops_kb OWNER devops_user;
   END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE devops_kb TO devops_user;
