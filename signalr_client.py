from signalrcore.hub_connection_builder import HubConnectionBuilder
from signalrcore.transport.websockets.websocket_transport import WebsocketTransport, ConnectionState
from extend_client import ExtendClient
import logging.handlers
import requests
import threading
import ssl
from signalrcore.helpers import Helpers
from signalrcore.hub.errors import HubError, UnAuthorizedHubError
import websocket


def negotiate(self):
    negotiate_url = Helpers.get_negotiate_url(self.url)
    self.logger.debug("Negotiate url:{0}".format(negotiate_url))

    response = requests.post(
        negotiate_url, headers=self.headers, verify=self.verify_ssl)
    self.logger.debug(
        "Response status code{0}".format(response.status_code))

    if response.status_code != 200:
        raise HubError(response.status_code) \
            if response.status_code != 401 else UnAuthorizedHubError()

    data = response.json()
    if "connectionId" in data.keys():
        self.url = Helpers.encode_connection_id(
            self.url, data["connectionId"])
    # Azure
    if 'url' in data.keys() and 'accessToken' in data.keys():
        Helpers.get_logger().debug(
            "Azure url, reformat headers, token and url {0}".format(data))
        self.url = data["url"] \
            if data["url"].startswith("ws") else \
            Helpers.http_to_websocket(data["url"])
        self.token = data["accessToken"]
        self.headers = {"Authorization": "Bearer " + self.token}
    self.im_cookie = ""
    for domain, cookie in response.cookies.items():
        self.im_cookie += domain+"="+cookie+";"


def start(self):
    if not self.skip_negotiation:
        self.negotiate()

    if self.state == ConnectionState.connected:
        self.logger.warning("Already connected unable to start")
        return False

    self.state = ConnectionState.connecting
    self.logger.debug("start url:" + self.url)

    self._ws = websocket.WebSocketApp(
        self.url,
        header=self.headers,
        on_message=self.on_message,
        on_error=self.on_socket_error,
        on_close=self.on_close,
        on_open=self.on_open,
        cookie=self.im_cookie,
    )

    self._thread = threading.Thread(
        target=lambda: self._ws.run_forever(
            sslopt={"cert_reqs": ssl.CERT_NONE}
            if not self.verify_ssl else {}
        ))
    self._thread.daemon = True
    self._thread.start()
    return True


WebsocketTransport.negotiate = negotiate
WebsocketTransport.start = start

logger = logging.getLogger("signalr_client")

class SignalRClient(object):

    def __init__(self, extend_client: ExtendClient):
        self.extend_client = extend_client
        self.hub_connection = None
        self.connected = False
        self.messages = list()
        self.__connection_reattempt_count = 0

    def create_hub_connection(self):
        self.extend_client.get_access_token()
        uri = self.extend_client.get_subscribe_uri()
        self.hub_connection = HubConnectionBuilder().with_url(uri,
                                          options={
                                              "access_token_factory": self.extend_client.get_access_token,
                                          })\
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

    def reconnect(self):
        logger.debug(msg="Connection lost.")

    def start(self):
        if self.hub_connection is None:
            self.create_hub_connection()
        self.hub_connection.on_open(lambda: self.set_connected())
        self.hub_connection.on_close(lambda: self.reconnect())
        self.hub_connection.on("OnPresenceEvent", self.register_message)
        self.hub_connection.start()

    def stop(self):
        self.hub_connection.on_close(lambda: logger.info("Close connection"))
        self.hub_connection.stop()


