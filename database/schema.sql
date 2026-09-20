CREATE DATABASE IF NOT EXISTS aarambh CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aarambh;

-- SQLAlchemy creates the tables. For an existing database, run:
--   cd backend
--   python migrate.py
-- then:
--   python seed.py
--
-- The migration is idempotent and adds Business/Education fields,
-- partner routing metrics, application timeline fields and data-governance fields.
