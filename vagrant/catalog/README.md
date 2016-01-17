# Item Catalog

## About

This application is a model of an item catalog and demonstrates my abilities to
apply CRUD operations on a web application using python with a sqlite database

## How to run

1. While in the vagrant folder type "vagrant up" to start up the virtual machine
2. Once it's on, type "vagrant ssh" to login
3. Nagivate to the catalog folder with the command "cd /vagrant/catalog"
4. You will need to setup the database before you can use it so start by loading
the database with the command "python database_setup.py" followed by
"python defaultitems.py" to load in some items without account ownership
to play around with
5. Finally you can run "python application.py" and in your browser navigate to
localhost:8000/ to run the hosted website

### How to JSONify

If you the data to be shown as json text, simply navigate to either of the following:
localhost:8000/<category-id>/items/JSON
or
localhost:8000/category/item/<item-id>/JSON
replacing <category-id> or <item-id> with the id of your desired category or id
