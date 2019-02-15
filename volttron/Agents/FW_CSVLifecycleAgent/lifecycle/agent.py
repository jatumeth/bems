"""
Agent documentation goes here.
"""

from __future__ import print_function

__docformat__ = 'reStructuredText'

import logging
import json
import subprocess
import sys,os
import csv
from threading import Thread, Lock
from Queue import Queue

from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC
import time


_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"
DEVID = "hiveos-lifecycle-agent"
DFLTTOPIC = "/hiveos/services/lifecycle"
CONFIGDIR = "AgentConfig"
DISCTRESH = 2
DFLTLOC = "/home/pi/workspace/hive_os/volttron"
DFLTCSVFILE = "openclose_new.csv"
AGENTNAME = "18ORC_OpenCloseAgent"
COUNTDOWN = 60
zone_id = 999

def normalize(brand):
    nbrand = ""
    for x in brand.lower():
        if x in "abcdefghijklmnopqrstuvwxyz":
            nbrand += x
    return nbrand


def lifecycle(config_path, **kwargs):
    """Parses the Agent configuration and returns an instance of
    the agent created using that configuration.

    :param config_path: Path to a configuration file.
    :type config_path: str
    :param kwargs: Dictionary passed to Agent creation.  
    :type kwargs: dict
    :returns: Discovery
    :rtype: Discovery
    """
    try:
        config = utils.load_config(config_path)
    except StandardError:
        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    topic = config.get('topic', DFLTTOPIC)
    fileloc = config.get('default location', DFLTLOC)
    csvfile = config.get('csvfile', fileloc +"/"+DFLTCSVFILE)
    if not os.path.isdir(fileloc+"/"+CONFIGDIR):
        os.mkdir(fileloc+"/"+CONFIGDIR)

    _log.debug("Topic is: "+topic)
    return Lifecycle(topic, csvfile, fileloc,  **kwargs)




class Lifecycle(Agent):
    """
    Document agent constructor here.
    """

    def __init__(self, topic=DFLTTOPIC, csvfile=DFLTCSVFILE, fileloc=DFLTLOC, **kwargs):
        super(Lifecycle, self).__init__(**kwargs)
        _log.debug("vip_identity: " + self.core.identity)
        self.default_config = {}
        self.topic = topic
        self.csvfile = csvfile
        self.fileloc = fileloc
        self.knowndevices = {}
        self.alreadyknown = []
        self.lock = Lock()
        self.countdown = COUNTDOWN

        #Grab info from sqlite database

        #Set a default configuration to ensure that self.configure is called immediately to setup
        #the agent.
        self.vip.config.set_default("config", self.default_config)
        #Hook self.configure up to changes to the configuration file "config".
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")

    def configure(self, config_name, action, contents):
        """
        Called after the Agent has connected to the message bus. If a configuration exists at startup
        this will be called before onstart.

        Is called every time the configuration in the store changes.
        """
        config = self.default_config.copy()
        config.update(contents)

        _log.debug("Configuring Agent (%s)"%self.topic)


    def _create_subscriptions(self, topic):
        #Unsubscribe from everything.
        self.vip.pubsub.unsubscribe("pubsub", None, None)

        self.vip.pubsub.subscribe(peer='pubsub',
                                  prefix=topic,
                                  callback=self._handle_publish)

    def _handle_publish(self, peer, sender, bus, topic, headers,
                                message):
        #_log.debug("Got message %s" % str(message))
        msg = json.loads(message.decode("utf-8"))
        _log.debug("For topic %s got message %s" % (topic,str(msg)))
        response={}
        if "type" in msg and msg["type"] == "command":
            if msg["command"] == "stop me":
                self._do_stopme(msg)
        else:
            self._do_process(msg,topic.split("/")[-1])

    def _do_stopme(self, msg):
        #TODO Update agentmatch and modelmatch tables
        xx = Thread(target=self._do_stop_thread, args = (msg["devid"]))
        xx.setDaemon(True)
        xx.start()      

    def _do_manage(self, msg):
        #TODO Update agentmatch and modelmatch tables
        if "subject" in msg and msg["subject"] in ["known device", "agent", "model"]:
            xx = Thread(target=self._do_manage_thread, args = (msg))
            xx.setDaemon(True)
            xx.start()  
            

    @Core.periodic(5)
    def _do_process(self):
        if self.countdown > 0:
            self.countdown -= 1
            return 
        self.countdown = COUNTDOWN
        notprocessed = self.knowndevices.keys()
        with open(self.csvfile, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:

                try:
                    devid, uuid, url, bearer, model, devname = [ x.strip() for x in row ]
                except:
                    _log.debug("Erro: Badly formated line: {}".format(row))
                    continue

                startme = False
                configme = False
                stopme = False
                if devid in self.knowndevices:
                    _log.debug("Processing known device {}".format(devname))
                    if self.knowndevices[devid]:
                        _log.debug("Known device from {} is thought to be running".format(devname))
                        continue #It is running, or so we think
                    else:
                        startme = True
                else:
                    _log.debug("Processing new device {} with id {}".format(devname,devid))
                    configme = True
                    startme = True
                
                if startme:
                    xx = Thread(target=self._do_process_thread, args = (devid, uuid, url, bearer, devname, model,
                                                                        [stopme, configme, startme]))
                    xx.setDaemon(True)
                    xx.start()  
                try:
                    notprocessed.remove(devid)
                except:
                    pass

        for devid in notprocessed:
            xx = Thread(target=self._do_process_thread, args = (devid, "", "", "", "", "",
                                                                [True, False, False]))
            xx.setDaemon(True)
            xx.start()  
            
                
    def _do_firstprocess_thread(self):
        #Checking devices known to voltron
        try:
            self.lock.acquire()
            #Not sure, let's check, will only happen at start
            statusreply = subprocess.check_output(self.fileloc+'/env/bin/volttron-ctl status',shell=True)
            found = False
            startme=False
            for line in statusreply.split("\n"):
                cmdresp = [x.strip() for x in line.split(" ") if x.strip()]
                if len(cmdresp)>3:
                    self.alreadyknown.append(cmdresp[3].strip())
        except Exception as e:
            _log.debug("ERROR: Could not figure out already configured agents. {}".format(e))
        finally:
            self.lock.release()
        _log.info("list of know tags. {}".format(self.alreadyknown))
        self.countdown = 0
        
    def _do_process_thread(self, devid, uuid, url, bearer, devname, model, flags):
        _log.debug("Process for {} with {}".format(devname,flags))
        notify=False
        try:
            stopme, configme, startme = flags
            confname = self.fileloc+"/dev_config/"+devid+".conf"
            if devid not in self.knowndevices:
                if devid in self.alreadyknown:
                    _log.debug("Known device {}, {} needs to be started.".format(devname,devid))
                    startme = True
                    configme = False
                else:
                    _log.debug("Device  {}, {} needs to be configured and started.".format(devname,devid))
                    configme = True
                    startme = True
            if stopme:
                _log.debug("Process for {} should be stopped.".format(devname))
                if configme:
                    statusreply = subprocess.call(self.fileloc+'/env/bin/volttron-ctl remove --tag %s'%devid,shell=True)
                else:
                    statusreply = subprocess.call(self.fileloc+'/env/bin/volttron-ctl stop --tag %s'%devid,shell=True)

            if configme:
                _log.debug("Process for {} should be configured.".format(devid))
                configuration = {}
                configuration["agent_id"]=devid
                configuration["message"] = "this is openclosed agent",
                configuration["heartbeat_period"] = 300
                configuration["api"] = "classAPI_Smartthings_openclose"
                configuration["url"] =url 
                configuration["device"] = uuid
                configuration["zone_id"] = zone_id
                configuration["bearer"] = bearer
                configuration["building_name"] =  "hive"
                configuration["device_monitor_time"] = 5
                configuration["model"] = model
                
                #Let's now create the agent instance
                try:
                    self.lock.acquire()
                    _log.debug("Packaging")
                    statusreply = subprocess.check_output(self.fileloc+"/env/bin/volttron-pkg package "+self.fileloc+"/Agents/"+AGENTNAME,shell=True)
                    try:
                        wheelfile = statusreply.split("Package created at:")[1].strip()
                    except Exception as e:
                        raise Exception("Agent could not be packaged.")
                    _log.debug("Wheelfile is {}.".format(wheelfile))
                    configuration["agent"] = {"exec": os.path.basename(wheelfile) + " --config \"%c\" --sub \"%s\" --pub \"%p\""}
                    cfname = self.fileloc+"/"+CONFIGDIR+"/"+devid+".conf"
                    _log.debug("Saving to {}: {}.".format(cfname,configuration))
                    conffile = open(cfname,"w")
                    json.dump(configuration,conffile)
                    conffile.close()
                    #Configure
                    _log.debug("Configuring")
                    statusreply = subprocess.call(self.fileloc+"/env/bin/volttron-pkg configure "+wheelfile+" "+cfname,shell=True)
                    _log.debug("Installing")
                    statusreply = subprocess.call(self.fileloc+"/env/bin/volttron-ctl install " + wheelfile + " --tag "+ devid + " --vip-identity vip"+devid,shell=True)
                    if devid not in self.knowndevices:
                        notify = True
                    self.knowndevices[devid] = startme
                except Exception as e:
                    _log.debug("ERROR: Could not configure. {}".format(e))
                    startme = False
                    configme = False
                finally:
                    self.lock.release()
            
            if startme:
                _log.debug("Process for {} should be started.".format(devname))
                statusreply = subprocess.call(self.fileloc+"/env/bin/volttron-ctl start --tag "+ devid,shell=True)
                statusreply = subprocess.call(self.fileloc + "/env/bin/volttron-ctl enable --tag " + devid, shell=True)
                self.knowndevices[devid] = True
                
            if configme:
                if notify:
                    _log.debug("Lifecycle sending new device event.")
                    ntopic = "/hiveos/devices"
                    message = json.dumps({"type":"event", "event": "new device", 
                                          "value":{"devid":devid,"name":devname, "device":uuid}})

                    self.vip.pubsub.publish(
                        'pubsub', ntopic,
                        {'Type': 'HiveOS notification'}, message)
        except Exception as e:
            _log.debug("Lifecycle for {} failed miserably: {}".format(devid,e))
      
    def _do_stopme_thread(self, devid):
        statusreply = subprocess.call(self.fileloc+'/env/bin/volttron-ctl stop --tag %s'%devid,shell=True)
        
    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        This is method is called once the Agent has successfully connected to the platform.
        This is a good place to setup subscriptions if they are not dynamic or
        do any other startup activities that require a connection to the message bus.
        Called after any configurations methods that are called at startup.

        Usually not needed if using the configuration store.
        """
        #Example publish to pubsub
        #self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")
        xx = Thread(target=self._do_firstprocess_thread)
        xx.setDaemon(True)
        xx.start()  
        self._create_subscriptions(self.topic)
        msg=json.dumps({"type": "command", "command": "discover", "parameter":{}})
        self.vip.pubsub.publish(
                'pubsub', DFLTTOPIC.replace("lifecycle","discovery"),
                {'Type': 'HiveOS notification'}, msg)
        


    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        """
        This method is called when the Agent is about to shutdown, but before it disconnects from
        the message bus.
        """
        pass

def main():
    """Main method called to start the agent."""
    utils.vip_main(lifecycle,
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass

