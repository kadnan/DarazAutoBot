from scrapingbee import ScrapingBeeClient
from dotenv import load_dotenv
import os, json, base64


def buy_item(cookies_string):
    order_number = ''
    buy_now_button = 'button[class="add-to-cart-buy-now-btn"]'
    buy_now_button = '.add-to-cart-buy-now-btn'
    process_buy = '.checkout-order-total-button'
    cod_method = '#automation-payment-method-item-122'
    place_order = '.btn-place-order'

    response = client.get(
        PRODUCT_URL,
        params={
            'extract_rules': {"order_number": ".thank-you-order-number"},
            'screenshot': True,
            'json_response': True,
            'session_id': SESSION_ID,
            "wait": 6000,
            "cookies": cookies_string,
            'js_scenario': {"instructions": [
                {"wait_for": buy_now_button},
                {"click": buy_now_button},
                {"wait_for": process_buy},
                {"click": process_buy},
                {"wait": 1000},
                {"wait_for": cod_method},
                {"click": cod_method},
                {"wait_for": place_order},
                {"click": place_order},
                {"wait": 8000},
            ]
            },
        }
    )

    if response.ok:
        d = json.loads(response.content)
        order_number = d['body']
        order_number = d['body']['order_number']
        print(order_number)
        with open("screenshot_product_final.png", "wb") as f:
            f.write(base64.b64decode(d["screenshot"]))
            print('Order screenshot generated with the name: screenshot_product_final.png')
    else:
        print('Response HTTP Status Code: ', response.status_code)
        print('DATA: ', response.content)

    return order_number


def login():
    cookie_string = ''
    email_selector = 'input[data-meta="Field"][type="text"]'
    password_selector = 'input[data-meta="Field"][type="password"]'
    button_selector = 'button[type="submit"]'

    response = client.get(
        LOGIN_URL,
        params={
            'screenshot': True,
            'json_response': True,
            'session_id': SESSION_ID,
            'js_scenario': {"instructions": [
                {"wait_for": email_selector},
                {"fill": [email_selector, EMAIL]},
                {"fill": [password_selector, PASSWORD]},
                {"click": button_selector},
                {"wait": 9000}
            ]
            },
        }
    )
    if not response.ok:
        print("Login request has failed, please try again")
        print('Response HTTP Status Code: ', response.status_code)
        print('Response Content: ', response.content)
        return False, cookie_string

    data = response.json()

    cookies = data['cookies']
    cookies_to_send = dict()
    for cookie in cookies:
        if cookie['name'] in ["lzd_b_csg", "_tb_token_", "lzd_sid"]:
            cookies_to_send[cookie['name']] = cookie['value']

    # Certain Login cookies required
    if len(cookies_to_send) < 1:
        print("The cookies lzd_b_csg, _tb_token_ and lzd_sid were not found, please try again")
        exit()

    for key in cookies_to_send:
        cookie_string += "{}={},domain=.daraz.pk;".format(key, cookies_to_send[key])

    cookie_string = cookie_string.rstrip(';')
    with open("login_screen_final.png", "wb") as f:
        f.write(base64.b64decode(data["screenshot"]))
        print('Login screenshot generated with the name: login_screen_final.png')
    return True, cookie_string


if __name__ == '__main__':
    load_dotenv()
    EMAIL = os.environ.get('EMAIL')
    PASSWORD = os.environ.get('PASSWORD')
    API_KEY = os.environ.get('API_KEY')
    SESSION_ID = 123456  # To keep the IP Same during the transitions.
    LOGIN_URL = 'https://member.daraz.pk/user/login'
    PRODUCT_URL = 'https://www.daraz.pk/products/fridge-toy-for-girls-kitchen-toy-set-for-kids-fridge-with-fridge-accessories-toy-for-girls-i152820734-s1317422364.html'

    client = ScrapingBeeClient(api_key=API_KEY)
    print('Logging as user..')
    is_logged_in, cookie = login()
    if not is_logged_in:
        print('Unable to log in')
        exit()

    if is_logged_in:
        print('Buying Item..')
        order_number = buy_item(cookie)
        if order_number != '':
            print('Item bought successfully with the order number:- {}'.format(order_number))
        else:
            print('Something went wrong. The item was not purchased.')
