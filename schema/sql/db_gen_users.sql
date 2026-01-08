USE RedSkyApp;

CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'Pencil1!';
GRANT ALL PRIVILEGES ON RedSkyApp.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
