#!/bin/sh
#Author: PEA HiVE Team

#Download the package lists from the repositories and update them
#sudo apt-get update
#
#volttron
sudo apt-get update
sudo apt-get install build-essential python-dev openssl libssl-dev libevent-dev git
cd ~/workspace/bems/hive_os/volttron/
python bootstrap.py

###install IoT hub
cd ~/workspace/bems/hive_os/volttron/hive_lib
sudo git clone --recursive https://github.com/Azure/azure-iot-sdk-python.git

#install cmake for IoT hub
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:george-edison55/cmake-3.x
sudo apt-get update
sudo apt-get install cmake

#install gcc IoT hub
sudo apt-get install gcc-4.9
cd ~/workspace/bems/hive_os/volttron/hive_lib/azure-iot-sdk-python/build_all/linux
sudo ./setup.sh
sudo ./build.sh
cd ~/workspace/bems/hive_os/volttron/hive_lib/
sudo chmod 777 -R azure-iot-sdk-python/
cd ~/workspace/bems/hive_os/volttron/hive_lib/azure-iot-sdk-python/device/samples
sudo rm -rf iothub_client_sample.py
sudo cp ~/workspace/bems/hive_os/volttron/DeviceAPI/classAPI/iothub_client_sample.py ~/workspace/bems/hive_os/volttron/hive_lib/azure-iot-sdk-python/device/samples
sudo cp ~/workspace/bems/hive_os/volttron/DeviceAPI/__init__.py ~/workspace/bems/hive_os/volttron/hive_lib/
sudo cp ~/workspace/bems/hive_os/volttron/DeviceAPI/__init__.py ~/workspace/bems/hive_os/volttron/hive_lib/azure-iot-sdk-python/
sudo cp ~/workspace/bems/hive_os/volttron/DeviceAPI/__init__.py ~/workspace/bems/hive_os/volttron/hive_lib/azure-iot-sdk-python/device/
sudo cp ~/workspace/bems/hive_os/volttron/DeviceAPI/__init__.py ~/workspace/bems/hive_os/volttron/hive_lib/azure-iot-sdk-python/device/samples

##Finish install IoT hub
cd ~/workspace/bems/hive_os/volttron
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

pip install psycopg2-binary
cd ~/workspace/bems/hive_os/volttron/
python platform_initiator.py



