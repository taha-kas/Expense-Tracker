CREATE DATABASE expense_manager;
USE expense_manager;

CREATE TABLE `User` (
  `user_id` int PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(50) UNIQUE NOT NULL,
  `email` varchar(100) UNIQUE NOT NULL,
  `psswd_hash` varchar(255) NOT NULL,
  `bday` date,
  `created_at` timestamp DEFAULT now(),
  `is_active` boolean DEFAULT true
);

CREATE TABLE `Category` (
  `category_id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `category_name` varchar(50) NOT NULL,
  `category_type` ENUM('income', 'spending') NOT NULL DEFAULT 'spending',
  `budget` decimal(10,2) NULL,
  `is_active` boolean DEFAULT true,
  `created_at` timestamp DEFAULT now()
);

CREATE TABLE `Transaction` (
  `transaction_id` int PRIMARY KEY AUTO_INCREMENT,
  `category_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `type` ENUM('Deposit', 'Withdrawal') NOT NULL,
  `transaction_date` date NOT NULL,
  `description` varchar(255),
  `created_at` timestamp DEFAULT now()
);

CREATE UNIQUE INDEX `Category_index_0` ON `Category` (`user_id`, `category_name`);

ALTER TABLE `Category` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`) ON DELETE CASCADE;
ALTER TABLE `Transaction` ADD FOREIGN KEY (`category_id`) REFERENCES `Category` (`category_id`) ON DELETE CASCADE;