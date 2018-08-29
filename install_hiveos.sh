#!/bin/sh
#Author: PEA HiVE Team

#Download the package lists from the repositories and update them
#sudo apt-get update
#
#
###install IoT hub
cd ~/workspace/hive_os/volttron
python bootstrap.py

cd ~/workspace/hive_os/volttron/hive_lib
sudo git clone --recursive https://github.com/Azure/azure-iot-sdk-python.git
#install cmake for IoT hub
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:george-edison55/cmake-3.x
sudo apt-get update
sudo apt-get install cmake
#install gcc IoT hub
sudo apt-get install gcc-4.9
cd ~/workspace/hive_os/volttron/hive_lib/azure-iot-sdk-python/build_all/linux
sudo ./setup.sh
sudo ./build.sh
cd ~/workspace/hive_os/volttron/hive_lib/
sudo chmod 777 -R azure-iot-sdk-python/
cd ~/workspace/hive_os/volttron/hive_lib/azure-iot-sdk-python/device/samples
sudo rm -rf iothub_client_sample.py
sudo cp ~/workspace/hive_os/volttron/DeviceAPI/classAPI/iothub_client_sample.py ~/workspace/hive_os/volttron/hive_lib/azure-iot-sdk-python/device/samples
sudo cp ~/workspace/hive_os/volttron/DeviceAPI/__init__.py ~/workspace/hive_os/volttron/hive_lib/
sudo cp ~/workspace/hive_os/volttron/DeviceAPI/__init__.py ~/workspace/hive_os/volttron/hive_lib/azure-iot-sdk-python/
sudo cp ~/workspace/hive_os/volttron/DeviceAPI/__init__.py ~/workspace/hive_os/volttron/hive_lib/azure-iot-sdk-python/device/
sudo cp ~/workspace/hive_os/volttron/DeviceAPI/__init__.py ~/workspace/hive_os/volttron/hive_lib/azure-iot-sdk-python/device/samples
##Finish install IoT hub


cd ~/workspace/hive_os/volttron
. env/bin/activate
#install fire base
pip install pyrebase

#install service bus
pip install azure.servicebus


#install postgreSQL
#Download the package lists from the repositories and update them
sudo apt-get update
sudo apt install python-pip
pip install --upgrade pip
pip install psycopg2

#Download and install the dependencies of the postgresql database
sudo apt-get install postgresql postgresql-contrib python-yaml --assume-yes
#Create the bemossdb database
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin';"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS hiveosdb"
sudo -u postgres createdb hiveosdb -O admin
sudo -u postgres psql -d hiveosdb -c "create extension hstore;"

pip install psycopg2-binary
cd ~/workspace/hive_os/volttron/
python platform_initiator.py



