import base64

from icecream import ic
from requests import request

code = "7549971"
url = f"https://oauth.yandex.ru/token"


client_id = "af20c4eb971f409eab78fd72cc6274b6"
client_secret = "c9549ad8a20a4dd5810a5f2f3d68c6c8"
secret = base64.b64decode(f"{client_id}:{client_secret}")

header_value = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
headers = {"Authorization": f"Basic {header_value}"}
data = {
    "grant_type": "refresh_token",
    "refresh_token": "1:5MPKTmi184UN9_AQ:S6okUGG8TI8hYkSyccGeOo2Knh5Yyz_4GduHWqGoOkeu0J59-7vT_oGvJrEPfnlGCEpJrNmmMIujgA:inXDgk4q8ADE6UFA1RymiA",
}

resp = request(method="POST", url=url, data=data, headers=headers)
if resp.status_code == 200:
    ic(resp.json())
else:
    ic(resp.text)

"https://yandex.ru/dev/disk/doc/ru/concepts/quickstart#quickstart__oauth"
"https://oauth.yandex.ru/authorize?response_type=code&client_id=af20c4eb971f409eab78fd72cc6274b6"
"refresh_token': '1:5MPKTmi184UN9_AQ:S6okUGG8TI8hYkSyccGeOo2Knh5Yyz_4GduHWqGoOkeu0J59-7vT_oGvJrEPfnlGCEpJrNmmMIujgA:inXDgk4q8ADE6UFA1RymiA"

a = {
    "access_token": "y0_AgAAAAABo1wMAAsTvgAAAAD3AGxAgdTeBafNQVmF-8JM3lycdXRhpE8",
    "expires_in": 28572705,
    "refresh_token": "1:5MPKTmi184UN9_AQ:S6okUGG8TI8hYkSyccGeOo2Knh5Yyz_4GduHWqGoOkeu0J59-7vT_oGvJrEPfnlGCEpJrNmmMIujgA:inXDgk4q8ADE6UFA1RymiA",
    "token_type": "bearer",
}
