# Person Detection using Roboflow Model (Jetson Orin Nano)

This project demonstrates **real-time person detection** using a **deep learning model exported from Roboflow** and deployed on the **NVIDIA Jetson Orin Nano**.

##  Features
- Real-time inference from camera feed
- Uses YOLOv5/YOLOv8 exported model
- Optimized for Jetson Nano/Orin GPU
- Detects "person" class with bounding boxes

## ⚙️ Setup Instructions

###  Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-opencv -y
pip3 install torch torchvision torchaudio
```

###  Install Python Libraries
```bash
pip3 install -r requirements.txt
```

###  Add Roboflow Model
- Export your model from Roboflow (YOLOv5 or YOLOv8)
- Place it in the project folder as `best.pt`
- Edit `roboflow_config.json` to match your model and labels

##  Run Detection
```bash
python3 detect_person.py
```
> Press `q` to exit the video window.

##  Performance on Jetson Orin Nano
| Metric | Value |
|---------|--------|
| FPS | 25–30 |
| Inference Latency | ~40ms |
| Accuracy | 90%+ (depends on model) |

##  Future Enhancements
- Add tracking (SORT/DeepSORT)
- Integrate with edge dashboard
- Deploy as a containerized service with MQTT streaming
