#!/bin/bash
#Copyright (c) 2016, Virginia Tech
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#disclaimer in the documentation and/or other materials provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#The views and conclusions contained in the software and documentation are those of the authors and should not be
#interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.
#
#This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
#United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
#nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
#express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
#any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
#privately owned rights.
#
#Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
#otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
#Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
#expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.
#
#VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
#under Contract DE-EE0006352
#
#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"

cd ~/workspace/bemoss_os/
. env/bin/activate
volttron -vv 2>&1 | tee ~/workspace/bemoss_os/log/volttron.log &

sudo chmod 777 -R /tmp/volttron_wheels/
sudo rm -rf /tmp/volttron_wheels/*
sudo rm -rf ~/.volttron/agents/*
cd ~/workspace/bemoss_os/

volttron-pkg package ~/workspace/bemoss_os/Agents/ThermostatAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/PlugloadAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/LightingAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/NetworkAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/RTUAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/VAVAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/DeviceDiscoveryAgent

volttron-pkg configure /tmp/volttron_wheels/devicediscoveryagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/DeviceDiscoveryAgent/devicediscoveryagent.launch.json
volttron-ctl install devicediscoveryagent=/tmp/volttron_wheels/devicediscoveryagent-0.1-py2-none-any.whl
volttron-pkg package ~/workspace/bemoss_os/Agents/AppLauncherAgent
volttron-pkg configure /tmp/volttron_wheels/applauncheragent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/AppLauncherAgent/applauncheragent.launch.json
volttron-ctl install applauncheragent=/tmp/volttron_wheels/applauncheragent-0.1-py2-none-any.whl
volttron-pkg package ~/workspace/bemoss_os/Applications/code/Lighting_Scheduler
volttron-pkg package ~/workspace/bemoss_os/Applications/code/Plugload_Scheduler

volttron-pkg package ~/workspace/bemoss_os/Agents/ApprovalHelperAgent/
volttron-pkg configure /tmp/volttron_wheels/approvalhelperagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/ApprovalHelperAgent/approvalhelperagent.launch.json
volttron-ctl install approvalhelperagent=/tmp/volttron_wheels/approvalhelperagent-0.1-py2-none-any.whl

# Run multibuilding agent
volttron-pkg package ~/workspace/bemoss_os/Agents/MultiBuilding/
volttron-pkg configure /tmp/volttron_wheels/multibuildingagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/MultiBuilding/multibuildingagent.launch.json
volttron-ctl install multibuildingagent=/tmp/volttron_wheels/multibuildingagent-0.1-py2-none-any.whl

# Run network agent
volttron-pkg package ~/workspace/bemoss_os/Agents/NetworkAgent/
volttron-pkg configure /tmp/volttron_wheels/networkagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/NetworkAgent/networkagent.launch.json
volttron-ctl install networkagent=/tmp/volttron_wheels/networkagent-0.1-py2-none-any.whl

# Run Powermeter agent
volttron-pkg package ~/workspace/bemoss_os/Agents/PowerMeterAgent/
volttron-pkg configure /tmp/volttron_wheels/powermeteragent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/PowerMeterAgent/powermeteragent.launch.json
volttron-ctl install powermeteragent=/tmp/volttron_wheels/powermeteragent-0.1-py2-none-any.whl

# Run Mode agent
volttron-pkg package ~/workspace/bemoss_os/Agents/ModeAppAgent/
volttron-pkg configure /tmp/volttron_wheels/modeappagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/ModeAppAgent/modeappagent.launch.json
volttron-ctl install modeappagent=/tmp/volttron_wheels/modeappagent-0.1-py2-none-any.whl

# Run DeviceStatusApp agent
volttron-pkg package ~/workspace/bemoss_os/Agents/DeviceStatusAppAgent/
volttron-pkg configure /tmp/volttron_wheels/devicestatusappagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/DeviceStatusAppAgent/devicestatusappagent.launch.json
volttron-ctl install devicestatusappagent=/tmp/volttron_wheels/devicestatusappagent-0.1-py2-none-any.whl

# Run ACAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/ACAgent/
volttron-pkg configure /tmp/volttron_wheels/acagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/ACAgent/1TH221445K1living1.launch.json
volttron-ctl install LivingroomAir1=/tmp/volttron_wheels/acagent-0.1-py2-none-any.whl

volttron-pkg configure /tmp/volttron_wheels/acagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/ACAgent/1TH221445K1living2.launch.json
volttron-ctl install LivingroomAir2=/tmp/volttron_wheels/acagent-0.1-py2-none-any.whl

volttron-pkg configure /tmp/volttron_wheels/acagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/ACAgent/1TH221445K12bedroom.launch.json
volttron-ctl install BedroomAir=/tmp/volttron_wheels/acagent-0.1-py2-none-any.whl

## Run Refridgerator Agent
#volttron-pkg package ~/workspace/bemoss_os/Agents/FridgeAgent/
#volttron-pkg configure /tmp/volttron_wheels/fridgeagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/FridgeAgent/1FR221445K1200111.launch.json
#volttron-ctl install 1FR221445K1200111=/tmp/volttron_wheels/fridgeagent-0.1-py2-none-any.whl

# Run MultisensorAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/MultiSensorAgent/
volttron-pkg configure /tmp/volttron_wheels/multisensoragent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/MultiSensorAgent/1MS221445K1200132.launch.json
volttron-ctl install 1MS221445K1200132=/tmp/volttron_wheels/multisensoragent-0.1-py2-none-any.whl

# Run LGTVAgent
volttron-pkg package ~/workspace/bemoss_os/Agents/LGTVAgent/
volttron-pkg configure /tmp/volttron_wheels/lgtvagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/LGTVAgent/11LG121445K1200137.launch.json
volttron-ctl install 1LG221445K1200137=/tmp/volttron_wheels/lgtvagent-0.1-py2-none-any.whl

# Run Fan
volttron-pkg package ~/workspace/bemoss_os/Agents/FanAgent/
volttron-pkg configure /tmp/volttron_wheels/fanagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/FanAgent/1FN221445K1200138.launch.json
volttron-ctl install 1FN221445K1200138=/tmp/volttron_wheels/fanagent-0.1-py2-none-any.whl

# Run Weather
volttron-pkg package ~/workspace/bemoss_os/Agents/WeatherAgent/
volttron-pkg configure /tmp/volttron_wheels/weatheragent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/WeatherAgent/1WE221445K1200132.launch.json
volttron-ctl install 1WE221445K1200132=/tmp/volttron_wheels/weatheragent-0.1-py2-none-any.whl

# Run Sonos
volttron-pkg package ~/workspace/bemoss_os/Agents/SonosAgent/
volttron-pkg configure /tmp/volttron_wheels/sonosagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/SonosAgent/1SONOS445K1200137.launch.json
volttron-ctl install 1SONOS445K1200137=/tmp/volttron_wheels/sonosagent-0.1-py2-none-any.whl

# Run DemandResponse Agent
volttron-pkg package ~/workspace/bemoss_os/Agents/DemandResponeAgent
volttron-pkg configure /tmp/volttron_wheels/demandresponseagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/DemandResponeAgent/DemandResponeAgent.launch.json
volttron-ctl install DemandResponseAgent=/tmp/volttron_wheels/demandresponseagent-0.1-py2-none-any.whl

## Run NETPIESensor Agent
#volttron-pkg package ~/workspace/bemoss_os/Agents/NETPIESensorgent
#volttron-pkg configure /tmp/volttron_wheels/netpiesensoragent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/NETPIESensorgent/NETPIESensoragent.launch.json
#volttron-ctl install NETPIESensorgent=/tmp/volttron_wheels/netpiesensoragent-0.1-py2-none-any.whl
#
## Run NETPIEButton Agent
#volttron-pkg package ~/workspace/bemoss_os/Agents/NetpieButtonAgent
#volttron-pkg configure /tmp/volttron_wheels/netpiebuttonagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/NetpieButtonAgent/netpiebuttonagent.launch.json
#volttron-ctl install NETPIEButton=/tmp/volttron_wheels/netpiebuttonagent-0.1-py2-none-any.whl

# Run ACApp
volttron-pkg package ~/workspace/bemoss_os/Applications/code/ACApp
volttron-pkg configure /tmp/volttron_wheels/acappagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Applications/code/ACApp/acappagent.launch.json
volttron-ctl install ACAPP=/tmp/volttron_wheels/acappagent-0.1-py2-none-any.whl

## Run Alexa SmartThings Agent
#volttron-pkg package ~/workspace/bemoss_os/Applications/code/AlexaSmartThingsAgent
#volttron-pkg configure /tmp/volttron_wheels/alexasmartthingsagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Applications/code/AlexaSmartThingsAgent/alexasmartthingsagent.launch.json
#volttron-ctl install AlexaSmartThings=/tmp/volttron_wheels/alexasmartthingsagent-0.1-py2-none-any.whl

# Run LightingApp Agent
volttron-pkg package ~/workspace/bemoss_os/Applications/code/LightingApp
volttron-pkg configure /tmp/volttron_wheels/lightingappagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Applications/code/LightingApp/lightingappagent.launch.json
volttron-ctl install LightingApp=/tmp/volttron_wheels/lightingappagent-0.1-py2-none-any.whl

# Run PlugloadApp Agent
volttron-pkg package ~/workspace/bemoss_os/Applications/code/PlugloadAppAgent
volttron-pkg configure /tmp/volttron_wheels/plugloadappagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Applications/code/PlugloadAppAgent/plugloadappagent.launch.json
volttron-ctl install PlugloadApp=/tmp/volttron_wheels/plugloadappagent-0.1-py2-none-any.whl

# Run PEA Welcome Switch Agent
volttron-pkg package ~/workspace/bemoss_os/Agents/PlugloadAgent
volttron-pkg configure /tmp/volttron_wheels/plugloadagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/PlugloadAgent/3WIS221445K1200321.launch.json
volttron-ctl install 3WSP3424348ce97489=/tmp/volttron_wheels/plugloadagent-0.1-py2-none-any.whl

# Run EnergyBillApp Agent
volttron-pkg package ~/workspace/bemoss_os/Applications/code/EnergyBillAppAgent
volttron-pkg configure /tmp/volttron_wheels/energybillappagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Applications/code/EnergyBillAppAgent/energybillappagent.launch.json
volttron-ctl install EnergyBillAppAgent=/tmp/volttron_wheels/energybillappagent-0.1-py2-none-any.whl

# Run PVinverter Agent
volttron-pkg package ~/workspace/bemoss_os/Agents/PVInverterAgent
volttron-pkg configure /tmp/volttron_wheels/pvinverteragent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/PVInverterAgent/1PVGW1445K1200138.launch.json
volttron-ctl install PVInverterAgent=/tmp/volttron_wheels/pvinverteragent-0.1-py2-none-any.whl

# Run DC Agent
volttron-pkg package ~/workspace/bemoss_os/Agents/DCRelayAgent
volttron-pkg configure /tmp/volttron_wheels/dcrelayagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/DCRelayAgent/RelaySRD05VDCSLCIP0035.launch.json
volttron-ctl install DCRelayAgent=/tmp/volttron_wheels/dcrelayagent-0.1-py2-none-any.whl

# Run Listener Agent
volttron-pkg package ~/workspace/bemoss_os/Agents/ListenerAgent
volttron-pkg configure /tmp/volttron_wheels/listeneragent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/ListenerAgent/listeneragent.launch.json
volttron-ctl install ListenerAgent=/tmp/volttron_wheels/listeneragent-0.1-py2-none-any.whl

# Run GridApp agent
volttron-pkg package ~/workspace/bemoss_os/Applications/code/GridAppAgent/
volttron-pkg configure /tmp/volttron_wheels/gridappagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Applications/code/GridAppAgent/gridappagent.launch.json
volttron-ctl install GridAppAgent=/tmp/volttron_wheels/gridappagent-0.1-py2-none-any.whl

# Run EVApp agent
volttron-pkg package ~/workspace/bemoss_os/Applications/code/EVAppAgent/
volttron-pkg configure /tmp/volttron_wheels/evappagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Applications/code/EVAppAgent/evappagent.launch.json
volttron-ctl install evappagent=/tmp/volttron_wheels/evappagent-0.1-py2-none-any.whl

# Run Netatmo agent
volttron-pkg package ~/workspace/bemoss_os/Agents/NetatmoAgent/
volttron-pkg configure /tmp/volttron_wheels/netatmoagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/NetatmoAgent/netatmoagent.launch.json
volttron-ctl install Netatmoagent=/tmp/volttron_wheels/netatmoagent-0.1-py2-none-any.whl

# Run CreativePowerMeter
volttron-pkg package ~/workspace/bemoss_os/Agents/CreativePowerMeterAgent/
volttron-pkg configure /tmp/volttron_wheels/creativepoweragent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/CreativePowerMeterAgent/creativepoweragent.launch.json
volttron-ctl install  CreativePowerAgent=/tmp/volttron_wheels/creativepoweragent-0.1-py2-none-any.whl


# Run Daikin
volttron-pkg package ~/workspace/bemoss_os/Agents/ACDaikinAgent/
volttron-pkg configure /tmp/volttron_wheels/daikinagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/ACDaikinAgent/daikinagent.launch.json
volttron-ctl install Daikinagent=/tmp/volttron_wheels/daikinagent-0.1-py2-none-any.whl

#volttron-pkg package ~/workspace/bemoss_os/Agents/mqttsubscribe/
#volttron-pkg configure /tmp/volttron_wheels/mqttsubagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/mqttsubscribe/mqttsubagent.launch.json
#volttron-ctl install MQTTSub=/tmp/volttron_wheels/mqttsubagent-0.1-py2-none-any.whl


# kitchen light

volttron-pkg package ~/workspace/bemoss_os/Agents/RelaySWAgent/
volttron-pkg configure /tmp/volttron_wheels/relayswagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/RelaySWAgent/1KR221445K1200138.launch.json
volttron-ctl install KitchenLight=/tmp/volttron_wheels/relayswagent-0.1-py2-none-any.whl

# Living light
volttron-pkg package ~/workspace/bemoss_os/Agents/RelaySWAgent/
volttron-pkg configure /tmp/volttron_wheels/relayswagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/RelaySWAgent/1LR221445K1200138.launch.json
volttron-ctl install LivingLight=/tmp/volttron_wheels/relayswagent-0.1-py2-none-any.whl

# Phillip-Hue
volttron-pkg package ~/workspace/bemoss_os/Agents/LightingAgent/
volttron-pkg configure /tmp/volttron_wheels/lightingagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/LightingAgent/2HUE0017881cab4b.launch.json
volttron-ctl install PEASmartHomeHue=/tmp/volttron_wheels/lightingagent-0.1-py2-none-any.whl

# Wemo-PEASmarthome
volttron-pkg package ~/workspace/bemoss_os/Agents/PlugloadAgent/
volttron-pkg configure /tmp/volttron_wheels/plugloadagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/PlugloadAgent/3WIS221445K1200321.launch.json
volttron-ctl install PEASmartHomeWemo=/tmp/volttron_wheels/plugloadagent-0.1-py2-none-any.whl

# Home-SceneApp
volttron-pkg package ~/workspace/bemoss_os/Agents/HomeScenceAgent/
volttron-pkg configure /tmp/volttron_wheels/homescenceagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/HomeScenceAgent/homescenceagent.launch.json
volttron-ctl install HomeSceneApp=/tmp/volttron_wheels/homescenceagent-0.1-py2-none-any.whl


volttron-pkg package ~/workspace/bemoss_os/Agents/LGTVAgent/
volttron-pkg configure /tmp/volttron_wheels/lgtvagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/LGTVAgent/18DOR06.launch.json
volttron-ctl install YaleDoorLock=/tmp/volttron_wheels/lgtvagent-0.1-py2-none-any.whl

volttron-pkg package ~/workspace/bemoss_os/Agents/LGTVAgent/
volttron-pkg configure /tmp/volttron_wheels/lgtvagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/LGTVAgent/3WSP221445K1200328.launch.json
volttron-ctl install somfy=/tmp/volttron_wheels/lgtvagent-0.1-py2-none-any.whl

# Run Openclose
volttron-pkg package ~/workspace/bemoss_os/Agents/OpenCloseAgent/
volttron-pkg configure /tmp/volttron_wheels/opencloseagent-0.1-py2-none-any.whl ~/workspace/bemoss_os/Agents/OpenCloseAgent/openclose221445K1200135.launch.json
volttron-ctl install openclose=/tmp/volttron_wheels/opencloseagent-0.1-py2-none-any.whl

sudo chmod 777 -R /tmp/volttron_wheels/
#Install Apps
#cd ~/workspace/bemoss_os/Applications/code/AppLauncherAgent
#sudo python installapp.py
cd ~/workspace/bemoss_os/Applications/code/Lighting_Scheduler
sudo python installapp.py
cd ~/workspace/bemoss_os/Applications/code/Plugload_Scheduler
sudo python installapp.py
sudo chmod 777 -R ~/workspace
echo "BEMOSS App installation complete!"
