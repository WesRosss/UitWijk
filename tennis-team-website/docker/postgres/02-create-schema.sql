-- Step 2: Create schema in tennis_db
-- This file will be executed in the context of tennis_db

-- Create extension for UUID if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create roles enum (for RBAC)
CREATE TYPE user_role_enum AS ENUM ('admin', 'coordinator', 'player');

-- Create notification type enum
CREATE TYPE notification_type_enum AS ENUM ('email', 'in_app', 'both');

-- Create notification status enum
CREATE TYPE notification_status_enum AS ENUM ('pending', 'sent', 'failed', 'read');

-- Create availability status enum
CREATE TYPE availability_status_enum AS ENUM ('available', 'unavailable', 'maybe', 'unknown');

-- Create match status enum
CREATE TYPE match_status_enum AS ENUM ('scheduled', 'confirmed', 'cancelled', 'completed', 'postponed');

-- Create match type enum
CREATE TYPE match_type_enum AS ENUM ('home', 'away', 'neutral');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    role user_role_enum NOT NULL DEFAULT 'player',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    coach_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name)
);

-- Players table (extends users with team-specific info)
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_number INTEGER,
    position VARCHAR(50),
    skill_level INTEGER DEFAULT 1 CHECK (skill_level >= 1 AND skill_level <= 10),
    emergency_contact_name VARCHAR(150),
    emergency_contact_phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, team_id)
);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    match_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    location VARCHAR(255) NOT NULL,
    home_team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL,
    away_team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL,
    match_type match_type_enum NOT NULL DEFAULT 'home',
    status match_status_enum NOT NULL DEFAULT 'scheduled',
    opponent_name VARCHAR(100),
    opponent_score INTEGER DEFAULT 0,
    our_score INTEGER DEFAULT 0,
    court_number VARCHAR(20),
    notes TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (match_date >= CURRENT_DATE OR (match_date = CURRENT_DATE AND start_time >= CURRENT_TIME))
);

-- Player availability for matches
CREATE TABLE IF NOT EXISTS player_availability (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    status availability_status_enum NOT NULL DEFAULT 'unknown',
    notes TEXT,
    responded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(player_id, match_id)
);

-- Match assignments (which players are assigned to which matches)
CREATE TABLE IF NOT EXISTS match_assignments (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    position VARCHAR(50),
    is_captain BOOLEAN NOT NULL DEFAULT FALSE,
    is_substitute BOOLEAN NOT NULL DEFAULT FALSE,
    assigned_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(player_id, match_id)
);

-- Responsibilities (transportation, refreshments, etc.)
CREATE TABLE IF NOT EXISTS responsibilities (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    responsibility_type VARCHAR(50) NOT NULL CHECK (responsibility_type IN ('transportation', 'refreshments', 'equipment', 'first_aid', 'photography', 'other')),
    description TEXT,
    assigned_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type notification_type_enum NOT NULL DEFAULT 'in_app',
    status notification_status_enum NOT NULL DEFAULT 'pending',
    related_model VARCHAR(50) NOT NULL CHECK (related_model IN ('match', 'team', 'player', 'availability', 'assignment', 'responsibility', 'user')),
    related_id INTEGER NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Notification preferences
CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('match_created', 'match_updated', 'match_cancelled', 'assignment_created', 'assignment_updated', 'availability_request', 'responsibility_assigned', 'team_announcement')),
    email_notification BOOLEAN NOT NULL DEFAULT TRUE,
    in_app_notification BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, notification_type)
);

-- Notification batch (for hourly bundling)
CREATE TABLE IF NOT EXISTS notification_batches (
    id SERIAL PRIMARY KEY,
    batch_identifier VARCHAR(64) NOT NULL UNIQUE,
    notification_type VARCHAR(50),
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    total_notifications INTEGER NOT NULL DEFAULT 0,
    processed_notifications INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_players_user_id ON players(user_id);
CREATE INDEX idx_players_team_id ON players(team_id);
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_home_team ON matches(home_team_id);
CREATE INDEX idx_matches_away_team ON matches(away_team_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_player_availability_match_id ON player_availability(match_id);
CREATE INDEX idx_player_availability_player_id ON player_availability(player_id);
CREATE INDEX idx_match_assignments_match_id ON match_assignments(match_id);
CREATE INDEX idx_match_assignments_player_id ON match_assignments(player_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_scheduled_for ON notifications(scheduled_for);

-- Create a function to update timestamps
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_users_timestamp BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_teams_timestamp BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_players_timestamp BEFORE UPDATE ON players FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_matches_timestamp BEFORE UPDATE ON matches FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_player_availability_timestamp BEFORE UPDATE ON player_availability FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_match_assignments_timestamp BEFORE UPDATE ON match_assignments FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_responsibilities_timestamp BEFORE UPDATE ON responsibilities FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_notifications_timestamp BEFORE UPDATE ON notifications FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Create a view for match summaries
CREATE VIEW match_summaries AS
SELECT 
    m.id,
    m.match_date,
    m.start_time,
    m.end_time,
    m.location,
    ht.name as home_team_name,
    at.name as away_team_name,
    m.match_type,
    m.status,
    m.opponent_name,
    (SELECT COUNT(*) FROM match_assignments ma WHERE ma.match_id = m.id) as assigned_players,
    (SELECT COUNT(*) FROM player_availability pa WHERE pa.match_id = m.id AND pa.status = 'available') as available_players
FROM matches m
LEFT JOIN teams ht ON m.home_team_id = ht.id
LEFT JOIN teams at ON m.away_team_id = at.id;

-- Create a view for player match status
CREATE VIEW player_match_status AS
SELECT 
    p.id as player_id,
    u.username,
    u.first_name,
    u.last_name,
    t.name as team_name,
    m.id as match_id,
    m.match_date,
    m.start_time,
    pa.status as availability_status,
    ma.position as assigned_position,
    ma.is_captain,
    ma.is_substitute
FROM players p
JOIN users u ON p.user_id = u.id
JOIN teams t ON p.team_id = t.id
LEFT JOIN matches m ON TRUE
LEFT JOIN player_availability pa ON p.id = pa.player_id AND m.id = pa.match_id
LEFT JOIN match_assignments ma ON p.id = ma.player_id AND m.id = ma.match_id;

-- Grant all privileges on all tables to the user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tennis_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tennis_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO tennis_user;
GRANT ALL PRIVILEGES ON ALL VIEWS IN SCHEMA public TO tennis_user;

-- Alter default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tennis_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO tennis_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO tennis_user;
