
import paho.mqtt.client as mqtt
#import MbotMQTT
from mbot import mbot_drive_straight
from mbot import mbot_motor_stop
#from MbotMQTT import Mbot_start
#from carSubscriberLibrary import readIO
import time
import serial
import threading

serial = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=3.0)

workArray=[ 10.,1.,3.,10.,5.,"Green"]

start_distance = 50.0
start_speed = 155
start_speedsi = (0.42/255)*155
max_speed = 255
min_speed = 55
min_speedsi = (0.42/255)*55
noInterupt = True
Broker="172.31.12.122"
topic_pub="traffiLight/carMessage"
#subscribe topics
state = "traffiLight/state"             #dummy topic
TTNS = "traffiLight/timeTillNextState"  #refreshed subtopic showing time till change in seconds
timestamp = "traffiLight/timestamp"               #UTC Servertime from Trafficlight
iRed = "traffiLight/iRed"               #interval for Red in Seconds
iRedYellow = "traffiLight/iRedYellow"   #interval for Red-Yellow in Seconds
iGreen = "traffiLight/iGreen"           #interval for Green in Seconds
iYellow = "traffiLight/iYellow"         #interval for Yellow in Seconds
interupt = "traffiLight/interupt"       #interupt if Bus/RTW comes and other
CS = "traffiLight/currentState"
currentState = ""
timeRed = 0.0
timeRedYellow = 0.0
timeGreen = 0.0
timeYellow = 0.0
	
def on_connect(client, userdata, flags, rc):
		print("Connected with result code "+str(rc))
		#self.client.subscribe(timestamp)
		client.subscribe(iRed)
		client.subscribe(iRedYellow)
		client.subscribe(iGreen)
		client.subscribe(iYellow)
		client.subscribe(TTNS)
		client.subscribe(interupt)
		client.subscribe(CS)
		
def on_message(client, userdata, msg):
	'''
	if self.msg.topic == timestamp:
			servertime = str(msg.payload)
			print("UTC Servertime:" +servertime)
	'''

	if msg.topic == iRed: 
		timeRed = msg.payload
		#print("Red: " + timeRed)
		workArray[0] = timeRed
	
	if msg.topic == iRedYellow:
		timeRedYellow = msg.payload
		#print("RedYellow: " + timeRedYellow)
		workArray[1] = timeRedYellow

	if msg.topic == iYellow:
		timeYellow = msg.payload
		#print("Yellow: " + timeYellow)
		workArray[2] = timeYellow

	if msg.topic == iGreen:
		timeGreen = msg.payload
		#print("Green: " + timeGreen)
		workArray[3] = timeGreen

	if msg.topic == interupt:
		serverInterupt = msg.payload
		#print("Serverinterupt " + serverInterupt)

	if msg.topic == TTNS:
		ttns = msg.payload
		#print("timeTillNextState " + ttns +"[seconds]")
		workArray[4] = ttns

	if msg.topic == CS:
		currentState = msg.payload
		#print("currentState " + currentState)
		workArray[5] = currentState
		


class connectMQTT(threading.Thread):
	def __init__(self,Broker):
		threading.Thread.__init__(self)
		
		if Broker == 0:
			self.Broker="172.31.12.122"
		
		self.client = mqtt.Client()
		self.client.on_connect = on_connect
		self.client.on_message = on_message
		self.client.connect(Broker, 1883, 60)
		self.run()
		
	def run(self):
		#while noInterupt == True:
		#print(timeNextGreenDeadline())
		self.client.loop_start()
		time.sleep(0.1)
		print str(workArray)
		self.client.loop_stop()


current_milli_time = lambda: int(round(time.time() * 1000))


def main():
	print "Chris Threadings should start here"
	mqttConnection = connectMQTT(Broker)
	mqttConnection.start()
	print "Chris Thread started"
	
	#driveAlgorithm()

	
def driveAlgorithm():
	t0 = current_milli_time()
   #while Mbot_start() == 1:
	while 1:
		print "Mbot started!"
		if timeNextGreenStart() == "error":
			break
		else:
			mbot_drive_straight(serial,start_speed,"forward")		    
			tta = start_distance/start_speedsi
			print "Debug1"
			# wenn die Gruenphase erreicht werden kann, dann behalte Geschwindigkeit
			if timeNextGreenStart()< tta and workArray[4] > tta:
				mbot_drive_straight(serial,start_speed,"forward")
				print "Debug2"
			#Mbot wuerde vor oder nach der Gruenphase ankommen
			elif timeNextGreenStart() > tta or workArray[4] < tta:
			
			#Mbot muss an der Ampel stoppen
				if timeNextGreenStart() > start_distance/min_speed:
					slowdown()
					tnow = current_milli_time()
					distance = ((start_speedsi+min_speedsi)/2)*(tnow-t0)
					if distance >= start_distance:
						mbot_motor_stop()
					
			#Geschwindigkeit wird angepasst, sodass Mbot bei gruen ankommt		
			else:
				new_speed = distance/timeNextGreenStart()
				mbot_drive_straight(serial,new_speed,"forward")
				print "Debug3"
		

def timeNextGreenStart():
	#Function returns a float with time in seconds till the next Green-Phase ends
	if 	workArray[5] == "Green":
		return 0 
		print("--------------------------------------------------Green received in main.py")

	if workArray[5] == "Red":
		#return ((timeRed - ttns) + timeRedYellow)
		return (workArray[0] - workArray[4] +workArray[1])
		print("--------------------------------------------------Red received in main.py")

	if workArray[5] == "Yellow":
		#return ((timeYellow -ttns) + timeRed + timeRedYellow)
		return (workArray[2] - workArray[4] + workArray[0] + workArray[1])
		print("--------------------------------------------------Yellow received in main.py")

		
	if workArray[5] == "Red-Yellow":
		#return ttns
		return workArray[4]
		print("--------------------------------------------------Red-Yellow received in main.py")
	else:
		return "Time till next Green Deadline can not be calculated"
		
def slowdown():
	for new_speed in range(start_speed,min_speed):
		mbot_drive_straight(serial,new_speed,"foreward")
		new_speed= newspeed-1
		sleep(0.2)

if __name__ == '__main__':
	main()


