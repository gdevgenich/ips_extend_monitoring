import asyncio

from extend_client import ExtendClient
from signalr_client import SignalRClient
import json


class IPSExtendChecker(object):

    def __init__(self, client_id, client_secret, hp_user_uid, client_resource, token_url, user_presence_url,
                 subscribe_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.hp_user_uid = hp_user_uid
        self.client_resource = client_resource
        self.token_url = token_url
        self.user_presence_url = user_presence_url
        self.subscribe_url = subscribe_url
        self.extend_client = None
        self.signalr_client = None
        self.errors = None

    def check_extend_presence(self, expected_presence):
        presence = json.loads(self.extend_client.get_user_presence(hp_user_uid=self.hp_user_uid))
        if presence.get("presence") == expected_presence:
            return None
        else:
            return "Expected {exp} but get {real}".format(exp=expected_presence, real=presence.get("presence"))

    def check(self):
        self.extend_client = ExtendClient(client_id="15kWI7uR2ESBLXFtbXNI6g",
                                          client_secret="vf1kxYHsy7mff6iekFX1K6505W0NSfHMXbPBfcK04HQ")
        self.extend_client.get_access_token()
        self.signalr_client = SignalRClient(extend_client=self.extend_client)
        connection_attempts = 0
        while not self.signalr_client.connected:
            connection_attempts += 1
            print(connection_attempts)
            self.signalr_client.start()
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
        self.extend_client.clear_presence(hp_user_uid=self.hp_user_uid, resource=self.client_resource)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(10))
        self.errors = self.check_extend_presence(expected_presence="offline")
        if self.errors is None:
            self.extend_client.set_presence(presence="agent_busy", hp_user_uid=self.hp_user_uid,
                                            resource=self.client_resource)
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(10))
            self.errors = self.check_extend_presence(expected_presence="agent_busy")
        if self.errors is None:
            self.extend_client.clear_presence(hp_user_uid=self.hp_user_uid, resource=self.client_resource)
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(10))
            self.errors = self.check_extend_presence(expected_presence="offline")
        if self.errors is None:
            self.errors = self.signalr_client.has_presence("agent_busy1")
        return self.errors
