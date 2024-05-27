DROP TABLE IF EXISTS flowers;

CREATE TABLE flowers
(
    name TEXT NOT NULL PRIMARY KEY,
    picture_name TEXT

);


INSERT INTO flowers (name, picture_name)
VALUES ('Lilly', 'lilly.jpg'),
        ('Orchid', 'orchid.jpg'),
        ('Lotus', 'lotus.jpg'),
        ('Tulip', 'tulip.jpg'),
        ('Iris', 'iris.jpg'),
        ('Rose', 'rose.jpg'),
        ('Narcissus', 'narcissus.jpg'),
        ('Geranium', 'geranium.jpg'),
        ('Daisy',  'daisy.jpg'),
        ('Jasmine', 'jasmine.jpg');


DROP TABLE IF EXISTS floral_shops;

CREATE TABLE floral_shops
(
    floral_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL ,
    address TEXT NOT NULL,
    open_time time NOT NULL,
    close_time time NOT NULL,
    description TEXT DEFAULT '',
    picture_name TEXT NOT NULL,
    user_id TEXT NOT NULL,
    income DECIMAL DEFAULT 0.0,
    CONSTRAINT fk_floral_shops_users FOREIGN KEY (user_id) REFERENCES users(user_id)
    
);

INSERT INTO floral_shops (name, address, open_time, close_time, picture_name,user_id)
VALUES ('Best Flowers', 'Green Street', '9:00', '15:00','floral1.jpg','kvit'),
        ('Molentic', 'Oliver Plunkett Street', '8:30', '16:30','floral2.jpg','kvit'),
        ('Lotus Fantasy','Douglas Street', '13:00', '18:00','floral3.jpg','kvit'),
        ('Radenko', 'Old Blackrock Road', '9:00', '12:00','floral4.jpg','kvit');


DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT NOT NULL PRIMARY KEY,
    password TEXT NOT NULL

    
);

INSERT INTO users (user_id, password)
VALUES ('kvit', 'pbkdf2:sha256:260000$gQoX2DI4fmiHnTXq$6ff5607ff432e3afc019a27fcdccfd3efc6b3e466485c13b809be8b43a931c65');

DROP TABLE IF EXISTS flowers_in_shop;

CREATE TABLE flowers_in_shop
(
    floral_id INTEGER NOT NULL ,
    name TEXT NOT NULL,
    price DECIMAL NOT NULL,
    quantity INTEGER,
    CONSTRAINT fk_flowers_in_shop_floral_shops FOREIGN KEY (floral_id) REFERENCES floral_shops(floral_id),
    CONSTRAINT fk_flowers_in_shop_flowers FOREIGN KEY (name) REFERENCES flowers(name)
);

INSERT INTO flowers_in_shop (floral_id, name, price, quantity)
VALUES  (1, 'Tulip',1.47, 10),
        (1, 'Jasmine',1.78, 6),
        (1, 'Lotus',2.00, 12),
        (2, 'Daisy',0.71, 7),
        (2, 'Narcissus',1.05, 10),
        (2, 'Geranium',1.57, 8),
        (2, 'Rose',1.32, 20),
        (3, 'Jasmine',1.12, 15),
        (3, 'Tulip',1.56, 13),
        (4, 'Orchid',1.66, 9),
        (4, 'Lilly',2.12, 14),
        (4, 'Iris',1.02, 7),
        (4, 'Narcissus',1.15, 10),
        (4, 'Geranium',1.24, 8),
        (4, 'Rose',1.75, 20);



DROP TABLE IF EXISTS bouquets_in_shop;

CREATE TABLE bouquets_in_shop
(
    floral_id INTEGER NOT NULL ,
    name TEXT NOT NULL,
    price DECIMAL NOT NULL,
    flowers TEXT NOT NULL,
    quantity INTEGER,
    picture_name TEXT NOT NULL,
    CONSTRAINT fk_flowers_in_shop_floral_shops FOREIGN KEY (floral_id) REFERENCES floral_shops(floral_id)

);

INSERT INTO bouquets_in_shop (floral_id, name, price, flowers,quantity, picture_name)
VALUES  (2, 'Your desire', 10.2, 'rose, narcissus', 3, 'bouquet1.jpg'),
        (2, 'Summer', 8.5, 'tulip', 5, 'bouquet2.jpg'),
        (2, 'Beauty', 12.0, 'rose, orchid, lily', 2, 'bouquet3.jpg'),
        (3, 'Love', 7.45, 'rose, daisy', 3, 'bouquet4.jpg'),
        (3, 'Street stranger', 8.2, 'rose, narcissus', 7, 'bouquet5.jpg'),
        (1, 'Autumn', 15.0, 'daisy, narcissus, tulip, lily', 4, 'bouquet6.jpg');

SELECT * FROM flowers_in_shop;

SELECT * FROM users;

SELECT * FROM floral_shops;

SELECT * FROM flowers;

SELECT * FROM bouquets_in_shop;



