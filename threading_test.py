
#Import our reqired Librarys
from threading import Thread
import paho.mqtt.client as mqtt
import serial
import time
import timeit
from time import sleep
from mbot import mbot_drive_straight
from mbot import mbot_motor_stop

# Global variables for MQTT Transfer
global timeRed 
global timeRedYellow 
global timeGreen
global timeYellow 
global m_start_signal
global workArray
global state
global TTNS
global timestamp 
global iRed 
global iRedYellow 
global iGreen 
global iYellow       
global interupt 
global CS 
global startTopic 
global currentState
global t0

# Set up the global Serial communication 
global serial
serial = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=3.0)

# Subscribe Topics all starting with traffiLight/ for
state = "traffiLight/state"             # dummy topic
TTNS = "traffiLight/timeTillNextState"  # refreshed subtopic showing time till change in seconds
timestamp = "traffiLight/timestamp"     # UTC Servertime from Trafficlight !!!Not needed yet"
iRed = "traffiLight/iRed"               # interval for Red in Seconds
iRedYellow = "traffiLight/iRedYellow"   # interval for Red-Yellow in Seconds
iGreen = "traffiLight/iGreen"           # interval for Green in Seconds
iYellow = "traffiLight/iYellow"         # interval for Yellow in Seconds
interupt = "traffiLight/interupt"       # interupt if Bus/RTW comes and other
CS = "traffiLight/currentState"         # current state as string, can be "Green","Red","Red-Yellow" and "Yellow"
startTopic = "traffiLight/start"        # topic to read start signal from for starting mBot from distance
currentState = ""                       # can be "Green","Red","Red-Yellow" and "Yellow"

timeRed = 0.0                           # inital time before MQTT received a value
timeRedYellow = 0.0                     # inital time before MQTT received a value
timeGreen = 0.0                         # inital time before MQTT received a value
timeYellow = 0.0                        # inital time before MQTT received a value
m_start_signal = 1                 # inital time before MQTT received a value
workArray=[ 10.,1.,3.,10.,4.,""]   # inital time before MQTT received a value

# create some global variables to transfer Data from one thread into an other
global cycle                            # global is needed to break up with the Main Loop
cycle = 0.0

global mqtt_return_value                # This is a variable to return the mqtt values
mqtt_return_value = 0                   # for testing reasons the default is 0

global mqtt_return_start                # This is a variable to start the Drive Algorithm
mqtt_return_start = 1	                # Default of these var is 0 for Not Starting; 1 = Start Drive Algorithm

global Broker                           # Broker is running via a dedicated windows pc... The MQTT.fx ,Broker is used on Windows(@Johannes?)
Broker = "172.31.12.122"                # Broker IP Adress

global topic_pub                        # Mqtt Topic to subscribe
topic_pub="traffiLight/carMessage"


class Get_MQTT:                         # Begining of the Get_MQTT Class
    def __init__(self):                 
        self._running = True

        if Broker == 0:
            self.Broker="172.31.12.122"
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(Broker, 1883, 60)

    def terminate(self):                # Terminator of the Get_MQTT Class
        self._running = False 

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        #self.client.subscribe(timestamp)
        client.subscribe(iRed)
        client.subscribe(iRedYellow)
        client.subscribe(iGreen)
        client.subscribe(iYellow)
        client.subscribe(TTNS)
        client.subscribe(interupt)
        client.subscribe(CS)
        client.subscribe(startTopic)
        
    def on_message(self,client, userdata, msg):
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

        if msg.topic == TTNS:
            ttns = msg.payload
            #print("timeTillNextState " + ttns +"[seconds]")
            workArray[4] = ttns

        if msg.topic == CS:
            currentState = msg.payload
            #print("currentState " + currentState)
            workArray[5] = currentState
        
        if msg.topic == startTopic:
            m_start_signal = msg.payload

    def run(self):                      # beginning of the "MAIN LOOP" from these Thread 
        global mqtt_return_value        # declare the global var for the Class
        global mqtt_return_start        # declare the global Start Var for the Class
        global workArray
        
        while self._running:            # Start While Loop

            self.client.loop_start()
            print str(workArray)		# Prints out the recived Messages            
            self.client.loop_stop()
            
            """
                In the following we have to implement our MQTT SUPscriber BLA BLA 
                Our return value is a global var called "mqtt_return_value"
                The Value of this Var is available in our main and also in other threds if the global var is declared in the class 
            """
            
            #If the Start topic is subscribed with 1 
            """
            if Mqtt.start == 1 
                mqtt_return_start = 1
            """

class Drive_Algorithm:  
	start_distance = 2
	#startdistance in m
	start_speed = 155				#Integer for motor value 0...255
	start_speedsi = (0.42/255)*155 #speed in m/s
	max_speed = 255
	min_speed = 55
	min_speedsi = (0.42/255)*55 # minimal moving speed
	
	bla = 23
	
	def __init__(self):
		self._running = True

	def terminate(self):                # Terminator for the Drive_Algortihm_Thread
		self._running = False
	"""  
		def calcSpeed(newSpeed):				# new Speed in Mbot values,  
			maxSpeed = 0.42						# maximum Speed in [m/s]
			newMbotSpeed = (newSpeed/maxSpeed)*255	#newMbotSpeed = Value betweeen 0-255; 
			return newMbotSpeed  
	"""
	def run(self):                      # beginning of the "Main Loop" From these Thread
		global mqtt_return_value        # declare the global var for the class
		global workArray
		global serial
		global m_start_signal
		
		
		while self._running:            # Start While Loop 
			tta = self.start_distance/self.start_speedsi
						
			# detection of the earliest reachable green light
			
			
			if (tta > self.timeNextGreenStart()):
				print "passt"
				
				
				
				print self.timeNextGreenStart()
			else:
				print "passt nicht"
				print self.start_speed
				print self.start_distance
				#print self.timeNextGreenStart
				print time_to_trafficlight 
				print self.timeNextGreenStart()
			
			
			
			
			
		
			
			
			
			
			print("t0 is:", t0)
			print "driveAlgorithm is alive"
			print workArray
			print ("tNGSis:", self.timeNextGreenStart())
			# wenn timeNextGreenStart nicht ausgefuehrt werden kann, ist workarray vermutlich nicht verfuegbar
			mbot_drive_straight(serial,self.start_speed,"forward")
			if self.timeNextGreenStart() == "error":
				print("TimeNextGreenStart can not be calculatet")
				#wenn eine 0 an Start Signal gesendet wird springe aus der Schleife
				break
			elif m_start_signal == 0:
				print("Start Signal is 0")
				
			#actual algorithm
			else:
				mbot_drive_straight(serial,self.start_speed,"forward")		    
				tta = self.start_distance/self.start_speedsi
				print("Startsignal is: ",str(m_start_signal))
				# wenn die Gruenphase erreicht werden kann, dann behalte Geschwindigkeit
				if self.timeNextGreenStart()< tta and workArray[4] > tta:
					mbot_drive_straight(serial,self.start_speed,"forward")
					#Mbot wuerde vor oder nach der Gruenphase ankommen
				elif self.timeNextGreenStart() > tta or workArray[4] < tta:
				
				#Mbot muss an der Ampel stoppen
					while self.timeNextGreenStart() > self.start_distance/self.min_speedsi:
						print "slowdown buddy!"
						mbot_drive_straight(serial,self.min_speed,"forward")
						tnow = timeit.default_timer()
						print("tnow is:",tnow)
						print("t0 is:", t0)
						distance = self.min_speedsi*(tnow-t0)
						print(distance)
						
						#Mbot hat Ampel erreicht, haelt an und wartet auf naechste Gruenphase
						if distance >= self.start_distance:
							print "Halt stop, jetzt bremst der mBot"
							mbot_motor_stop(serial)
							
							
				#Geschwindigkeit wird angepasst, sodass Mbot bei gruen ankommt		
				else:
					new_speed = (distance/self.timeNextGreenStart())/(0.42/255) #new speed muss auf Werte zwischen 55 und 255 gemapt werden
					if new_speed > 255 or new_speed < 55:
						break
					else:
						mbot_drive_straight(serial,new_speed,"forward")
						print "Geschwindigkeit wird gedrosselt fuer Gruene Welle :)"
			
			
			tnow = timeit.default_timer()
			print("tnow is:",tnow)
			print("t0 is:", t0)
			distance = self.min_speedsi*(tnow-t0)
			print(distance)
			
			#Mbot ist an der Ampel vorbei
			if distance >= self.start_distance:
							print ("mBot has passed the trafficLight!")		
							mbot_motor_stop(serial)
							break
					
	def timeNextGreenStart(self):
		#Function returns a float with time in seconds till the next Green-Phase ends
		if 	workArray[5] == "Green":
			return 0 
			print("--------------------------------------------------Green received in main.py")

		if workArray[5] == "Red":
			#return (ttns + timeRedYellow)
			return (workArray[4] + workArray[1])
			print("--------------------------------------------------Red received in main.py")

		if workArray[5] == "Yellow":
			#return (ttns + timeRed + timeRedYellow)
			return (workArray[4] + workArray[0] + workArray[1])
			print("--------------------------------------------------Yellow received in main.py")
			
		if workArray[5] == "Red-Yellow":
			#return ttns
			return workArray[4]
			print("--------------------------------------------------Red-Yellow received in main.py")
		else:
			return "Time till next Green phase can not be calculated"
		
	def slowdown(self):
		for new_speed in range(self.start_speed,self.min_speed):
			mbot_drive_straight(serial,new_speed,"foreward")
			new_speed= new_speed-3
			sleep(0.2)
			


#Create Class Get_MQTT
Get_MQTT = Get_MQTT()
#Create Thread Get_MQTT_Thread
Get_MQTT_Thread = Thread(target=Get_MQTT.run) 
#Start Thread Get_MQTT_Thread
Get_MQTT_Thread.start()

sleep (1)							#Wait till next 
#Create Class Drive_Algortihm
Drive_Algorithm = Drive_Algorithm()
#Create Thread Drive_Algortihm_Thread
Drive_Algorithm_Thread = Thread(target=Drive_Algorithm.run) 
  


"""
#Start Thread Drive_Algortihm_Thread
Drive_Algorithm_Thread.start()          #The Drive Algorithm should be starded later in the Code, when the Main gets the Start Value
"""


[10.0, 1.0, 3.0, 10.0, 2.0, '']

Exit = False                            # Exit flag for Breaking up with the main Loop 
while Exit==False:                      # while Exit flag == False => Do the Loop... A Possible Exit Situation is when the Mbot reaches its goal
    #Starting the Main Loop of the whole Programm 

    """
	This is the Main Loop...
	This is where the magic happened
    """
	
    #The Get_MQTT Thread is already starded if there is there is the Start Topic, Start the Drive Algorithm
    if (m_start_signal == 1):
	#Start Thread Drive_Algortihm_Thread
		t0 = timeit.default_timer()
		Drive_Algorithm_Thread.start() 


    """
    ############### Some Test Code 

    print "Hier meldet sich die Main zu wort"
    time.sleep(0.1) #One second delay

    #Test if the returnvalue of the mqtt thread is valid 
    #print mqtt_return_value

    cycle = cycle + 0.1 
    print cycle
    if (cycle > 5): Exit = True #Exit Program

    ############### END of Test
    """

Drive_Algorithm.terminate()
Get_MQTT.terminate()
print "Goodbye :)"