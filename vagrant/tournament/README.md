# Game Tournament Program

# About
This application serves to correctly pair players together when playing a game
tournament together using the Swiss pairing method.

The app has the ability to deleting matches or players, register new players
and record player wins as well as show player standings in the table.

## How to run
To run this app, navigate to the vagrant folder inside the downloaded file
and run your virtual machine by typing 'vagrant up' and log in with the command
'vagrant ssh'. Next navigate to the tournament folder by typing
'cd /vagrant/tournament', next you will need to load the data from the sql file
by typing psql to enter the sql console and then typing '\i tournament.sql'
which will load the necessary database, tables and views. Once created type \q
to exit the psql console and then running the program tournament_test.py for testing.
