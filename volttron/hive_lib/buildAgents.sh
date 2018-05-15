#!/bin/bash

#
#__author__ = "Teerapong Ponmat"
#__credits__ = ""
#__version__ = "5.0"
#__maintainer__ = "HiVE Team"
#__email__ = "peahive@gmail.com"
#__website__ = "www.peahive.github.io"
#__created__ = "2018-04-4 12:04:50"
#__lastUpdated__ = "2018-04-4 11:23:33"

cd ~/workspace/hive_os/volttron/
. env/bin/activate
volttron -vv 2>&1 | tee ~/workspace/hive_os/volttron/log/volttron.log &

sudo chmod 777 -R /.volttron/agents/
sudo rm -rf ~/.volttron/agents/*
cd ~/workspace/hive_os/


#Lighting Agent

volttron-pkg package Agents/LightingAgent
# Set the agent's configuration file
volttron-pkg configure ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/LightingAgent/02ORV0017886.config.json

# Install the agent (volttron must be running):
volttron-ctl install ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl --tag lighting


#Fibaro Agent

volttron-pkg package Agents/FibaroAgent
volttron-pkg configure ~/.volttron/packaged/fibaroagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/FibaroAgent/20FIB1234568.config.json

volttron-ctl install ~/.volttron/packaged/fibaroagent-0.1-py2-none-any.whl --tag fibaro

#Netatmo Agent

volttron-pkg package Agents/NetatmoAgent

volttron-pkg configure ~/.volttron/packaged/netatmoagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/NetatmoAgent/12NET1234510.config.json


volttron-ctl install ~/.volttron/packaged/netatmoagent-0.1-py2-none-any.whl --tag netatmo

#Weather Agent

volttron-pkg package Agents/WeatherAgent

volttron-pkg configure ~/.volttron/packaged/weatheragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/WeatherAgent/1WE221445K1200138.config.json


volttron-ctl install ~/.volttron/packaged/weatheragent-0.1-py2-none-any.whl --tag weather


#Powermeter Agent

volttron-pkg package Agents/PowerMeterAgent

volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/PowerMeterAgent/05CRE0061217.config.json


volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter

#Yale Agent

volttron-pkg package Agents/YaleAgent

volttron-pkg configure ~/.volttron/packaged/yaleagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/YaleAgent/09YAL1234567.config.json


volttron-ctl install ~/.volttron/packaged/yaleagent-0.1-py2-none-any.whl --tag yale

#OpenClose Agent

volttron-pkg package Agents/OpenCloseAgent

volttron-pkg configure ~/.volttron/packaged/opencloseagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/OpenCloseAgent/18ORV0832132.config.json


volttron-ctl install ~/.volttron/packaged/opencloseagent-0.1-py2-none-any.whl --tag openclose


#Curtain Agent

volttron-pkg package Agents/curtainAgent

volttron-pkg configure ~/.volttron/packaged/opencloseagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/curtainAgent/08SOM221445K.config.json

volttron-ctl install ~/.volttron/packaged/opencloseagent-0.1-py2-none-any.whl --tag curtain


## RUN Lighting Agent
#volttron-pkg package ~/workspace/bemoss_os/Agents/MultiBuilding/
#volttron-pkg configure /tmp/volttron_wheels/multibuildingagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/MultiBuilding/multibuildingagent.launch.json
#volttron-ctl install multibuildingagent=/tmp/volttron_wheels/multibuildingagent-0.1-py2-none-any.whl
#
## Run network agent
#volttron-pkg package ~/workspace/bemoss_os/Agents/NetworkAgent/
#volttron-pkg configure /tmp/volttron_wheels/networkagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/NetworkAgent/networkagent.launch.json
#volttron-ctl install networkagent=/tmp/volttron_wheels/networkagent-0.1-py2-none-any.whl


sudo chmod 777 -R ~/workspace
echo "HiVE OS installation complete!"
