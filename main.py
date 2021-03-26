import asyncio
import json
import datetime
import requests


def read_config():
    with open("/usr/share/ddnss-ip-updater/config.json") as config:
        data = json.loads(config.read())
        print(f"User: {data['USER']}\nPassword: {data['PASS']}\nHost: {data['HOST']}\n")
        return data['USER'], data['PASS'], data['HOST']


async def send_request(user, password, host):
    try:
        requests.post(f"http://ddnss.de/upd.php?user={user}&pwd={password}&host={host}")
    except (requests.exceptions.ConnectionError, ConnectionError):
        print("No connection available! Waiting for connection")
        await asyncio.sleep(20)

        error = True
        while error:
            try:
                requests.post(f"http://ddnss.de/upd.php?user={user}&pwd={password}&host={host}")
            except (requests.exceptions.ConnectionError, ConnectionError):
                await asyncio.sleep(5)
            except Exception:
                raise
            else:
                # It works again
                error = False
        return
    except Exception:
        raise


async def process_loop():
    print(f"Process started at {datetime.datetime.now()}")
    user, password, host = read_config()

    ip = None
    error = True
    while error:
        try:
            ip = requests.get('https://api.ipify.org').text
        except (requests.exceptions.ConnectionError, ConnectionError):
            await asyncio.sleep(5)
        except Exception:
            raise
        else:
            error = False

    while True:
        new_ip = requests.get('https://api.ipify.org').text
        # ip is different and a request needs to be sent
        if new_ip != ip:
            await send_request(user, password, host)
            print(f"Changed ip to {new_ip}")
            ip = new_ip
        print("IP does not require updating! Sleeping for 30s")
        await asyncio.sleep(30)


loop = asyncio.get_event_loop()
loop.run_until_complete(process_loop())
loop.run_forever()
