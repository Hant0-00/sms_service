import time

from playwright.sync_api import sync_playwright, Playwright


class MyFave:
    url = "https://myfave.com/auth/request-code?from=%2F"

    @classmethod
    def register(cls, page, fake, phone_number):

        page.goto(cls.url, wait_until="load")

        country_number = page.locator(".block.truncate")
        country_number.click()

        input_number_country = page.locator("#headlessui-combobox-input-\\:r3\\:")
        input_number_country.fill("+380")
        page.keyboard.press("Enter")

        number_from = page.locator("#\\:r0\\:-form-item")
        number_from.fill(phone_number[1:])
        submit_button = page.locator(".bg-primary.text-white")
        submit_button.click()




