import requests
import json


class ExtendClient(object):

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None

    def get_access_token(self):
        if self.access_token is None:
            body = {"grant_type": "client_credentials", "client_id": self.client_id,
                    "client_secret": self.client_secret, "scope": "api.service.messaging"}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            req = requests.Request(method="POST", headers=headers, data=body,
                                   url="https://login.intermedia.net/user/connect/token")
            resp = requests.session().send(request=req.prepare())
            self.access_token = json.loads(resp.content.decode()).get("access_token")
            self.refresh_token = json.loads(resp.content.decode()).get("refresh_token")

    def refresh_access_token(self):
        raise NotImplementedError

    def get_user_presence(self, hp_user_uid):
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + self.access_token}
        url = "https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/"+hp_user_uid
        req = requests.Request(method="GET", headers=headers, url=url)
        resp = requests.session().send(request=req.prepare())
        return resp.content.decode()

    def get_subscribe_uri(self, ttl="00:02:00"):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        body = {"events": ["*"], "ttl": ttl}
        req = requests.Request(method="POST", headers=headers, json=body,
                               url="https://api.intermedia.net/messaging/v1/subscriptions/accounts/_me/users/_all")
        resp = requests.session().send(request=req.prepare())
        return json.loads(resp.content.decode()).get("deliveryMethod").get("uri")

    def set_presence(self, presence, hp_user_id, resource):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        body = {"presence": presence}
        url = "https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/"+hp_user_id+"?resource="+resource
        req = requests.Request(method="PUT", headers=headers, json=body, url=url)
        resp = requests.session().send(request=req.prepare())
        return resp.content.decode()

    def clear_presence(self, hp_user_id, resource):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.access_token}
        url = "https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/"+hp_user_id+"?resource="+resource
        req = requests.Request(method="DELETE", headers=headers, url=url)
        resp = requests.session().send(request=req.prepare())
        print(resp.content.decode())
