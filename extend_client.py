import requests
import json
import logging


class ExtendClient(object):

    def __init__(self, client_id, client_secret, token_url, user_presence_uri, subscribe_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.logger = logging.getLogger("extend_client")
        self.token_url = token_url
        self.user_presence_uri = user_presence_uri
        self.subscribe_url = subscribe_url

    def get_access_token(self):
        if self.access_token is None:
            body = {"grant_type": "client_credentials", "client_id": self.client_id,
                    "client_secret": self.client_secret, "scope": "api.service.messaging"}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            req = requests.Request(method="POST", headers=headers, data=body, url=self.token_url)
            self.logger.debug(msg=f"SEND URL {req.url}")
            self.logger.debug(msg=f"SEND body {req.json}")
            resp = requests.session().send(request=req.prepare())
            self.logger.debug(msg=f"RECV {resp.content.decode()}")
            self.access_token = json.loads(resp.content.decode()).get("access_token")
            self.refresh_token = json.loads(resp.content.decode()).get("refresh_token")
        return self.access_token

    def refresh_access_token(self):
        raise NotImplementedError

    def get_user_presence(self, hp_user_uid):
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + self.access_token}
        url = self.user_presence_uri+hp_user_uid
        req = requests.Request(method="GET", headers=headers, url=url)
        self.logger.debug(msg=f"SEND URL {req.url}")
        resp = requests.session().send(request=req.prepare())
        self.logger.debug(msg=f"RECV HEADERS {resp.headers}")
        self.logger.debug(msg=f"RECV {resp.content.decode()}")
        return resp.content.decode()

    def get_subscribe_uri(self, ttl="00:02:00"):
        if self.access_token is None:
            raise RuntimeError("Failed to obtain access token")
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        body = {"events": ["*"], "ttl": ttl}
        req = requests.Request(method="POST", headers=headers, json=body,
                               url=self.subscribe_url)
        self.logger.debug(msg=f"SEND URL {req.url}")
        self.logger.debug(msg=f"SEND body {req.json}")
        resp = requests.session().send(request=req.prepare())
        self.logger.debug(msg=f"RECV HEADERS {resp.headers}")
        self.logger.debug(msg=f"RECV {resp.content.decode()}")
        return json.loads(resp.content.decode()).get("deliveryMethod").get("uri")

    def set_presence(self, presence, hp_user_uid, resource):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        body = {"presence": presence}
        url = self.user_presence_uri+hp_user_uid+"?resource="+resource
        req = requests.Request(method="PUT", headers=headers, json=body, url=url)
        self.logger.debug(msg=f"SEND URL {req.url}")
        self.logger.debug(msg=f"SEND body {req.json}")
        resp = requests.session().send(request=req.prepare())
        self.logger.debug(msg=f"RECV HEADERS {resp.headers}")
        self.logger.debug(msg=f"RECV {resp.content.decode()}")
        return resp.content.decode()

    def clear_presence(self, hp_user_uid, resource):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        url = self.user_presence_uri+hp_user_uid+"?resource="+resource
        req = requests.Request(method="DELETE", headers=headers, url=url)
        self.logger.debug(msg=f"SEND URL {req.url}")
        resp = requests.session().send(request=req.prepare())
        self.logger.debug(msg=f"RECV HEADERS {resp.headers}")
        self.logger.debug(msg=f"RECV {resp.content.decode()}")
        return resp.content.decode()
