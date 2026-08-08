-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  mood TEXT NOT NULL DEFAULT '😐',
  FOREIGN KEY (author_id) REFERENCES user (id)
);

-- Mood Ring migration for EXISTING databases (init-db drops all data!):
--   ALTER TABLE post ADD COLUMN mood TEXT NOT NULL DEFAULT '😐';
