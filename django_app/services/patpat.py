import time


class Patpat:
    url = "https://www.patpat.com/de-de/account/login"

    @classmethod
    def register(cls, page, fake, number):
        page.goto(cls.url, wait_until="load")

        input_element = page.locator('[name="patpat-base-input-7306"]')

        # Примусове встановлення значення через JavaScript
        page.evaluate("document.querySelector('[name=\"patpat-base-input-7306\"]').value = 'test@example.com'")

        submit_button = page.locator(".pat-button.submit-btn.form-submit.patpat-SemiBold.pat-button.pat-button--black."
                                     "pat-button--large")
        submit_button.click()

        time.sleep(10)
