import asyncio
import json
import datetime
import logging
import sys
import traceback
import requests


class LogFilter(logging.Filter):
    # https://stackoverflow.com/a/24956305/408556
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        # "<" instead of "<=": since logger.setLevel is inclusive, this should be exclusive
        return record.levelno < self.level


MIN_LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(MIN_LEVEL)

stdout_hdlr = logging.StreamHandler(sys.stdout)
stderr_hdlr = logging.StreamHandler(sys.stderr)
log_filter = LogFilter(logging.WARNING)
stdout_hdlr.addFilter(log_filter)
stdout_hdlr.setLevel(MIN_LEVEL)
stderr_hdlr.setLevel(max(MIN_LEVEL, logging.WARNING))

formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
stdout_hdlr.setFormatter(formatter)
stderr_hdlr.setFormatter(formatter)

logger.addHandler(stdout_hdlr)
logger.addHandler(stderr_hdlr)

file_handler = logging.FileHandler('main.log')
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


def read_config():
    with open("./config.json") as config:
        data = json.loads(config.read())
        return data['KEY'], data['HOST']


class DDNSSIPChanger:
    def sync_get_curr_ip(self):
        return requests.get('https://api.ipify.org').text

    async def wait_for_connection(self):
        logger.debug("Awaiting reconnection...")
        error = True
        url = "https://ddnss.de"
        timeout = 5
        while error is True:
            try:
                r = requests.get(url, timeout=timeout)
                r.raise_for_status()
            except (requests.ConnectionError, requests.Timeout):
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Encountered invalid response or critical error:\n{e}")
            else:
                error = False
        logger.debug("Connection reestablished")

    async def update_ip(self, key, host):
        try:
            # Waits until a connection is possible
            logger.info("Attempting to update ip in DNS record")

            new_ip = self.sync_get_curr_ip()
            r = requests.post(f"https://ddnss.de/upd.php?key={key}&host={host}&ip={new_ip}")
            r.raise_for_status()

            logger.debug(f"Received response: {r.text}")
            logger.info(f"Successfully changed ip to {new_ip}")
        except (requests.ConnectionError, requests.Timeout):
            logger.error("Failed to perform request... no internet or server down")

            # No connection => Waits until a connection is possible again
            await self.wait_for_connection()

            # Change the ip immediately to recover from potential DNS ip mismatch
            await self.update_ip(key, host)

            logger.info("Successfully recovered from error")
        except Exception as e:
            logger.critical("Failed to perform request due to unknown error:\n{e}")
            raise

    async def run(self, key, host):
        ip = self.sync_get_curr_ip()
        logger.info(f"Starting with ip {ip}")

        # On start it will automatically update the ip
        await self.update_ip(key, host)

        while True:
            new_ip = self.sync_get_curr_ip()

            # ip is different and a request needs to be sent
            if new_ip != ip:
                await self.update_ip(key, host)
                ip = new_ip

            logger.debug("Sleeping until next cycle")
            await asyncio.sleep(60)


async def main():
    ip_changer = DDNSSIPChanger()
    logger.info("Reading config")
    key, host = read_config()
    logger.info("Starting process loop")
    while True:
        await ip_changer.run(key, host)


if __name__ == '__main__':
    logger.info("-- Process started --")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
