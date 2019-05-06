CREATE TABLE `experiments` (
	`Id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`Rule`	TEXT,
	`Protocol`	TEXT,
	`Dataset`	TEXT,
	`Results`	TEXT UNIQUE
);