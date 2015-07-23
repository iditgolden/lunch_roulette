from selenium import webdriver
from display import Display
from os.path import join
from datetime import datetime
import logging
log = logging.getLogger(__name__)

"""
Browser
~~~~~~~~~~~~~~~~~~~~~

Browser is a class used to initiate and use Selenium Firefox web driver
over virtual display. Usage:

   >>> from com.taykey.framework import Browser
   >>> bro = Browser()
   >>> bro.get_browser()
   <selenium.webdriver.firefox.webdriver.WebDriver object at 0x28ea050>
   >>> do other things with bro
   >>> bro.close()
   
Or:
	>>> from com.taykey.framework import Browser
	>>> with Browser() as bro:
	>>> 	do things with bro
   
The user can also start (start_browser()) and close (close_browser()) multiple times.  

Init options:
 - downloaded_data_dir (string, default=None) - set a profile to the Firefox web driver,
	which can save file in the background to the specified directory
 - implicitly_wait_seconds (int, default=10) - sets a sticky timeout to implicitly wait for an element to be found
 - is_visible (boolean, default=False) - allow visible browser
 - profile_directory (string, default=None) - if profile_directory is passed then a copy of this directory is created
        in /tmp by the FirefoxProfile and all the changed for this profile are made under the temporary directory.
		Otherwise, a new profile will be created in /tmp.

"""

class Browser(object):
	display = None
	browser = None

	def __init__(self, downloaded_data_dir=None, implicitly_wait_seconds=10, is_visible=False, profile_directory=None):
		if not is_visible:
			self.display = Display()
		self.downloaded_data_dir = downloaded_data_dir
		self.start_browser(downloaded_data_dir, implicitly_wait_seconds, profile_directory)

	def __enter__(self):
		return self

	def __exit__(self, type, value, trace):
		if type and self.downloaded_data_dir:
			try:
				save_to = join(self.downloaded_data_dir, 'error_screenshot_' + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
				self.browser.save_screenshot(save_to)
			except:
				pass
		self.close()

	def start_browser(self, downloaded_data_dir=None, implicitly_wait_seconds=10, profile_directory=None):
		profile = webdriver.FirefoxProfile(profile_directory)
		if downloaded_data_dir:
			'''start browser with profile'''
			profile.set_preference("browser.download.folderList", 2)
			profile.set_preference("browser.download.manager.showWhenStarting", False)
			profile.set_preference("browser.download.dir", downloaded_data_dir)
			profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/csv,text/csv")
			profile.set_preference("browser.download.manager.scanWhenDone", False)
			profile.set_preference("browser.download.manager.showAlertOnComplete", True)
			profile.set_preference("browser.download.manager.useWindow", False)
			profile.set_preference("browser.helperApps.alwaysAsk.force", False)

		self.browser = webdriver.Firefox(firefox_profile=profile)
		self.browser.implicitly_wait(implicitly_wait_seconds)

	def get_browser(self):
		if self.browser:
			return self.browser
		raise Exception("browser don't exist")

	def close_browser(self):
		'''browser.quit() closes the browser & deleted the temp files'''
		if self.browser:
			try:
				self.browser.quit()
			except Exception as e:
				log.error("error closing browser, reason: " + str(e))
			self.browser = None

	def close(self):
		self.close_browser()
		if self.display:
			self.display.stop_display()
