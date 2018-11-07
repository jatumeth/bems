#mqtt
volttron-pkg package Agents/mqttsubAgent
volttron-pkg configure ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/mqttsubAgent/mqttsub.config
volttron-ctl install ~/.volttron/packaged/mqttsubagent-0.1-py2-none-any.whl --tag mqtt
volttron-ctl enable --tag mqtt

#daikin
volttron-pkg package Agents/01DAI_ACAgent
volttron-pkg configure ~/.volttron/packaged/acagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/01DAI_ACAgent/01DAI1200110.config.json
volttron-ctl install ~/.volttron/packaged/acagent-0.1-py2-none-any.whl --tag daikin
volttron-ctl enable --tag daikin

#Hue
volttron-pkg package Agents/02HUE_HueAgent
volttron-pkg configure ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/02HUE_HueAgent/02HUE1234500.config.json
volttron-ctl install ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl --tag hue
volttron-ctl enable --tag hue

#Tplink
volttron-pkg package Agents/GGGGG_TplinkPlugAgent
volttron-pkg configure ~/.volttron/packaged/plugagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/GGGGG_TplinkPlugAgent/03WSP123568.config.json
volttron-ctl install ~/.volttron/packaged/plugagent-0.1-py2-none-any.whl --tag plug
volttron-ctl enable --tag plug

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
