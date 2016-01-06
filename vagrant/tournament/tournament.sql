-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Checks if this database has been previously initialised and is so, deleted
-- it and create a new one
drop database if exists tournament;

-- Initial database is created
create database tournament;

-- When the user imports the sql file the file will automatically connect
-- to the databsae with this command
\c tournament;

-- Table is craeted to hold all the players data
create table players (
  player_id serial primary key,
  player_name text not null,
  player_wins int not null,
  player_matches int not null
);

create table matches (
  
);
