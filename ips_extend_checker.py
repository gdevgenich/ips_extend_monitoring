import asyncio

from extend_client import ExtendClient
from signalr_client import SignalRClient
import json
import graphyte
from mail_reporter import send_report
from json import loads


class IPSExtendChecker(object):

    def __init__(self, config_file, section_name):
        self.config_file = config_file
        self.section_name = section_name
        self.res_file = "/var/tmp/monitoring/extend_{number}_sync".format(number=section_name)

        self.emails = None
        self.graphyte_host = None
        self.graphyte_port = None
        self.client_id = None
        self.client_secret = None
        self.hp_user_uid = None
        self.client_resource = None
        self.token_url = None
        self.user_presence_url = None
        self.subscribe_url = None
        self.extend_client = None
        self.signalr_client = None
        self.error_message = None

    def read_data_from_config(self):
        with open(self.config_file) as stream:
            content = stream.read()
        res = loads(content)
        self.emails = res.get("email_notification").get("emails")
        self.graphyte_host = res.get("graphyte").get("host")
        self.graphyte_port = res.get("graphyte").get("port")
        self.token_url = res.get("urls").get("token_url")
        self.user_presence_url = res.get("urls").get("user_presence_ulr")
        self.subscribe_url = res.get("urls").get("subscribe_url")
        account = res.get(name=self.section_name)
        self.client_id = account.get("client_id")
        self.client_secret = account.get("client_secret")
        self.hp_user_uid = account.get("hp_user_uid")
        self.client_resource = account.get("client_resource")

    def check_extend_presence(self, expected_presence):
        presence = json.loads(self.extend_client.get_user_presence(hp_user_uid=self.hp_user_uid))
        if presence.get("presence") == expected_presence:
            return None
        else:
            return "Expected {exp} but get {real}".format(exp=expected_presence, real=presence.get("presence"))

    def clients_init(self):
        self.extend_client = ExtendClient(client_id=self.client_id, client_secret=self.client_secret,
                                          subscribe_url=self.subscribe_url, user_presence_uri=self.user_presence_url,
                                          token_url=self.token_url)
        self.extend_client.get_access_token()
        self.signalr_client = SignalRClient(extend_client=self.extend_client)
        connection_attempts = 0
        while not self.signalr_client.connected:
            if connection_attempts > 5:
                raise RuntimeError("Can't connect to signalr server")
            connection_attempts += 1
            self.signalr_client.start()
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))

    def check(self):
        self.extend_client.clear_presence(hp_user_uid=self.hp_user_uid, resource=self.client_resource)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(10))
        self.error_message = self.check_extend_presence(expected_presence="offline")
        if self.error_message is None:
            self.extend_client.set_presence(presence="agent_busy", hp_user_uid=self.hp_user_uid,
                                            resource=self.client_resource)
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(10))
            self.error_message = self.check_extend_presence(expected_presence="agent_busy")
        if self.error_message is None:
            self.extend_client.clear_presence(hp_user_uid=self.hp_user_uid, resource=self.client_resource)
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(10))
            self.error_message = self.check_extend_presence(expected_presence="offline")
        if self.error_message is None:
            self.error_message = self.signalr_client.has_presence("agent_busy1")
        if self.error_message is not None:
            raise RuntimeError(self.error_message)

    def send_report(self):
        if self.error_message is not None:
            test_res = open(self.res_file, mode='w')
            test_res.write(self.error_message + "\n")
            test_res.write("1")
            test_res.close()
            subject = "Monitoring detect failure in extend rmq monitoring {name}".format(name=self.section_name)
            send_report(to=self.emails, subject=subject, body=self.error_message)
        else:
            test_res = open(self.res_file, mode="w")
            test_res.write("0")
            test_res.close()

        try:
            import socket
            hostname = socket.gethostname().split(".")[0]
            graphyte.init(host=self.graphyte_host, port=self.graphyte_port,
                          prefix="apps.HPBXMon")
            graphyte.send("{hostname}.status".format(hostname=hostname), 0.0, tags={"zzz_team": "hpbx"})
        except Exception as e:
            pass
