#!/bin/bash
#Inwall Agent

volttron-pkg package Agents/02ORV_InwallLightingAgent
# Set the agent's configuration file
volttron-pkg configure ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/02ORV_InwallLightingAgent/02HUE1234569.config.json
volttron-ctl install ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl --tag livingroom
volttron-ctl enable --tag livingroom
volttron-ctl start --tag livingroom

#Fibaro Agent
volttron-pkg package Agents/20FIB_FibaroAgent
volttron-pkg configure ~/.volttron/packaged/fibaroagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/20FIB_FibaroAgent/20FIB87654321.config.json
volttron-ctl install ~/.volttron/packaged/fibaroagent-0.1-py2-none-any.whl --tag fibaro
volttron-ctl enable --tag fibaro
volttron-ctl start --tag fibaro

#Netatmo Agent
volttron-pkg package Agents/12NET_NetatmoAgent
volttron-pkg configure ~/.volttron/packaged/netatmoagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/12NET_NetatmoAgent/12NET123451231.config.json
volttron-ctl install ~/.volttron/packaged/netatmoagent-0.1-py2-none-any.whl --tag netatmo
volttron-ctl enable --tag netatmo
volttron-ctl start --tag netatmo

#Yale Agent
volttron-pkg package Agents/09YAL_YaleAgent
volttron-pkg configure ~/.volttron/packaged/yaleagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/09YAL_YaleAgent/09YAL1234567.config.json
volttron-ctl install ~/.volttron/packaged/yaleagent-0.1-py2-none-any.whl --tag yale
volttron-ctl enable --tag yale
volttron-ctl start --tag yale

#OpenClose Agent
volttron-pkg package Agents/18ORC_OpenCloseAgent
volttron-pkg configure ~/.volttron/packaged/opencloseagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/18ORC_OpenCloseAgent/18OPC23451237.config.json
volttron-ctl install ~/.volttron/packaged/opencloseagent-0.1-py2-none-any.whl --tag openclose
volttron-ctl enable --tag openclose
volttron-ctl start --tag openclose

#Curtain Agent
volttron-pkg package Agents/08SOM111_CurtainAgent
volttron-pkg configure ~/.volttron/packaged/certainagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/08SOM111_CurtainAgent/08SOM123457.config.json
volttron-ctl install ~/.volttron/packaged/certainagent-0.1-py2-none-any.whl --tag curtain
volttron-ctl enable --tag curtain
volttron-ctl start --tag curtain


#Motion Agent
volttron-pkg package Agents/21ORV_MotionAgent
volttron-pkg configure ~/.volttron/packaged/motionagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/21ORV_MotionAgent/21ORV23451231.config.json
volttron-ctl install ~/.volttron/packaged/motionagent-0.1-py2-none-any.whl --tag motion
volttron-ctl enable --tag motion
volttron-ctl start --tag motion

#mqtt
volttron-pkg package Agents/mqttsubAgent
volttron-pkg configure ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/mqttsubAgent/mqttsub.config
volttron-ctl install ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl --tag mqtt
volttron-ctl enable --tag mqtt
volttron-ctl start --tag mqtt


#powermeter1
volttron-pkg package Agents/05CRE_PowerMeterAgent
volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/05CRE_PowerMeterAgent/05CRE0250883398.config.json
volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter1
volttron-ctl enable --tag powermeter1
volttron-ctl start --tag powermeter1

#air
volttron-pkg package Agents/01DAI_ACAgent
volttron-pkg configure ~/.volttron/packaged/acagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/01DAI_ACAgent/01DAI1200101.config.json
volttron-ctl install ~/.volttron/packaged/acagent-0.1-py2-none-any.whl --tag saijo
volttron-ctl enable --tag saijo
volttron-ctl start --tag saijo

volttron-pkg configure ~/.volttron/packaged/acagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/01DAI_ACAgent/01DAI1200100.config.json
volttron-ctl install ~/.volttron/packaged/acagent-0.1-py2-none-any.whl --tag daikin
volttron-ctl enable --tag daikin
volttron-ctl start --tag daikin

#weatherwunderground
volttron-pkg package Agents/50WeatherAgent
volttron-pkg configure ~/.volttron/packaged/weatheragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/50WeatherAgent/50Weather01.config.json
volttron-ctl install ~/.volttron/packaged/weatheragent-0.1-py2-none-any.whl --tag weatherwunderground
volttron-ctl enable --tag weatherwunderground
volttron-ctl start --tag weatherwunderground

#consumption
volttron-pkg package Applications/code/ConsumptionAgent
volttron-pkg configure ~/.volttron/packaged/consumptionagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Applications/code/ConsumptionAgent/E05CRE0250883398.launch.json
volttron-ctl install ~/.volttron/packaged/consumptionagent-0.1-py2-none-any.whl --tag consumption
volttron-ctl enable --tag consumption
volttron-ctl start --tag consumption

echo "GGG!"
