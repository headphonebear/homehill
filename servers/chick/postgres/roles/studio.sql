-- ╔══════════════════════════════════════════════════════════════════════════╗
-- ║  chick-postgres — role + schema `studio` (mk3's workbench, 2026-11-07)   ║
-- ╚══════════════════════════════════════════════════════════════════════════╝
--
-- WHO: `mk3` (the Claude of the music collection, Linux user mk3/2001 on barn)
-- reaches this DB through an SSH tunnel to chick (see servers/chick/README.md,
-- "mk3 tunnel"). This file is the whole permission model for that access.
--
-- THE MODEL — one schema, one owner:
--   public  → owned by the indexer role `mk3`. `studio` may READ everything,
--             write nothing. The catalog has exactly one writer.
--   studio  → owned by the role `studio`. Its own lists (artist lists,
--             white/black/grey-lists, whatever turns up) live here; it may
--             create, write and drop freely. Joins across both just work.
--
-- WHY a role named `studio` and not `mk3_read`: it doesn't only read, and the
-- name matches mk3's room (~/studio). Bonus: Postgres' default search_path is
-- `"$user", public` — so new tables land in schema `studio` by default, while
-- catalog tables resolve without a prefix.
--
-- WHY no password here: this file is committed. Set it separately:
--   ALTER ROLE studio PASSWORD '...';   (the value lives in mk3's secrets.env)
--
-- Idempotent — safe to re-run:
--   docker exec -i chick-postgres psql -U mk3 -d mk3 -v ON_ERROR_STOP=1 < studio.sql

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'studio') THEN
    CREATE ROLE studio LOGIN;
  END IF;
END
$$;

-- Into the database, and nothing more at DB level (no CREATE SCHEMA rights:
-- one workbench is enough; ask when a second one makes sense).
GRANT CONNECT ON DATABASE mk3 TO studio;

-- The workbench. Owner = studio → full rights on everything it builds there.
CREATE SCHEMA IF NOT EXISTS studio AUTHORIZATION studio;

-- Read the catalog: what exists today …
GRANT USAGE ON SCHEMA public TO studio;
GRANT SELECT ON ALL TABLES    IN SCHEMA public TO studio;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO studio;

-- … and whatever the indexer (role mk3) creates later.
-- WHY: without this, every new catalog table would be invisible to studio
-- until someone remembers to re-grant. FOR ROLE mk3 = applies to objects
-- *mk3* creates; run this file as mk3 (the DB owner) or a superuser.
ALTER DEFAULT PRIVILEGES FOR ROLE mk3 IN SCHEMA public GRANT SELECT ON TABLES    TO studio;
ALTER DEFAULT PRIVILEGES FOR ROLE mk3 IN SCHEMA public GRANT SELECT ON SEQUENCES TO studio;

-- Writing into a specific catalog table, should it ever be wanted, is a
-- deliberate per-table GRANT added here with a WHY — never a default.
