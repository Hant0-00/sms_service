import time

from playwright_recaptcha import recaptchav2, recaptchav3


class Bigo:
    url = "https://www.bigo.tv/en/"

    @classmethod
    def register(cls, page, fake, phone_number):
        page.goto(cls.url, wait_until="domcontentloaded")
        page.evaluate("""
            new MutationObserver((mutationsList) => {
                for (const mutation of mutationsList) {
                    if (document.querySelector('.close')) {
                        document.querySelector('.close').click();
                        console.log('Елемент .close знайдено та закрито через MutationObserver.');
                    }
                }
            }).observe(document.body, { childList: true, subtree: true });
        """)
        login_button = page.locator("//span[text()='Login']")
        login_button.click()
        time.sleep(1)
        page.click("text=Sign up now")

        page.locator(".CountrySelect-Component[data-v-f417e242][data-v-7db65f17]").click()
        page.locator("text='Ukraine'").nth(1).click()

        phone_number_field = page.locator(".phone-number-box.phone-code-box input")
        phone_number_field.fill(phone_number[1:])

        password_field = page.locator("//input[@type='password']").nth(1)
        password_field.fill(fake.password(length=15, special_chars=False, upper_case=True, lower_case=True))
        time.sleep(5)
        page.locator(".btn-send").click()

        with recaptchav3.SyncSolver(page) as solver:
            token = solver.solve_recaptcha()
            print(token)

        # with recaptchav2.SyncSolver(page) as solver:
        #     token = solver.solve_recaptcha()
        #     print(token)


        time.sleep(30)

