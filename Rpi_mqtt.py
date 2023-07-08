import pandas as pd
from loadcell import loadcell
import gpiozero as gpio
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import threading
from simple_pid import PID
import json
import sys, getopt
import RTIMU
import os.path
import time
import math
sys.path.append('/usr/local/lib/python3.10/dist-packages')
sys.path.append('/usr/local/lib/python3.10/dist-packages/RTIMULib-8.1.0-py3.10-linux-x86_64.egg')

def weigh():
    global client
    weight=lc.weigh()
    client.publish('weight', weight)
def tare():
    lc.tare()
def startIMU():
    global client
    global IMUflag
    global phi
    global theta
    global phi_slider_val
    global theta_slider_val
    global angleflag
    global autolevelflag
    global file
    global stopwatchFlag
    global timestamp
    stopwatchFlag=True
    IMUflag=True
    SETTINGS_FILE = "RTIMULib"
    s = RTIMU.Settings(SETTINGS_FILE)
    imu = RTIMU.RTIMU(s)
    timestamp=0
    if (not imu.IMUInit()):
        sys.exit(1)
    else:
        pass

    imu.setSlerpPower(0.02)
    imu.setGyroEnable(True)
    imu.setAccelEnable(True)
    imu.setCompassEnable(False)
    poll_interval=imu.IMUGetPollInterval()

    while IMUflag:
        if imu.IMURead():
            fusiondata = imu.getFusionData()
            phi= math.degrees(fusiondata[0])
            theta = math.degrees(fusiondata[1])
            time.sleep(poll_interval*1.0/1000.0)
            msg=(phi,theta)
            msg=json.dumps(msg)
            client.publish('IMU',msg)
            if autolevelflag:
                # angleroll=round(pidroll(theta),1)
                # anglepitch=round(pidroll(phi),1)
                # data=df.loc[(anglepitch,angleroll)]
                data=df.loc[(round(phi),round(theta))]
                rightpos=data.loc['right']
                leftpos=-data.loc['left']
                frontpos=data.loc['front']
                backpos=data.loc['back']
                right.angle=rightpos
                left.angle=leftpos
                front.angle=frontpos
                back.angle=backpos
            elif angleflag:
                angleroll=round(pidroll(theta),1)
                anglepitch=round(pidpitch(phi),1)
                data=df.loc[(anglepitch,angleroll)]
                rightpos=data.loc['right']
                leftpos=data.loc['left']
                frontpos=data.loc['front']
                backpos=data.loc['back']
                right.angle=rightpos
                left.angle=leftpos
                front.angle=frontpos
                back.angle=backpos
            file.append({'time':timestamp,'roll':theta,'pitch':phi,})        
def startloadcell():
    global loadcellflag
    global file
    global client
    global timestamp
    loadcellflag=True
    while loadcellflag:
        lc1, lc2, lc3, lc4 = lc.measure()
        lct = round((lc1 + lc2 + lc3 + lc4),2)
        msg=(lc1, lc2, lc3, lc4, lct)
        msg = json.dumps(msg)
        client.publish('loadcell',msg)     
        file.append({'time': timestamp, 'thrust': lct, 'motor1': lc1, 'motor2': lc2, 'motor3': lc3, 'motor4': lc4})
def updateSliders(message):
    global phi_slider_val
    global theta_slider_val
    global pidroll
    global pidpitch
    msg=message.decode('utf-8')
    msg=json.loads(msg)
    phi_slider_val=msg[0]
    theta_slider_val=msg[1] 
    pidroll.setpoint=theta_slider_val
    pidpitch.setpoint=phi_slider_val
def stop():
    global IMUflag
    global stopwatchFlag
    global loadcellflag
    global pidroll
    global pidpitch
    stopwatchFlag=False
    loadcellflag=False
    IMUflag=False
def autolevel():
    global angleflag
    global autolevelflag
    global pidroll
    global pidpitch
    angleflag=False
    autolevelflag=True
    pidroll.setpoint=0
    pidpitch.setpoint=0
def angle():
    global angleflag
    global autolevelflag
    global pidroll
    global pidpitch
    autolevelflag=False 
    angleflag=True
    pidroll.setpoint=theta_slider_val
    pidpitch.setpoint=phi_slider_val
def stopwatch():
    global stopwatchFlag
    global client
    global timestamp
    start=time.time()
    while stopwatchFlag:
        passed=time.time()-start
        timestr=formatTime(passed)
        timestamp=passed
        client.publish('time',timestr)
def formatTime(time):
    secs=time % 60
    mins=time//60
    hours=mins//60
    return f'{int(hours):02d}:{int(mins):02d}:{int(secs):02d}:{int((time % 1)*100):02d}'
def saveFile():
    global file
    timestr=time.strftime('%Y_%m_%d-%H_%M_%S')
    filename='logs/'+timestr+'.json'
    f=open(filename,'w')
    file=json.dumps(file)
    f.write(file)
    print('File saved as '+timestr+'.json')
def on_message(client, userdata, message):
    global phi_slider_val
    global theta_slider_val
    global autolevelflag
    global angleflag
    global file
    topic=message.topic
    msg=message.payload
    if topic=='weigh':
        print('weigh received')
        weigh()
    if message.topic=='tare':
        print('tare received')
        tare()
    if message.topic=='start':
        print('start received')
        file=[]
        t1=threading.Thread(target=startIMU, daemon=True)
        t1.start()
        threading.Thread(target=stopwatch).start()
        t2=threading.Thread(target=startloadcell,daemon=True)
        t2.start()
    if message.topic=='stop':
        print('stop received')
        t3=threading.Thread(target=stop)
        t3.start()
    if message.topic=='autolevel':
        print('autolevel received')
        t4=threading.Thread(target=autolevel)
        t4.start()
    if message.topic=='angle':
        print('angle received')
        t5=threading.Thread(target=angle)
        t5.start()
    if message.topic=='updateSliders':
        t6=threading.Thread(target=updateSliders(msg), daemon=True)
        t6.start()
    if message.topic=='savetofile':
        print('save to file received')
        t7=threading.Thread(target=saveFile)
        t7.start()
    return topic, msg 
try:
    # Read data from database
    df=pd.read_csv('database3.csv') # test data, must be recalculated once final measurements are known
    df.set_index(['phi','theta'], inplace=True)
    # Initialize phi and theta values
    phi=0
    theta=0
    phi_slider_val=0
    theta_slider_val=0

    # set servo initial values
    right=gpio.AngularServo(12,initial_angle=0.0, min_angle=-90, max_angle=90, min_pulse_width=0.00075,max_pulse_width=0.0022) # 0.75ms to 2.2ms with 20ms period
    left=gpio.AngularServo(16,initial_angle=0.0, min_angle=-90, max_angle=90, min_pulse_width=0.00075,max_pulse_width=0.0022)
    front=gpio.AngularServo(20,initial_angle=0.0, min_angle=-90, max_angle=90, min_pulse_width=0.00075,max_pulse_width=0.0022)
    back=gpio.AngularServo(21,initial_angle=0.0, min_angle=-90, max_angle=90, min_pulse_width=0.00077,max_pulse_width=0.0022)
    right.angle=0.0
    left.angle=0.0
    back.angle=0.0
    front.angle=0.0
    pidroll = PID(0.5,0.02,0.001, setpoint=0) # once everything is connected, check and tune pid values
    pidpitch = PID(0.5, 0.02, 0.001, setpoint=0)
    angleflag=False
    autolevelflag=True
    IMUflag=False     
    lc=loadcell()   

    broker_address ='localhost'
    broker_port=1883
    client=mqtt.Client('RPi')
    client.on_message=on_message
    client.connect(broker_address,broker_port)
    client.subscribe('weigh')
    client.subscribe('tare')
    client.subscribe('start')
    client.subscribe('stop')
    client.subscribe('updateSliders')
    client.subscribe('autolevel')
    client.subscribe('angle')
    client.subscribe('savetofile')
    client.loop_forever()
except KeyboardInterrupt:
    GPIO.cleanup()
    client.disconnect()
