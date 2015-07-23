import logging
from browser import TenBisBrowser
from selenium.webdriver.common.by import By
from utils import wait_for_element
import time

from logging.config import dictConfig
from conf.logging_conf import LOGGING_CONF

dictConfig(LOGGING_CONF)
log = logging.getLogger(__name__)
rest_url_template = 'https://www.10bis.co.il/Restaurants/Menu/Delivery?ResId=%s&couponValue=0'


def give_master_permissions(mail, password, master_user):
    with TenBisBrowser(implicitly_wait_seconds=7, is_visible=True, is_profile_dir=True, downloaded_data_dir=None) as browser:
        browser.get_browser().get("https://www.10bis.co.il/Account/UserAccountManagement")
        email_xpath = '/html/body/div[2]/table/tbody/tr/td/div/table/tbody/tr[3]/td[1]/div/div[3]/div/div[2]/div[1]/div[2]/input'
        wait_for_element(browser, email_xpath, By.XPATH)
        elem = browser.get_browser().find_element_by_xpath(email_xpath)
        elem.clear()
        elem.send_keys(mail)
        elem = browser.get_browser().find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td/div/table/tbody/tr[3]/td[1]/div/div[3]/div/div[2]/div[2]/div[2]/input')
        elem.clear()
        elem.send_keys(password)
        enter = '/html/body/div[2]/table/tbody/tr/td/div/table/tbody/tr[3]/td[1]/div/div[3]/div/div[2]/div[4]'
        browser.get_browser().find_element_by_xpath(enter).click()
        id_xpath = '/html/body/div[2]/table/tbody/tr/td/div/div'
        wait_for_element(browser, id_xpath, By.XPATH)
        user_id = browser.get_browser().find_element_by_xpath(id_xpath).get_attribute('data-account-user-id')
        try:
            card = '/html/body/div[2]/table/tbody/tr/td/div/div/div[1]/div/div[1]'
            wait_for_element(browser, card, By.XPATH, timeout=4)
            browser.get_browser().find_element_by_xpath(card).click()
        except Exception:
            pass
        browser.get_browser().find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td/div/div/div[2]/div[1]/div[1]/table/tbody/tr[2]/td[2]/table/tbody/tr[7]/td[2]/div').click()
        user = '//*[@id="userMcLinksInterfaceDiv"]/div/table[2]/tfoot/tr[2]/td[2]/input'
        wait_for_element(browser, user, By.XPATH)
        elem = browser.get_browser().find_element_by_xpath(user)
        elem.clear()
        elem.send_keys(master_user)
        time.sleep(3)
        browser.get_browser().find_element_by_xpath('//*[@id="userMcLinksInterfaceDiv"]/div/table[2]/tfoot/tr[2]/td[1]/div').click()
        log.debug("user id: %s" % user_id)
        return user_id


def order_meal(mail, password, restaurant_id, dish_id, loosers_ids):
    with TenBisBrowser(implicitly_wait_seconds=7, is_visible=True, is_profile_dir=True, downloaded_data_dir=None) as browser:
        browser.get_browser().get(rest_url_template % restaurant_id)
        signed_user = '//*[@id="LogOnPopupAnchor"]'
        wait_for_element(browser, signed_user, locator_type=By.XPATH)
        browser.get_browser().find_element_by_xpath(signed_user).click()
        email_xpth ='//*[@id="LogonPopupPartialView"]/div/div/div[4]/div[1]/div[2]/input'
        wait_for_element(browser, email_xpth, locator_type=By.XPATH)
        elem = browser.get_browser().find_element_by_xpath(email_xpth)
        elem.clear()
        elem.send_keys(mail)
        elem = browser.get_browser().find_element_by_xpath('//*[@id="LogonPopupPartialView"]/div/div/div[4]/div[2]/div[2]/input')
        elem.clear()
        elem.send_keys(password)
        time.sleep(3)
        browser.get_browser().find_element_by_xpath('//*[@id="LogonPopupPartialView"]/div/div/div[4]/div[4]').click()
        address = '//*[@id="chooseAddressListForm"]/div/table[1]/tbody/tr[1]/td[3]/div/span'
        wait_for_element(browser, address, locator_type=By.XPATH)
        time.sleep(2)
        browser.get_browser().find_element_by_xpath(address).click()
        dish_list = '//*[@id="myTabs"]/div[1]/div[1]/div/div[2]'
        wait_for_element(browser, dish_list, locator_type=By.XPATH)
        time.sleep(1)
        dishes =  browser.get_browser().find_element_by_xpath(dish_list).find_elements_by_xpath('//div[contains(@class,"dishesBox")]')
        for dish in dishes:
            if dish.get_attribute("data-dishid") == dish_id:
                dish.click()
                break
        else:
            raise Exception("did not find dish id %s" % dish_id)

        users = '//*[@id="dishContent"]/table/thead/tr/td[2]/div[3]'
        wait_for_element(browser, users, locator_type=By.XPATH)
        all_users = browser.get_browser().find_element_by_xpath('//*[@id="dishContent"]/table/thead/tr/td[2]/div[3]').find_elements_by_xpath("//select")[3].find_elements_by_tag_name("option")
        for user in all_users:
            if user.get_attribute("value") == loosers_ids[0]:
                user.click()
                break
        browser.get_browser().find_element_by_xpath('//*[@id="dishContent"]/table/tfoot/tr[3]/td/div[1]').click()
        shoppingCartBottom = '//*[@id="shoppingCartBottom"]/td/div'
        wait_for_element(browser, shoppingCartBottom, locator_type=By.XPATH)
        browser.get_browser().find_element_by_xpath(shoppingCartBottom).click()
        confirm = '//*[@id="orderConfirmationBtn"]'
        wait_for_element(browser, confirm, locator_type=By.XPATH)
        browser.get_browser().find_element_by_xpath(confirm).click()

        # TODO: add other payments
        # add_payment = '//*[@id="checkOutPaymentList"]/div[2]/div[1]/table/tbody/tr[3]/td/div[2]/div[2]'
        # wait_for_element(browser, add_payment, locator_type=By.XPATH)
        # browser.get_browser().find_element_by_xpath(add_payment).click()
        # payers_list = '//*[@id="unassignedPaymentsList"]/table/tbody/tr/td/div/table'
        # all_users = browser.get_browser().find_element_by_xpath('//*[@id="unassignedPaymentsList"]/table/tbody/tr/td/div/table').find_elements_by_xpath("//select")[3].find_elements_by_tag_name("option")


        # # ********************** PAY *******************
        # confirm = '//*[@id="checkOutPaymentList"]/div[2]/div[2]/div[5]/div/div/div'
        # wait_for_element(browser, confirm, locator_type=By.XPATH)
        # browser.get_browser().find_element_by_xpath(confirm).click()


# give_master_permissions("idit@taykey.com", "hackathon2015", "udy@taykey.com")
# send_meal("idit@taykey.com", "hackathon2015", "12009", "696235", ["829477"])
# ("idit@taykey.com", "hackathon2015", "562", "533298", ["829477"])


