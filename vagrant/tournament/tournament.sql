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
  matches int not null
);

-- Table is created to hold match history data
create table matches (
  match_id serial primary key,
  winner int references players(player_id),
  loser int references players(player_id)
);

-- This view finds the current player ranking and returns it as a table
-- with their ids and wins
create view placement_order as
  select row_number() over (order by count(matches.winner) desc) as rownum,
  players.player_id as id,
  count(matches.winner) as wins from players
  left join matches on matches.winner = players.player_id
  group by players.player_id order by wins desc;

-- Finds the even players from the placement
create view even_num as
  select row_number() over (order by wins desc) as rownum_even,
  id from placement_order as placement
  where mod(rownum,2) = 0;

-- Finds the odd players from the placement
create view odd_num as
  select row_number() over (order by wins desc) as rownum_odd,
  id from placement_order as placement
  where mod(rownum,2) = 1;
