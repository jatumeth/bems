#mqtt
volttron-pkg package Agents/mqttsubAgent
volttron-pkg configure ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/mqttsubAgent/mqttsub.config
volttron-ctl install ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl --tag mqtt
volttron-ctl enable --tag mqtt

#fan
volttron-pkg package Agents/01DAI_ACAgent
volttron-pkg configure ~/.volttron/packaged/acagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/01DAI_ACAgent/03WSP1234566.config.json
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

#Scenesetup
volttron-pkg package Agents/ScenesetupAgent
volttron-pkg configure ~/.volttron/packaged/setupsceneagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/ScenesetupAgent/1KR221445K1200138.config.json
volttron-ctl install ~/.volttron/packaged/setupsceneagent-0.1-py2-none-any.whl --tag scenesetup
volttron-ctl enable --tag scenesetup

#Scene
volttron-pkg package Agents/SceneAgent
volttron-pkg configure ~/.volttron/packaged/sceneagentagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/SceneAgent/sceneconfig.json
volttron-ctl install ~/.volttron/packaged/sceneagentagent-0.1-py2-none-any.whl --tag scene
volttron-ctl enable --tag scene

echo "Guidekub!"
