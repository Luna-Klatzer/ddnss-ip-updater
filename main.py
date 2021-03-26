import asyncio
import json
import requests


def read_config():
    with open("./config.json") as config:
        data = json.loads(config.read())
        return data['USER'], data['PASS'], data['HOST']


def send_request(user, password, host):
    requests.post(f"http://ddnss.de/upd.php?user={user}&pwd={password}&host={host}")


async def process_loop():
    user, password, host = read_config()
    ip = requests.get('https://api.ipify.org').text
    while True:
        new_ip = requests.get('https://api.ipify.org').text
        # ip is different and a request needs to be sent
        if new_ip != ip:
            send_request(user, password, host)
            ip = new_ip
        await asyncio.sleep(30)


loop = asyncio.get_event_loop()
loop.run_until_complete(process_loop())
loop.run_forever()
