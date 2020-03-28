
---------- books table ----------
CREATE TABLE books
(
    isbn VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
   	year INTEGER NOT NULL
);

---------- users table ----------
CREATE TABLE users
(
	id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE,
    password VARCHAR NOT NULL    
);

---------- REVIEWS table ----------
CREATE TABLE reviews
(
	id SERIAL PRIMARY KEY,
    review VARCHAR NOT NULL,
    rating INTEGER NOT NULL,
    book_isbn VARCHAR references books,
    user_id INTEGER references users
    
);

