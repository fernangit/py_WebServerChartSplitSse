import os

class MCP3424():
	
	SYSFS_PATH = '/sys/bus/i2c/devices/i2c-1/1-0068'
	SYSFS_IIO  = '/iio:device0/'
	__enable = False
	
	def __init__(self):
		if not os.path.exists(self.SYSFS_PATH):
			os.system('sudo /bin/bash -c "echo \'mcp3424 0x68\' > /sys/bus/i2c/devices/i2c-1/new_device"')
		
		if not os.path.exists(self.SYSFS_PATH):
			raise Exception('sysfs error')
		
		self.__enable = True
	
	def getVoltage(self, ch):
		if not self.__enable:
			return 0
		
		raw = 0.0
		scale = 0.0
		
		with open(self.SYSFS_PATH+self.SYSFS_IIO+'in_voltage{}_raw'.format(ch), "r") as f:
			raw = float(f.read())
		with open(self.SYSFS_PATH+self.SYSFS_IIO+'in_voltage{}_scale'.format(ch), "r") as f:
			scale = float(f.read())
		
		return (raw * scale)
	
	@property
	def ch0(self):
		return self.getVoltage(0)
	
	@property
	def ch1(self):
		return self.getVoltage(1)
	
	@property
	def ch2(self):
		return self.getVoltage(2)

	@property
	def ch3(self):
		return self.getVoltage(3)
