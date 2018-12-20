"""
Agent documentation goes here.
"""

from __future__ import print_function

__docformat__ = 'reStructuredText'

import logging
import json
import subprocess
import sys
import socket
import broadlink

from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"
DEVID="peadisc-agent"
DFLTTOPIC="/agent/zmq/update/hive/discovery"



def discovery(config_path, **kwargs):
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

    topic = config.get('topic', )
    _log.debug("Topic is: "+topic)
    return Discovery(topic, **kwargs)




class Discovery(Agent):
    """
    Document agent constructor here.
    """

    def __init__(self, topic=DFLTTOPIC,
                 **kwargs):
        super(Discovery, self).__init__(**kwargs)
        _log.debug("vip_identity: " + self.core.identity)
        self.loplugs={}

        self.default_config = {}
        self.topic = topic


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
        _log.debug("Got message %s" % str(message))
        msg = json.loads(message.decode("utf-8"))
        _log.debug("Got message %s" % str(msg))
        response={}
        if "command" in msg:
            try:
                if msg["command"] == "discovery":
                    self._disc_broadlink(msg)
                    self._disc_camera(msg)
                    self._disc_sonoff(msg)
                    self._disc_tplink(msg)

            except Exception as e:
                topic = self.topic
                message = json.dumps({"device": DEVID, "event": "error", "value":str(e)})
                self.vip.pubsub.publish(
                    'pubsub', topic,
                    {'Type': 'pub device status to ZMQ'}, message)

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

        self._create_subscriptions(self.topic)
        
    def _disc_camera(self,msg):
        #Example RPC call
        #self.vip.rpc.call("some_agent", "some_method", arg1, arg2)
        _log.debug("Discovering Camera devices.")
        if "username" in msg:
            user=msg["username"]
        else:
            user = None
        if "password" in msg:
            passwd = msg["password"]
        else:
            passwd = ""
        if user:
            output = subprocess.Popen("env -i /usr/local/bin/camera-discovery -u '%s' -p '%s'"%(user,passwd), shell=True, stdout=subprocess.PIPE)
        else:
            output = subprocess.Popen("env -i /usr/local/bin/camera-discovery", shell=True, stdout=subprocess.PIPE)
        message = output.communicate()
        if message[0].strip() not in ["", "{}"]:
            topic = self.topic + "/camera"
            _log.debug("Sending message: %s"%str(message))
            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message[0].strip())



    def _disc_sonoff(self,msg):
        #Example RPC call
        #self.vip.rpc.call("some_agent", "some_method", arg1, arg2)
        _log.debug("Discovering Sonoff devices.")
        output = subprocess.Popen("env -i /usr/local/bin/sonoff-discovery -p Sonoff", shell=True, stdout=subprocess.PIPE)
        message = output.communicate()
        if message[0].strip() not in ["", "{}"]:
            topic = self.topic + "/sonoff"
            _log.debug("Sending message: %s"%str(message))
            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message[0].strip())


    def _disc_tplink(self,msg):
        #Example RPC call
        #self.vip.rpc.call("some_agent", "some_method", arg1, arg2)
        _log.debug("Discovering TP-Link devices.")
        output = subprocess.Popen("env -i /usr/local/bin/tplink-discovery", shell=True, stdout=subprocess.PIPE)
        message = output.communicate()
        if message[0].strip() not in ["", "{}"]:
            topic = self.topic + "/tp-link"
            _log.debug("Sending message: %s"%str(message))
            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message[0].strip())

    def _disc_broadlink(self,msg):
        #Example RPC call
        #self.vip.rpc.call("some_agent", "some_method", arg1, arg2)
        _log.debug("Discovering Broadlink devices.")
        result = {}
        devices = broadlink.discover(timeout=5)
        for dev in devices:
            try:
                ip, port = dev.host
                model = devices[0].type
                mac = ":".join([ "%02x"%x for x in devices[0].mac[::-1]])
                result[ip] = {"port": port, "mac address": mac, "model": model}
            except:
                pass
        if result:
            topic = self.topic + "/broadlink"
            _log.debug("Sending message: %s"%str(result))
            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, json.dumps(result))



    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        """
        This method is called when the Agent is about to shutdown, but before it disconnects from
        the message bus.
        """

        for adev in self.loplugs.values():
            topic = self.topic
            message = json.dumps({"device": adev.dev_id, "event": "presence", "value":{"status":"offline"}})

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)


def main():
    """Main method called to start the agent."""
    utils.vip_main(discovery,
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
