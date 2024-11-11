# -*- coding: utf-8 -*-
import firebase_admin
from google.cloud import firestore
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, render_template
from read_sensor import turnoff, motor

cred = credentials.Certificate("/home/anhuynh/IoT_Projects/connect_firebase/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()  
app = Flask(__name__)

@app.route('/')
def index():
    doc = db.collection("sensor_data").document("sensor1").get()
    if doc.exists:
        sensor_data = doc.to_dict()
    else:
        sensor_data = {"temperature": "No data", "humidity": "No data"}

    for key in sensor_data.keys():
        try:
            sensor_data[key] = str(sensor_data[key]) if sensor_data[key] is not None else "No data"
        except UnicodeEncodeError as e:
            sensor_data[key] = "Invalid data"  
            print(f"UnicodeEncodeError: {e}")

    return render_template('index.html', sensor_data=sensor_data)

@app.route('/get_sensor_data', methods=['GET'])
def get_sensor_data():
    doc = db.collection("sensor_data").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).get()
    if doc:
        sensor_data = doc[0].to_dict()
        return jsonify(sensor_data)  
    else:
        return jsonify({"timestamp": "No data", "temperature": "No data", "humidity": "No data"})

@app.route('/turn_off_alert', methods=['POST'])
def turn_off_alert():
    turnoff()
    return jsonify({"message": "Alert turned off successfully"}), 200

@app.route('/turn_off_motor', methods=['POST'])
def turn_off_motor():
    motor()
    return jsonify({"message": "Alert turned off successfully"}), 200

@app.route('/senddata', methods=['POST'])
def recieive():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        doc_ref = db.collection("sensor_data").document("sensor1")
        doc_ref.set(data)  
        return jsonify({"message": "Data sent to Firebase successfully"}), 200
    except Exception as e:
        print("Failed to send data:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)