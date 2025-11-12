import torch
import cv2
import os
import json

# Load Roboflow model info
with open("roboflow_config.json") as f:
    config = json.load(f)

model_path = config.get("model_path", "best.pt")
labels = config.get("labels", ["person"])

# Load YOLOv5 or YOLOv8 model
print("[INFO] Loading model...")
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=False)

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera not found!")
    exit()

print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Inference
    results = model(frame)
    detections = results.xyxy[0].cpu().numpy()

    # Draw bounding boxes for 'person' class
    for *xyxy, conf, cls in detections:
        label = model.names[int(cls)]
        if label.lower() == "person":
            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Person Detection - Jetson Orin Nano", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
