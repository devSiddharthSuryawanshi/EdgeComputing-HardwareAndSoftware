# web_dashboard.py
from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json
import sqlite3
import threading
from datetime import datetime
import time

app = Flask(__name__)

# Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "steel/defects"
DB_FILE = "defects.db"

# Global variables for real-time updates
latest_alerts = []
statistics = {}

class MQTTListener:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            client.subscribe(MQTT_TOPIC)
        else:
            print(f"❌ Failed to connect to MQTT broker. Return code: {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            alert_data = json.loads(msg.payload.decode())
            alert_data['received_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Store in database
            self.store_alert(alert_data)
            
            # Update latest alerts (keep last 10)
            global latest_alerts
            latest_alerts.insert(0, alert_data)
            latest_alerts = latest_alerts[:10]
            
            print(f"📨 Received alert: {alert_data['defect_type']}")
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            
    def store_alert(self, alert_data):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO defects (timestamp, defect_type, confidence, frame_number, total_defects_session)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                alert_data.get('timestamp'),
                alert_data.get('defect_type'),
                alert_data.get('confidence'),
                alert_data.get('frame'),
                alert_data.get('total_defects_session', 0)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Database error: {e}")
            
    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/alerts')
def get_alerts():
    return jsonify(latest_alerts)

@app.route('/api/statistics')
def get_statistics():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Total defects
        cursor.execute("SELECT COUNT(*) FROM defects")
        total_defects = cursor.fetchone()[0]
        
        # Defects by type
        cursor.execute("SELECT defect_type, COUNT(*) FROM defects GROUP BY defect_type")
        defects_by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent activity
        cursor.execute("""
            SELECT strftime('%Y-%m-%d %H:%M', timestamp) as hour, COUNT(*) 
            FROM defects 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY hour 
            ORDER BY hour DESC 
            LIMIT 24
        """)
        hourly_activity = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_defects': total_defects,
            'defects_by_type': defects_by_type,
            'hourly_activity': hourly_activity,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent')
def get_recent():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, defect_type, confidence 
            FROM defects 
            ORDER BY id DESC 
            LIMIT 20
        """)
        recent = cursor.fetchall()
        conn.close()
        
        recent_list = [
            {'timestamp': row[0], 'defect_type': row[1], 'confidence': row[2]}
            for row in recent
        ]
        
        return jsonify(recent_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def init_database():
    """Initialize database if not exists"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            defect_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            frame_number INTEGER,
            total_defects_session INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start MQTT listener in background thread
    mqtt_listener = MQTTListener()
    mqtt_listener.start()
    
    # Start Flask web server
    print("🚀 Starting Web Dashboard on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)