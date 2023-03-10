import requests
import json
import logging


class ExtendClient(object):

    def __init__(self, client_id, client_secret, token_url=None, user_presence_uri=None, subscribe_url=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.logger = logging.getLogger("extend_client")
        self.token_url = token_url if token_url is not None else "https://login.intermedia.net/user/connect/token"
        self.user_presence_uri = user_presence_uri if user_presence_uri is not None else \
            "https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/"
        self.subscribe_url = subscribe_url if subscribe_url is not None else \
            "https://api.intermedia.net/messaging/v1/subscriptions/accounts/_me/users/_all"


    def get_access_token(self):
        if self.access_token is None:
            body = {"grant_type": "client_credentials", "client_id": self.client_id,
                    "client_secret": self.client_secret, "scope": "api.service.messaging"}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            req = requests.Request(method="POST", headers=headers, data=body, url=self.token_url)
            self.logger.debug("Request {request}".format(request=requests))
            resp = requests.session().send(request=req.prepare())
            self.logger.debug("Response {resp}".format(resp=resp))
            self.access_token = json.loads(resp.content.decode()).get("access_token")
            self.refresh_token = json.loads(resp.content.decode()).get("refresh_token")

    def refresh_access_token(self):
        raise NotImplementedError

    def get_user_presence(self, hp_user_uid):
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + self.access_token}
        url = self.user_presence_uri+hp_user_uid
        req = requests.Request(method="GET", headers=headers, url=url)
        self.logger.debug("Request {request}".format(request=requests))
        resp = requests.session().send(request=req.prepare())
        self.logger.debug("Response {response}".format(response=resp))
        return resp.content.decode()

    def get_subscribe_uri(self, ttl="00:02:00"):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        body = {"events": ["*"], "ttl": ttl}
        req = requests.Request(method="POST", headers=headers, json=body,
                               url=self.subscribe_url)
        self.logger.debug("Request {request}".format(request=requests))
        resp = requests.session().send(request=req.prepare())
        self.logger.debug("Response {response}".format(response=resp))
        return json.loads(resp.content.decode()).get("deliveryMethod").get("uri")

    def set_presence(self, presence, hp_user_id, resource):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        body = {"presence": presence}
        url = self.user_presence_uri+hp_user_id+"?resource="+resource
        req = requests.Request(method="PUT", headers=headers, json=body, url=url)
        self.logger.debug("Request {request}".format(request=requests))
        resp = requests.session().send(request=req.prepare())
        self.logger.debug("Response {response}".format(response=resp))
        return resp.content.decode()

    def clear_presence(self, hp_user_id, resource):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        url = self.user_presence_uri+hp_user_id+"?resource="+resource
        req = requests.Request(method="DELETE", headers=headers, url=url)
        self.logger.debug("Request {request}".format(request=requests))
        resp = requests.session().send(request=req.prepare())
        self.logger.debug("Response {response}".format(response=resp))
        print(resp.content.decode())
