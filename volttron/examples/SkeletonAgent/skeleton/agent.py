import logging
from volttron.platform.vip.agent import Agent, Core, PubSub, RPC
from volttron.platform.agent import utils

utils.setup_logging()
_log = logging.getLogger(__name__)

class MyAgent(Agent):
    def __init__(self, config_path, **kwargs):
            self.config = utils.load_config(config_path)

    @Core.receiver('onsetup')
    def onsetup(self, sender, **kwargs):
        pass

    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
            self.vip.heartbeat.start()

    @Core.receiver('onstop')
    def onstop(self, sender, **kwargs):
        pass

    @Core.receiver('onfinish')
    def onfinish(self, sender, **kwargs):
        pass

    @PubSub.subscribe('pubsub', 'some/topic')
    def on_match(self, peer, sender, bus, topic, headers, message):
        pass

    @RPC.export
    def my_method(self): pass

def main():
    utils.vip_main(MyAgent)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass