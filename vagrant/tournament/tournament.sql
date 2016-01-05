-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

create database tournament;

\c tournament;

create table players (
  player_id serial primary key,
  player_name text not null,
  player_wins int not null,
  player_matches int not null
);

create table matches (
  match_id int primary key,
  player_one int not null,
  player_two int not null,
  winner int not null
);
