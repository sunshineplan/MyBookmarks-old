-- Drop any existing data.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS bookmark;
DROP TRIGGER IF EXISTS add_seq;
DROP TRIGGER IF EXISTS reorder;