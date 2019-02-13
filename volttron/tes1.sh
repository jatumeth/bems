#!/bin/bash
#Inwall Agent

volttron-pkg package Agents/02ORV_InwallLightingAgent
# Set the agent's configuration file
volttron-pkg configure ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/02ORV_InwallLightingAgent/02ORVD6F0011A70953o.config.json
volttron-ctl install ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl --tag 02ORVD6F0011A70953o
volttron-pkg configure ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/02ORV_InwallLightingAgent/02ORVD6F0011A7129Eo.config.json
volttron-ctl install ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl --tag 02ORVD6F0011A7129Eo
volttron-ctl enable --tag 02ORVD6F0011A70953o
volttron-ctl start --tag 02ORVD6F0011A70953o
volttron-ctl enable --tag 02ORVD6F0011A7129Eo
volttron-ctl start --tag 02ORVD6F0011A7129Eo
