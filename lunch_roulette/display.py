import pyvirtualdisplay
import logging
log = logging.getLogger(__name__)

"""
Display
~~~~~~~~~~~~~~~~~~~~~
Display is a class used to initiate and use virtual display. Usage:

   >>> from com.taykey.framework import Display
   >>> d = Display() # init and start display
   >>> d.start_display() # start display
   >>> d.stop_display() # stop display

"""

class Display(object):
	def __init__(self):
		self.display = pyvirtualdisplay.Display(visible=0, size=(800, 600))
		self.start_display()

	def start_display(self):
		self.display.start()
	
	def stop_display(self):
		'''display.stop() closes the virtual display'''
		if self.display.is_alive():
			try:
				self.display.stop()
			except Exception as e:
				log.error("error stopping display, reason: " + str(e))
				
