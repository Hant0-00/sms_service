import time

from asgiref.timeout import timeout


class Hllucky:
    url = "https://hllucky99.com/vn"

    @classmethod
    def register(cls, page, fake, phone_number):
        page.goto(cls.url, wait_until="domcontentloaded")

        username_field = page.locator("//input[@autocomplete='username']")

        cls.click_with_retry(page, username_field)

        username_field.fill(fake.user_name())

        page.locator(".flex.flex-col.justify-center.h-full").click()

        page.locator("text='+380'").click()

        phone_field = page.locator("//input[@autocomplete='phone']")
        phone_field.fill(phone_number)

        password = fake.password()
        password_field = page.locator("//span[text()='Mật khẩu ']/preceding-sibling::input")
        password_field.fill(password)

        reset_password_field = page.locator("//span[text()='Xác nhận mật khẩu ']/preceding-sibling::input")
        reset_password_field.fill(password)

        adulthood_field = page.locator("//div[contains(@class, 'clickable') and contains(@class, 'relative') and contains(@class, 'h-[20px]') and contains(@class, 'w-[20px]')]")
        adulthood_field.nth(0).click()

        page.locator("//span[text()='Bước kế tiếp']").click()
        register_complete = page.locator(".font-bold.text-2xl")
        register_complete.wait_for(timeout=5000)
        if register_complete.is_visible():
            return "Register complete"
        else:
            return "Register failed"

    @staticmethod
    def click_with_retry(page, username_field):
        while not username_field.is_visible():
            register_button = page.locator(".clickable.whitespace-nowrap")
            register_button.click(force=True)
            time.sleep(1)