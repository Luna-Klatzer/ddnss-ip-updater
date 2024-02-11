import asyncio
import json
import datetime
import sys
import traceback

import discord
import discord.ext.commands
import requests


def read_config():
    with open("/usr/share/ddnss-ip-updater/config.json") as config:
        data = json.loads(config.read())
        print(f"User: {data['USER']}\nPassword: {data['PASS']}\nHost: {data['HOST']}\n")
        return data['USER'], data['PASS'], data['HOST'], data['TOKEN']


class DDNSSIPChanger:
    async def wait_for_connection(self):
        error = True
        url = "http://google.com"
        timeout = 5
        while error is True:
            try:
                requests.get(url, timeout=timeout)
            except (requests.ConnectionError, requests.Timeout):
                await asyncio.sleep(5)
            else:
                error = False

    async def update_ip(self, user, password, host):
        # Waits until a connection is possible
        await self.wait_for_connection()
        requests.post(f"http://ddnss.de/upd.php?user={user}&pwd={password}&host={host}")

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
                    print(f"Changed ip to {new_ip}")
                    ip = new_ip

                await asyncio.sleep(10)

            except (requests.ConnectionError, requests.Timeout):
                # No connection => Waits until a connection is possible again
                await self.wait_for_connection()

                # Changes the ip for security reasons!
                await self.update_ip(user, password, host)

            except Exception:
                raise


async def main():
    ip_changer = DDNSSIPChanger()

    print(f"Process started at {datetime.datetime.now()}")
    user, password, host, bot_token = read_config()

    intents = discord.Intents.all()
    client = discord.ext.commands.Bot(".", intents=intents)

    while True:
        try:
            await ip_changer.run(user, password, host)
        except Exception as e:
            exception = sys.exc_info()[0].__name__
            tb = traceback.format_tb(sys.exc_info()[2])
            tb_str = "".join(frame for frame in tb)

            @client.event
            async def on_ready():
                guild = client.get_guild(702222354037735476)
                await guild.get_member(376406094639267862).send(
                    f"Failed due to exception: ```py\n{tb_str}\n{exception}: {e}\n```"
                )
                await client.close()

            await client.login(token=bot_token)
            await client.connect(reconnect=True)
            await asyncio.sleep(10)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
