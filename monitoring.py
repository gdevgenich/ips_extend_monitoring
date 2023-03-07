import requests
import json
from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import time


body = {"grant_type": "client_credentials", "client_id": "r6mwnN2x0KchOOj1MCsg",
           "client_secret": "lwITu1LqRF0DNIEmUhwRFrRmPNRukkToLmp8mmw8ZrU", "scope": "api.service.messaging"}
headers = {"Content-Type": "application/x-www-form-urlencoded"}
req = requests.Request(method="POST", headers=headers, data=body, url="https://login.intermedia.net/user/connect/token")

resp = requests.session().send(request=req.prepare())
print(resp.content.decode())
access_token = json.loads(resp.content.decode()).get("access_token")
print(access_token)


headers = {"Content-Type": "application/x-www-form-urlencoded" , "Authorization": "Bearer "+access_token}
req = requests.Request(method="GET", headers=headers,
                       url="https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/e76da5b1-f534-4c06-b3ac-984df0d2498e")
resp = requests.session().send(request=req.prepare())
print(resp.content.decode())

headers = {"Content-Type": "application/json", "Authorization": "Bearer "+access_token}
body = {"events": ["*"], "ttl": "00:02:00"}
req = requests.Request(method="POST", headers=headers, json=body,
                       url="https://api.intermedia.net/messaging/v1/subscriptions/accounts/_me/users/_all")
resp = requests.session().send(request=req.prepare())
print(resp.content.decode())
uri = json.loads(resp.content.decode()).get("deliveryMethod").get("uri")
uri_id = json.loads(resp.content.decode()).get("id")
print(uri, uri_id)

def login_function():
    return access_token

hub_connection = HubConnectionBuilder()\
            .with_url(uri,
            options={
                "access_token_factory": login_function,
            })\
            .configure_logging(logging.DEBUG, handler=logging.StreamHandler())\
            .with_automatic_reconnect({
                "type": "raw",
                "keep_alive_interval": 10,
                "reconnect_interval": 5,
                "max_attempts": 5
            }).build()

hub_connection.start()
hub_connection.on_close(lambda: hub_connection.start())
time.sleep(10)
print(1)
time.sleep(10)

headers = {"Content-Type": "application/json", "Authorization": "Bearer "+access_token}
body = {"presence": "onphone"}
req = requests.Request(method="PUT", headers=headers, json=body,
                       url="https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/e76da5b1-f534-4c06-b3ac-984df0d2498e?resource=92cefb52-27fd-4c33-8a65-450723391fd6")
resp = requests.session().send(request=req.prepare())
print(resp.content.decode())

headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer "+access_token}
req = requests.Request(method="GET", headers=headers,
                       url="https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/e76da5b1-f534-4c06-b3ac-984df0d2498e")
resp = requests.session().send(request=req.prepare())
print(resp.content.decode())

headers = {"Content-Type": "application/json", "Authorization": "Bearer "+access_token}
req = requests.Request(method="DELETE", headers=headers,
                       url="https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/e76da5b1-f534-4c06-b3ac-984df0d2498e?resource=92cefb52-27fd-4c33-8a65-450723391fd6")
resp = requests.session().send(request=req.prepare())
print(resp.content.decode())

headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Bearer "+access_token}
req = requests.Request(method="GET", headers=headers,
                       url="https://api.intermedia.net/messaging/v1/presence/accounts/_me/users/e76da5b1-f534-4c06-b3ac-984df0d2498e")
resp = requests.session().send(request=req.prepare())
print(resp.content.decode())