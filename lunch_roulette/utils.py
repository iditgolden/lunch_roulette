import random
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_element(browser, element, locator_type, expected_cond=EC.element_to_be_clickable, timeout=20):
    try:
        WebDriverWait(browser.get_browser(), timeout).until(expected_cond((locator_type, element)))
    except Exception:
        raise TimeoutException("Timeout Exception. element: %s. locator type: %s" % (element, locator_type))



def random_sleep(millies=1000, interval_millies=200):
    sleeping = millies + random.randint(-interval_millies, interval_millies)
    time.sleep(sleeping / 1000.0)