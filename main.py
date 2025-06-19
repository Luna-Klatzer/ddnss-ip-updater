import asyncio
import json
import datetime
import sys
import traceback
import requests

def get_prefix():
    return f"[{datetime.datetime.now()}]"

def log(msg):
    print(f"{get_prefix()} {msg}")

def read_config():
    with open("./config.json") as config:
        data = json.loads(config.read())
        return data['USER'], data['PASS'], data['HOST']


class DDNSSIPChanger:
    async def wait_for_connection(self):
        log("Awaiting connection...")
        error = True
        url = "https://google.com"
        timeout = 5
        while error is True:
            try:
                requests.get(url, timeout=timeout)
            except (requests.ConnectionError, requests.Timeout):
                await asyncio.sleep(5)
            else:
                error = False
        log("Connection reestablished")

    async def update_ip(self, user, password, host):
        # Waits until a connection is possible
        log("Updating ip in DNS record")
        await self.wait_for_connection()
        requests.post(f"https://ddnss.de//upd.php?user={user}&pwd={password}&host={host}")
        log(f"Changed ip to {new_ip}")

    async def run(self, user, password, host):
        # On Start it will automatically update the ip
        await self.update_ip(user, password, host)

        ip = requests.get('https://api.ipify.org').text
        while True:
            try:
                new_ip = requests.get('https://api.ipify.org').text

                # ip is different and a request needs to be sent
                if new_ip != ip:
                    await self.update_ip(user, password, host)
                    ip = new_ip

                await asyncio.sleep(30)

            except (requests.ConnectionError, requests.Timeout):
                # No connection => Waits until a connection is possible again
                await self.wait_for_connection()

                # Changes the ip for security reasons!
                await self.update_ip(user, password, host)

            except Exception:
                raise


async def main():
    ip_changer = DDNSSIPChanger()
    log("Reading config")
    user, password, host = read_config()
    log("Starting process loop")
    while True:
        await ip_changer.run(user, password, host)


if __name__ == '__main__':
    log("-- Process started --")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
