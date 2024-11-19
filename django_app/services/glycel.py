import time


class Glycel:
    url = "https://www.glycel.com/tc/my-account/"

    @classmethod
    def register(cls, page, fake, phone_number, ):

        page.goto(cls.url, wait_until="load")

        first_name_field = page.locator("#reg_billing_first_name")
        first_name_field.fill(fake.first_name())

        last_name_field = page.locator("#reg_billing_last_name")
        last_name_field.fill(fake.last_name())

        date_field = page.locator("#billing_birthday")
        date_field.fill(fake.date())

        region_select = page.select_option("#reg_telprefix", index=1)

        phone_number_field = page.locator("#reg_billing_phone")
        phone_number_field.fill(f"+380{phone_number}")

        confirm_phone_number_field = page.locator("#reg_billing_phone2")
        confirm_phone_number_field.fill(f"+380{phone_number}")

        email_field = page.locator("#reg_email")
        email_field.fill(fake.email())

        password_field = page.locator("#reg_password")
        password_field.fill(fake.password())

        submit_button = page.locator("(//button[@type='submit'])[2]")
        submit_button.click()

        time.sleep(10)
