#!/bin/sh
#Author: BEMOSS Team

#Download the package lists from the repositories and update them
sudo apt-get update
#Download and install the dependencies of the postgresql database
sudo apt-get install postgresql postgresql-contrib python-yaml --assume-yes
#Create the bemossdb database
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin';"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS bemossdb;"
sudo -u postgres createdb hiveosdb -O admin
sudo -u postgres psql -d hiveosdb -c "create extension hstore;"
#Go to the bemoss_web_ui and run the syncdb command for the database tables (ref: model.py)
#cd ~/workspace/bemoss_os
#sudo python ~/workspace/bemoss_web_ui/manage.py syncdb
#sudo python ~/workspace/bemoss_web_ui/run/defaultDB.py
