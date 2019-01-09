#!/bin/bash
#Inwall Agent

volttron-pkg package Agents/02ORV_InwallLightingAgent
volttron-pkg configure ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/02ORV_InwallLightingAgent/02HUE1234551.config.json
volttron-ctl install ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl --tag blight
volttron-pkg configure ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/02ORV_InwallLightingAgent/02HUE1234560.config.json
volttron-ctl install ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl --tag flight
volttron-ctl enable --tag blight
volttron-ctl enable --tag flight
volttron-ctl start --tag blight
volttron-ctl start --tag flight

#Fibaro Agent
volttron-pkg package Agents/20FIB_FibaroAgent
volttron-pkg configure ~/.volttron/packaged/fibaroagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/20FIB_FibaroAgent/20FIB87654328.config.json
volttron-ctl install ~/.volttron/packaged/fibaroagent-0.1-py2-none-any.whl --tag fibaro
volttron-ctl enable --tag fibaro
volttron-ctl start --tag fibaro


#Plug Agent
volttron-pkg package Agents/03WSP_PlugAgent
volttron-pkg configure ~/.volttron/packaged/plugagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/03WSP_PlugAgent/03WSP060BFEA.config.json
volttron-ctl install ~/.volttron/packaged/plugagent-0.1-py2-none-any.whl --tag Plug
volttron-ctl enable --tag Plug
volttron-ctl start --tag Plug


#mqtt
volttron-pkg package Agents/mqttsubAgent
volttron-pkg configure ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/mqttsubAgent/mqttsub.config
volttron-ctl install ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl --tag mqtt
volttron-ctl enable --tag mqtt
volttron-ctl start --tag mqtt

#powermeter1
volttron-pkg package Agents/05CRE_PowerMeterAgent
volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/05CRE_PowerMeterAgent/05CRE960794931.config.json
volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter1
volttron-ctl enable --tag powermeter1
volttron-ctl start --tag powermeter1

#powermeter2
volttron-pkg package Agents/05CRE_PowerMeterAgent
volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/05CRE_PowerMeterAgent/05CRE124930529.config.json
volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter2
volttron-ctl enable --tag powermeter2
volttron-ctl start --tag powermeter2

#powermeter3
volttron-pkg package Agents/05CRE_PowerMeterAgent
volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/05CRE_PowerMeterAgent/05CRE270121594.config.json
volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter3
volttron-ctl enable --tag powermeter3
volttron-ctl start --tag powermeter3

#powermeter4
volttron-pkg package Agents/05CRE_PowerMeterAgent
volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/05CRE_PowerMeterAgent/05CRE389362892.config.json
volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter4
volttron-ctl enable --tag powermeter4
volttron-ctl start --tag powermeter4

#powermeter5
volttron-pkg package Agents/05CRE_PowerMeterAgent
volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/05CRE_PowerMeterAgent/05CRE621800813.config.json
volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter5
volttron-ctl enable --tag powermeter5
volttron-ctl start --tag powermeter5

#powermeter6
volttron-pkg package Agents/05CRE_PowerMeterAgent
volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/05CRE_PowerMeterAgent/05CRE998025329.config.json
volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter6
volttron-ctl enable --tag powermeter6
volttron-ctl start --tag powermeter6

#air
volttron-pkg package Agents/22Broadlink_Agent
volttron-pkg configure ~/.volttron/packaged/broadlinkagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/22Broadlink_Agent/03WSP1234567.config.json
volttron-ctl install ~/.volttron/packaged/broadlinkagent-0.1-py2-none-any.whl --tag air
volttron-ctl enable --tag air
volttron-ctl start --tag air

#energy trading
volttron-pkg package Agents/EnergyTradeAgent
volttron-pkg configure ~/.volttron/packaged/energytradeagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/EnergyTradeAgent/sub001.config.json
volttron-ctl install ~/.volttron/packaged/energytradeagent-0.1-py2-none-any.whl --tag trading
volttron-ctl enable --tag trading
volttron-ctl start --tag trading

echo "GGG!"
