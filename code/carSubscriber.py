import threading
import paho.mqtt.client as mqtt
import datetime
import time
from time import sleep
import Queue

'''
def publish_1(client,topic):
message="on"
print("publish data")
client.publish(topic,message)
publish_1(client,topic)
'''
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
t0 = 0.0

servertime = ''
ts = 0.0

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe(timestamp)
	client.subscribe(iRed)
	client.subscribe(iRedYellow)
	client.subscribe(iGreen)
	client.subscribe(iYellow)
	client.subscribe(TTNS)
	client.subscribe(interupt)

def on_message(client, userdata, msg):
	t0 = time.time()
	if msg.topic == timestamp:
		servertime = str(msg.payload)
		print("UTC Servertime:" +servertime)
		
	if msg.topic == iRed:
		timeRed = msg.payload
		print("Red: " + timeRed)
		q.put("Queue Inhalt")
		
	if msg.topic == iRedYellow:
		timeRedYellow = msg.payload
		print("RedYellow: " + timeRedYellow)
		
	if msg.topic == iYellow:
		timeYellow = msg.payload
		print("Yellow: " + timeYellow)
	if msg.topic == iGreen:
		timeGreen = msg.payload
		print("Green: " + timeGreen)
		
	if msg.topic == interupt:
		serverInterupt = msg.payload
		print("Serverinterupt " + serverInterupt)
		
	if msg.topic == TTNS:
		ttns = msg.payload
		print("timeTillNextState " + ttns +"[seconds]")
		
	if msg.topic == CS:
		currentState = msg.payload
		print("current State " + currentState)

def getPeriodTime():
	periodtime = timeRed + timeRedYellow + timeGreen + timeYellow
	return periodtime
	
def timeNextGreenDeadline():
	if 	currentState == "Green":
		return 0 

	if currentState == "Red":
		return ((timeRed - ttns) + timeRedYellow)
		
	if currentState == "Yellow":
		return ((timeYellow -ttns) + timeRed + timeRedYellow)
		
	if currentState == "Red-Yellow":
		return ttns
	else:
		return "Time till next Green Deadline can not be calculated"

		


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(Broker, 1883, 60) 
q = Queue.Queue

#timeSync  

while noInterupt == True:
	print(timeNextGreenDeadline())
	client.loop_forever()


