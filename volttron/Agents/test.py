import json
from os.path import expanduser
home_path = expanduser("~")
json_path = '/workspace/hive_os/volttron/token.json'
automation_control_path = home_path + json_path
launcher = json.load(open(home_path + json_path, 'r'))  # load config.json to variable
#  Update new agentID to variable (agentID is relate to automation_id)
launcher.update({'token': '123'})
json.dump(launcher, open(home_path + json_path, 'w'), sort_keys=True, indent=4)