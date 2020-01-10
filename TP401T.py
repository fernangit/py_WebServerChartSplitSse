import threading
import time
from MCP3424 import MCP3424

class TP401T(MCP3424):
	
	WAITING = -1	# 測定開始待ち
	NORMAL  = 0		# 空気に問題はない
	ALERT   = 1		# 汚染されている
	WARNING = 2		# 汚染されているが減少中
	
	term = False
	__current_state = -1
	
	def __init__(self, ch = 0):
		super().__init__()
		self.tp401_ch = ch
		self.term = False
		self.prev_value = self.getVoltage(self.tp401_ch)
		self.normal_value = self.prev_value
	
	def start(self):
		self.worker = threading.Thread(target=self.__measure)
		self.term = False
		self.worker.start()
	
	def stop(self):
		self.term = True
		self.worker.join()
	
	def __sleep(self, sec):
		for i in range(sec * 100):
			if self.term == True:
				return False
			time.sleep(1/100)
		
		return True
		
	def __measure(self):
		self.__current_state = self.WAITING
		
		sum = 0.0
		for i in range(10):
			sum += self.getVoltage(self.tp401_ch)
			if self.__sleep(3) == False:
				return
		# 30秒間の平均値を平時の値として採用する
		self.normal_value = sum / 10
		self.prev_value = self.normal_value
		self.__current_state = self.NORMAL
		
		while self.__sleep(3):
			value = self.getVoltage(self.tp401_ch)
			if value < self.normal_value * 1.5:
				self.__current_state = self.NORMAL
			else:
				if (self.prev_value - value) < 0:	# 汚染が増加中
					self.__current_state = self.ALERT
				else:
					self.__current_state = self.WARNING
			
			self.prev_value = value
	
	@property
	def state(self):
		return self.__current_state
	
	def __del__(self):
		self.term = True
