from flask import Flask, Response, render_template_string
import cv2

app = Flask(__name__)
cap = cv2.VideoCapture(0)

def generate():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Home route to show the video feed in a simple HTML page
@app.route('/')
def index():
    return render_template_string('''
        <html>
            <head><title>Live Camera Feed</title></head>
            <body>
                <h1>Camera Streaming</h1>
                <img src="{{ url_for('video_feed') }}" width="640" height="480">
            </body>
        </html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
