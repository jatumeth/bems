#!/bin/bash

volttron-pkg package Agents/02ORV_InwallLightingLoggingAgent
volttron-pkg configure ~/.volttron/packaged/lightingloggingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/02ORV_InwallLightingLoggingAgent/lighting.config
volttron-ctl install ~/.volttron/packaged/lightingloggingagent-0.1-py2-none-any.whl --tag loggingAgent
volttron-ctl enable --tag loggingAgent
volttron-ctl start --tag loggingAgent


