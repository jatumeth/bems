# Import the packages and classes we will need:
import logging
import sys

from volttron.platform.vip.agent import Agent, PubSub
from volttron.platform.agent import utils

# Initialize the logging facility, agents should favor logging over print
utils.setup_logging()
_log = logging.getLogger(__name__)

# Since we want to publish we will import the PubSub module

class TestAgent(Agent):

    '''
        Create an init method to deal with creating the agent and getting the
        config file later
    '''
    def __init__(self, config_path, **kwargs):
        super(TestAgent, self).__init__(**kwargs)

    '''
        Add Configuration Store Support
    '''
    def __init__(self, config_path, **kwargs):
        super(TestAgent, self).__init__(**kwargs)

        self.setting1 = 42
        self.default_config = {"setting1": self.setting1}

        self.vip.config.set_default("config", self.default_config)
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")

    def configure(self, config_name, action, contents):
        config = self.default_config.copy()
        config.update(contents)

        # make sure config variables are valid
        try:
            self.setting1 = int(config["setting1"])
        except ValueError as e:
            _log.error("ERROR PROCESSING CONFIGURATION: {}".format(e))


    '''
        Setting up a Subscription
    '''
    @PubSub.subscribe('pubsub', 'heartbeat/listeneragent')
    def on_heartbeat_topic(self, peer, sender, bus, topic, headers, message):
        print "TestAgent got\nTopic: {topic}, {headers}, Message: {message}".format(topic=topic, headers=headers,
                                                                                    message=message)

'''
    Argument Parsing and Main
'''
def main(argv=sys.argv):
    '''Main method called by the platform.'''
    utils.vip_main(TestAgent)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass































