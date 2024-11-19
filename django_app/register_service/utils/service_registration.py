import random
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time_ns

from faker import Faker
from playwright.sync_api import sync_playwright

from django_app.register_service.utils.config_reg import CONFIGS
from register_service.utils.utils import generate_numbers, generate_proxy
from django_app.register_service.utils.user_agents import USER_AGENTS


def register_service(conf, fake, phone_number):
    with sync_playwright() as p:
        chromium = p.chromium
        # proxy_data = random.choice(generate_proxy())
        # proxy = {
        #     "server": f"http://{proxy_data['ip']}:{proxy_data['port_socks5']}",
        #     "username": proxy_data["username"],
        #     "password": proxy_data["password"]
        # }
        # print(proxy)
        # time.sleep(100)
        browser = chromium.launch(headless=False)
        if conf.get("user-agent", True):
            context = browser.new_context(user_agent=random.choice(USER_AGENTS))
        else:
            context = browser.new_context()
        page = context.new_page()

        try:
            code = conf["code"]
            info = code().register(page, fake, phone_number)
        except Exception as e:
            print(f"Error in register_service: {e}")
            info = None
        finally:
            context.close()
            browser.close()

    return info


def worker(conf, number):
    fake = Faker()

    try:
        return register_service(conf,  fake, number)
    except Exception as e:
        print(f"Error worker: {e}")
        return None


def run_registration():
    numbers = generate_numbers()
    futures = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        for conf in CONFIGS:
            for number in numbers:
                future = executor.submit(worker, conf=conf, number=number)
                futures.append(future)

        for future in as_completed(futures):
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Error: {e}")


# def main_test():
#     numbers = generate_numbers()
#     futures = []
#     worker(CONFIGS[0], "0993971241")
#
#
# main_test()



