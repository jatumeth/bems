#!/bin/bash

#powermeter1
volttron-pkg package Applications/code/ConsumptionAgent
volttron-pkg configure ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl ~/workspace/hive_os/volttron/Applications/code/ConsumptionAgent/E05CRE270121594.launch.json
volttron-ctl install ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl --tag con1
volttron-ctl enable --tag con1
volttron-ctl start --tag con1

#powermeter2
volttron-pkg package Applications/code/ConsumptionAgent
volttron-pkg configure ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl ~/workspace/hive_os/volttron/Applications/code/ConsumptionAgent/E05CRE389362892.launch.json
volttron-ctl install ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl --tag con2
volttron-ctl enable --tag con2
volttron-ctl start --tag con2

#powermeter3
volttron-pkg package Applications/code/ConsumptionAgent
volttron-pkg configure ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl ~/workspace/hive_os/volttron/Applications/code/ConsumptionAgent/E05CRE621800813.launch.json
volttron-ctl install ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl --tag con3
volttron-ctl enable --tag con3
volttron-ctl start --tag con3

#powermeter4
volttron-pkg package Applications/code/ConsumptionAgent
volttron-pkg configure ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl ~/workspace/hive_os/volttron/Applications/code/ConsumptionAgent/E05CRE960794931.launch.json
volttron-ctl install ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl --tag con4
volttron-ctl enable --tag con4
volttron-ctl start --tag con4

#powermeter5
volttron-pkg package Applications/code/ConsumptionAgent
volttron-pkg configure ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl ~/workspace/hive_os/volttron/Applications/code/ConsumptionAgent/E05CRE998025329.launch.json
volttron-ctl install ~/.volttron/packaged/consumptionagent-3.2-py2-none-any.whl --tag con5
volttron-ctl enable --tag con5
volttron-ctl start --tag con5

echo "GGG!"
