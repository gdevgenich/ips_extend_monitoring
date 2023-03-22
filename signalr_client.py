from signalrcore.hub_connection_builder import HubConnectionBuilder
from extend_client import ExtendClient
import logging
import logging.handlers
import json

logger = logging.getLogger("signalr_client")

class SignalRClient(object):

    def __init__(self, extend_client: ExtendClient):
        self.extend_client = extend_client
        self.hub_connection = None
        self.connected = False
        self.messages = list()
        self.__connection_reattempt_count = 0

    def create_hub_connection(self, logging_level=logging.DEBUG,
                              logging_handler=logging.handlers.SysLogHandler(address="/dev/log")):
        self.extend_client.get_access_token()
        uri = self.extend_client.get_subscribe_uri()
        self.hub_connection = HubConnectionBuilder().with_url(uri,
                                          options={
                                              "access_token_factory": self.extend_client.get_access_token,
                                          }) \
                                          .configure_logging(logging_level=logging_level, handler=logging_handler) \
                                          .with_automatic_reconnect({
                                            "type": "raw",
                                            "keep_alive_interval": 10,
                                            "reconnect_interval": 5,
                                            "max_attempts": 5
                                          }).build()

    def register_message(self, *args):
        for el in args:
            for presence in el:
                self.messages.append(presence)

    def has_presence(self, presence):
        for msg in self.messages:
            if msg.get("presenceState") == presence:
                return None
        return "No expected presence {exp} in {real}".format(exp=presence, real=self.messages)

    def set_connected(self):
        self.connected = True
        logger.info("Connection ready")

    def start(self):
        if self.hub_connection is None:
            self.create_hub_connection()
        self.hub_connection.on_open(lambda: self.set_connected())
        self.hub_connection.on("OnPresenceEvent", self.register_message)
        self.hub_connection.start()

    def stop(self):
        self.hub_connection.on_close(lambda: logger.info("Close connection"))
        self.hub_connection.stop()


