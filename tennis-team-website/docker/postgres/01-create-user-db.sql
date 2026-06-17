-- Step 1: Create user and database
CREATE USER tennis_user WITH PASSWORD 'tennis_password';
CREATE DATABASE tennis_db OWNER tennis_user;
GRANT ALL PRIVILEGES ON DATABASE tennis_db TO tennis_user;
