volttron-pkg package Agents/mqttsubAgent
volttron-pkg configure ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/mqttsubAgent/mqttsub.config
volttron-ctl install ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl --tag mqtt
volttron-ctl enable --tag mqtt

#tv
volttron-pkg package Agents/01DAI_ACAgent
volttron-pkg configure ~/.volttron/packaged/acagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/01DAI_ACAgent/03WSP1234566.config.json
volttron-ctl install ~/.volttron/packaged/acagent-0.1-py2-none-any.whl --tag tv
volttron-ctl enable --tag tv

#fan
volttron-pkg configure ~/.volttron/packaged/acagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/01DAI_ACAgent/03WSP1234567.config.json
volttron-ctl install ~/.volttron/packaged/acagent-0.1-py2-none-any.whl --tag fan
volttron-ctl enable --tag fan

#plug
volttron-pkg package Agents/03WSP_TplinkPlugAgent
volttron-pkg configure ~/.volttron/packaged/plugagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/03WSP_TplinkPlugAgent/03WSP123568.config.json
volttron-ctl install ~/.volttron/packaged/plugagent-0.1-py2-none-any.whl --tag tplink
volttron-ctl enable --tag tplink

#powermeter1
volttron-pkg package Agents/05CRE_PowerMeterAgent
volttron-pkg configure ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/05CRE_PowerMeterAgent/05CRE532254311.config.json
volttron-ctl install ~/.volttron/packaged/powermeteragent-0.1-py2-none-any.whl --tag powermeter1
volttron-ctl enable --tag powermeter1

echo "Guidekub!"
