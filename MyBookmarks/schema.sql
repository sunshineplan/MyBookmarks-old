-- Initialize the database.

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL DEFAULT '123456'
);

CREATE TABLE category (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE bookmark (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  bookmark TEXT NOT NULL,
  url TEXT NOT NULL,
  seq INTEGER DEFAULT 0,
  created TIMESTAMP DEFAULT (datetime('now', 'localtime')),
  user_id INTEGER NOT NULL,
  category_id INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TRIGGER add_seq AFTER INSERT ON bookmark
BEGIN
    UPDATE bookmark SET seq = (SELECT MAX(seq)+1 FROM bookmark WHERE user_id = new.user_id)
    WHERE user_id = new.user_id AND url = new.url;
END;

CREATE TRIGGER reorder AFTER DELETE ON bookmark
BEGIN
    UPDATE bookmark SET seq = seq-1
    WHERE user_id = old.user_id AND seq > old.seq;
END;

INSERT INTO user (id, username)
  VALUES (0, 'guest');

INSERT INTO bookmark (user_id, bookmark, url)
  VALUES (0, 'Google', 'https://www.google.com');
