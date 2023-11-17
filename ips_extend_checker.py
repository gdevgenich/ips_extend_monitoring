import asyncio

from extend_client import ExtendClient
from signalr_client import SignalRClient
import json
from mail_reporter import send_report
from configparser2.yaml import loads
import logging.handlers

class IPSExtendChecker(object):

    def __init__(self, config_file, section_name):
        self.config_file = config_file
        self.section_name = section_name
        self.res_file = "/var/tmp/monitoring/extend_{number}_sync".format(number=section_name)

        self.emails = None
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
        self.token_url = res.get("urls").get("token_url")
        self.user_presence_url = res.get("urls").get("user_presence_ulr")
        self.subscribe_url = res.get("urls").get("subscribe_url")
        account = res.get(name=self.section_name)
        self.client_id = account.get("client_id")
        self.client_secret = account.get("client_secret")
        self.hp_user_uid = account.get("hp_user_uid")
        self.client_resource = account.get("client_resource")

    def check_extend_presence(self, expected_presence):
        try:
            presence = json.loads(self.extend_client.get_user_presence(hp_user_uid=self.hp_user_uid))
            if presence.get("presence") == expected_presence:
                return None
            else:
                asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
                presence = json.loads(self.extend_client.get_user_presence(hp_user_uid=self.hp_user_uid))
                if presence.get("presence") == expected_presence:
                    return None
            return f"Expected {expected_presence} but get {presence.get('presence')}"
        except:
            return "Exception happen during extend presence check"

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

    def clients_stop(self):
        self.signalr_client.stop()

    def set_logging(self):
        formatter = logging.Formatter(
            fmt="extend_ips_monitoring: %(levelname)s | {server} |%(message)s".format(server=self.section_name))
        for logger_name in ["asyncio", "extend_client", "SignalRCoreClient"]:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            file_handler = logging.handlers.SysLogHandler(address="/dev/log")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.propagate = False

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
            self.error_message = self.signalr_client.has_presence("agent_busy")

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
