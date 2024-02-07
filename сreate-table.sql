-- Создание базы данных
CREATE DATABASE IF NOT EXISTS my_database;

-- Подключение к базе данных
\c my_database;

-- Создание таблицы user_balance
CREATE TABLE user_balance (
    user_id INT,
    amount FLOAT
);