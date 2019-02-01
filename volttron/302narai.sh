#!/bin/bash

volttron-pkg package Agents/02ORV_InwallLightingAgent
volttron-pkg configure ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl ~/workspace/hive_os/volttron/Agents/02ORV_InwallLightingAgent/02ORVD6F0011A71230o.config.json
volttron-ctl install ~/.volttron/packaged/lightingagent-0.1-py2-none-any.whl --tag 302bathlight
volttron-ctl enable --tag 302bathlight
volttron-ctl start --tag 302bathlight
