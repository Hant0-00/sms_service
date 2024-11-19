import time


class Iherb:
    url = "https://checkout1.iherb.com/auth/ui/account/login?correlationId=b7321470a46f5a254c364cab630e59c4"

    @classmethod
    def register(cls, page, fake, phone_number):
        page.goto(cls.url, wait_until="domcontentloaded")
        time.sleep(2)
        text = page.evaluate("document.querySelector('p').innerText")
        if 'Press & Hold' in text:
            press_hold = page.locator("p")
        print(press_hold)
        box = press_hold.bounding_box()
        print(box)
        if box:
            if box:
                page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)  # Перемістити курсор
                page.mouse.down()  # Натиснути кнопку
                time.sleep(7)  # Утримувати протягом 2 секунд
                page.mouse.up()

        select_code_country = page.select_option("select.select-country-code", value="UA")