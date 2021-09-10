from machine import Pin,ADC,PWM
from time import sleep, time 
from neopixel import NeoPixel
import network
import json
from umqtt.simple import MQTTClient
import urequests as requests

TIMEOUT = None

np=NeoPixel(Pin(21), 1)
adc= ADC(Pin(36))
buzzer=Pin(18,Pin.OUT)
buzz=PWM(buzzer)
buzz.deinit()
relay=Pin(21,Pin.OUT)

def buz():
    buzz.init()
    buzz.freq(500)
    buzz.duty(50)
    sleep(2)
    buzz.duty(0)
    
def buzzz():
    buzz.init()
    buzz.freq(2000)
    buzz.duty(50)
    sleep(2)
    buzz.duty(0)

station=network.WLAN(network.STA_IF)
station.active( True)
station.connect("WorkShop", "m,./@1234")
print(station.isconnected())
print(station.ifconfig())
webhook_url="https://maker.ifttt.com/trigger/fire_notify/with/key/d4-rwPEBcD6dTNo-DD6o8hopYUDioCLOi8Fro1qDvVb"
WEBHOOK_URL="https://maker.ifttt.com/trigger/smart_fire_alarm/with/key/d4-rwPEBcD6dTNo-DD6o8hopYUDioCLOi8Fro1qDvVb"

CAYENNE_UNAME="32b88db0-a922-11eb-883c-638d8ce4c23d"
CAYENNE_PASSWORD="19af329a907a0d600b7dc2845c4779eae362e8e5"
CAYENNE_CLIENT= "cee5f010-a922-11eb-883c-638d8ce4c23d"   
server="mqtt.mydevices.com"

c = MQTTClient(CAYENNE_CLIENT, server,user=CAYENNE_UNAME, password=CAYENNE_PASSWORD)

try:
    c.connect()
    print("connection Success...")
except Exception as e:
    print(e)
    print("connection Error...")


topic="v1/"+CAYENNE_UNAME+"/things/"+CAYENNE_CLIENT+"/data/json"
bytes_topic=bytes(topic,'utf-8')

def notify():
    try:
       r=requests.get(webhook_url)
       print(r.text)
    except Exception as e:
        print(e)
        
def call():
    try:
        r=requests.get(WEBHOOK_URL)
        print(r.text)
    except Exception as e:
        print(e)
        
def led():
    np[0]=(0,0,255)
    np.write()
    sleep(0.5)
    np[0]=(0,0,0)
    np.write()
    sleep(0.5)
    
def cayenne():
    data=[
    {
       "channel": 1,
       "value": value,
       "type": "temp",
       "unit": "c"
},
    {
       "channel": 2,
       "value": value,
       "type": "temp",
       "unit": "c"
}
    
   
    
]
 
    data=json.dumps(data)
    c.publish(bytes_topic,data)
    
   
    sleep(1)


while True:
    try:
        value=adc.read()
        sleep(2)
        print(value)
        cayenne()
        if value <=2700:
            np[0]=(0,255,0)
            np.write()
            
        elif value>2700 and value<3000:
            np[0]=(0,0,255)
            np.write()
            buzzz()
            
        else:
            np[0]=(255,0,0)
            np.write()
            buz()
            relay.value(1)
            if TIMEOUT is None:
                TIMEOUT =  time()
                call()
                notify()
            elif time() - TIMEOUT >= 30:
                TIMEOUT =  time()
                call()
                notify()
            print('Time lapse ',  time() - TIMEOUT)
    except Exception as e:
        print(e)
        with open('error_logs.txt', 'a') as err_log:
            err_log.write(str(e)+'\n')
        
    print()



       

