# -*- coding: utf-8 -*-
from flask import Flask, jsonify
import Adafruit_DHT
import time
import requests
import threading
import RPi.GPIO as GPIO
app = Flask(__name__)

DHT = Adafruit_DHT.DHT11    
LED_PIN = 27      
BUZZER_PIN = 22    
FIRE_PIN = 18
TEMP_PIN = 4
RELAY_PIN = 17


GPIO.setmode(GPIO.BCM)
GPIO.setup(FIRE_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)       
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(RELAY_PIN,GPIO.OUT)  
GPIO.output(RELAY_PIN, GPIO.LOW)
TEMP_THRESHOLD = 50.0
def log_data():
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT,TEMP_PIN)
        # gas_detected = GPIO.input(GAS_PIN)
        fire_detected = GPIO.input(FIRE_PIN)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        detect(fire_detected, temperature)            
        if humidity is not None and temperature is not None:
            print(f"Temp: {temperature:.2f}C  Humidity: {humidity:.2f}%")
            data ={
                "temperature" : temperature,
                "humidity" : humidity,
                "timestamp" : timestamp,
                "is_fire":fire_detected,
            }
            thread = threading.Thread(target=send_data, args=(data,))
            thread.start()
        else :
             print("Failed to retrieve data from sensor")
        
        #time.sleep(0.5)

def detect(fire_detected,temperature):
    # if fire_detected == 1 and temperature > TEMP_THRESHOLD:
    if fire_detected == 1:
        GPIO.output(LED_PIN, GPIO.HIGH)   
        GPIO.output(BUZZER_PIN, GPIO.HIGH) 
        GPIO.output(RELAY_PIN, GPIO.HIGH)

 

def turnoff():
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def motor():
    GPIO.output(RELAY_PIN, GPIO.LOW)

def send_data(data):
    response = requests.post("http://127.0.0.1:5000/senddata", json=data)
    if response.status_code == 200:
        print("Data sent successfully:", data)
    else:
        print("Failed to send data:", response.text)


if __name__ == "__main__":
    try:
        log_data()
    except KeyboardInterrupt:
        print("ERROR")
    finally:
        GPIO.cleanup()
