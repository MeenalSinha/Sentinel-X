import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import tempfile
import os
from datetime import datetime
import pandas as pd
from collections import deque
import time

# Page config
st.set_page_config(
    page_title="Sentinel-X | Autonomous Border Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for glassmorphism + pastel UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark military gradient background */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Glassmorphism sidebar with light text */
    [data-testid="stSidebar"] {
        background: rgba(15, 52, 96, 0.7);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    /* Headers with gradient */
    h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0 !important;
        font-weight: 700;
    }
    
    h1 {
        background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Body text - darker/more visible */
    p, span, div, label {
        color: #1a1a1a !important;
    }
    
    /* Glassmorphism cards with dark text */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.3s ease;
        animation: fadeIn 0.6s ease-out;
    }
    
    .glass-card * {
        color: #1a1a1a !important;
    }
    
    .glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4, .glass-card h5, .glass-card h6 {
        color: #00d4ff !important;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 180, 216, 0.2);
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Hero section with glassmorphism */
    .hero-section {
        background: linear-gradient(135deg, rgba(224, 242, 254, 0.95), rgba(186, 230, 253, 0.95));
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(0, 212, 255, 0.3);
        margin-bottom: 2rem;
        animation: heroFadeIn 1s ease-out;
    }
    
    @keyframes heroFadeIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .hero-logo {
        font-size: 4rem;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .hero-title {
        color: #00d4ff !important;
        font-size: 3.5rem;
        font-weight: 900;
        margin: 1rem 0;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    .hero-subtitle {
        color: #1a1a1a !important;
        font-size: 1.5rem;
        font-weight: 400;
        opacity: 0.8;
    }
    
    /* Military-style buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%);
        color: #0a0e27 !important;
        border-radius: 15px;
        height: 3.5em;
        width: 100%;
        font-size: 1.1em;
        font-weight: 700;
        border: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #00b4d8 0%, #0096c7 100%);
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5);
    }
    
    .stButton>button:active {
        transform: translateY(0px);
    }
    
    /* Metric cards with glassmorphism */
    .metric-glass-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(240, 240, 240, 0.9));
        backdrop-filter: blur(15px);
        padding: 1.8rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(0, 212, 255, 0.2);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .metric-glass-card * {
        color: #1a1a1a !important;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-glass-card:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.3);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        margin: 0.5rem 0;
        color: #00d4ff !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #1a1a1a !important;
    }
    
    /* Threat level badges */
    .threat-high {
        background: linear-gradient(135deg, rgba(255, 68, 68, 0.95), rgba(220, 38, 38, 0.95));
        backdrop-filter: blur(10px);
        color: white !important;
        padding: 15px;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        border: 1px solid rgba(255, 68, 68, 0.3);
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.2);
        animation: pulse 2s infinite;
    }
    
    .threat-high * {
        color: white !important;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .threat-medium {
        background: linear-gradient(135deg, rgba(255, 170, 0, 0.95), rgba(255, 140, 0, 0.95));
        backdrop-filter: blur(10px);
        color: white !important;
        padding: 15px;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        border: 1px solid rgba(255, 170, 0, 0.3);
        box-shadow: 0 4px 15px rgba(255, 170, 0, 0.2);
    }
    
    .threat-medium * {
        color: white !important;
    }
    
    .threat-low {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.95), rgba(22, 163, 74, 0.95));
        backdrop-filter: blur(10px);
        color: white !important;
        padding: 15px;
        border-radius: 15px;
        font-weight: bold;
        text-align: center;
        border: 1px solid rgba(34, 197, 94, 0.3);
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
    }
    
    .threat-low * {
        color: white !important;
    }
    
    /* Alert boxes with light backgrounds */
    .glass-alert-success {
        background: rgba(220, 252, 231, 0.95);
        backdrop-filter: blur(10px);
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #1a1a1a !important;
    }
    
    .glass-alert-success * {
        color: #1a1a1a !important;
    }
    
    .glass-alert-warning {
        background: rgba(254, 243, 199, 0.95);
        backdrop-filter: blur(10px);
        border-left: 4px solid #ffaa00;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #1a1a1a !important;
    }
    
    .glass-alert-warning * {
        color: #1a1a1a !important;
    }
    
    .glass-alert-info {
        background: rgba(224, 242, 254, 0.95);
        backdrop-filter: blur(10px);
        border-left: 4px solid #00d4ff;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #1a1a1a !important;
    }
    
    .glass-alert-info * {
        color: #1a1a1a !important;
    }
    
    .glass-alert-danger {
        background: rgba(254, 226, 226, 0.95);
        backdrop-filter: blur(10px);
        border-left: 4px solid #ff4444;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #1a1a1a !important;
    }
    
    .glass-alert-danger * {
        color: #1a1a1a !important;
    }
    
    /* Tech badges */
    .tech-badge {
        display: inline-block;
        background: rgba(224, 242, 254, 0.9);
        backdrop-filter: blur(5px);
        color: #0077b6 !important;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        border: 1px solid rgba(0, 212, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .tech-badge:hover {
        background: rgba(0, 212, 255, 0.25);
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 212, 255, 0.2);
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(240, 248, 255, 0.9));
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 3rem;
        text-align: center;
        border: 1px solid rgba(0, 212, 255, 0.2);
        margin-top: 3rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .footer * {
        color: #1a1a1a !important;
    }
    
    .footer h2 {
        color: #00d4ff !important;
    }
    
    /* Streamlit specific overrides */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%);
    }
    
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #e0e0e0 !important;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%);
        color: #0a0e27 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #e0e0e0 !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 10px;
        color: #1a1a1a !important;
    }
    
    /* Slider */
    .stSlider>div>div>div>div {
        background: rgba(0, 212, 255, 0.3);
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #1a1a1a !important;
    }
    
    /* Streamlit text elements */
    .stMarkdown {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'event_log' not in st.session_state:
    st.session_state.event_log = []
if 'threat_history' not in st.session_state:
    st.session_state.threat_history = []
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False

# Object Tracker Class
class ObjectTracker:
    def __init__(self, max_disappeared=30):
        self.next_object_id = 0
        self.objects = {}
        self.disappeared = {}
        self.max_disappeared = max_disappeared
        self.trails = {}
        self.speeds = {}
        self.detection_classes = {}  # Track class per object
        
    def register(self, centroid, detection_class="entity"):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.trails[self.next_object_id] = deque(maxlen=30)
        self.trails[self.next_object_id].append(centroid)
        self.speeds[self.next_object_id] = 0
        self.detection_classes[self.next_object_id] = detection_class
        self.next_object_id += 1
        
    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]
        del self.trails[object_id]
        del self.speeds[object_id]
        if object_id in self.detection_classes:
            del self.detection_classes[object_id]
        
    def update(self, detections, detection_classes_map=None):
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects
        
        input_centroids = np.array([det[:2] for det in detections])
        
        if len(self.objects) == 0:
            for i, centroid in enumerate(input_centroids):
                det_class = detection_classes_map.get(i, "entity") if detection_classes_map else "entity"
                self.register(centroid, det_class)
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            D = np.linalg.norm(np.array(object_centroids)[:, np.newaxis] - input_centroids, axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                    
                if D[row, col] > 50:
                    continue
                    
                object_id = object_ids[row]
                old_centroid = self.objects[object_id]
                new_centroid = input_centroids[col]
                
                # Calculate speed
                distance = np.linalg.norm(new_centroid - old_centroid)
                self.speeds[object_id] = distance
                
                self.objects[object_id] = new_centroid
                self.trails[object_id].append(new_centroid)
                self.disappeared[object_id] = 0
                
                # Update detection class if provided
                if detection_classes_map and col in detection_classes_map:
                    self.detection_classes[object_id] = detection_classes_map[col]
                
                used_rows.add(row)
                used_cols.add(col)
            
            unused_rows = set(range(D.shape[0])) - used_rows
            unused_cols = set(range(D.shape[1])) - used_cols
            
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
                    
            for col in unused_cols:
                det_class = detection_classes_map.get(col, "entity") if detection_classes_map else "entity"
                self.register(input_centroids[col], det_class)
                
        return self.objects

# Anomaly Detection Class
class AnomalyDetector:
    def __init__(self, frame_width, frame_height, border_position=50):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.border_line = int(frame_height * border_position / 100)
        
    def detect_anomalies(self, tracker, current_time):
        """Detect behavioral anomalies using per-object detection classes"""
        anomalies = []
        
        for obj_id, centroid in tracker.objects.items():
            threat_level = "LOW"
            reasons = []
            confidence = 0.0
            behavior_score = 0.0
            
            # Check border crossing
            if obj_id in tracker.trails and len(tracker.trails[obj_id]) > 5:
                trail = list(tracker.trails[obj_id])
                crossed_border = False
                
                for i in range(len(trail) - 1):
                    if (trail[i][1] < self.border_line and trail[i+1][1] > self.border_line) or \
                       (trail[i][1] > self.border_line and trail[i+1][1] < self.border_line):
                        crossed_border = True
                        break
                
                if crossed_border:
                    reasons.append("Border crossing detected")
                    confidence += 35
                    behavior_score += 30
            
            # Check night-time movement (simulated based on darkness)
            hour = datetime.now().hour
            is_night = False
            if hour < 6 or hour > 20:
                reasons.append("Night-time movement")
                confidence += 20
                behavior_score += 15
                is_night = True
            
            # Check unusual speed
            speed_level = None
            if obj_id in tracker.speeds:
                speed = tracker.speeds[obj_id]
                if speed > 15:  # High speed
                    reasons.append("Relative speed anomaly detected (high)")
                    confidence += 25
                    behavior_score += 20
                    speed_level = "high"
                elif speed > 8:
                    reasons.append("Relative speed anomaly detected (moderate)")
                    confidence += 15
                    behavior_score += 10
                    speed_level = "moderate"
            
            # Check zigzag pattern
            has_erratic_movement = False
            if obj_id in tracker.trails and len(tracker.trails[obj_id]) > 10:
                trail = list(tracker.trails[obj_id])
                direction_changes = 0
                for i in range(1, len(trail) - 1):
                    v1 = trail[i] - trail[i-1]
                    v2 = trail[i+1] - trail[i]
                    if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                        angle = np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1))
                        if angle > np.pi / 3:  # More than 60 degrees
                            direction_changes += 1
                
                if direction_changes > 3:
                    reasons.append("Erratic movement pattern")
                    confidence += 20
                    behavior_score += 15
                    has_erratic_movement = True
            
            # Check proximity to border
            distance_to_border = abs(centroid[1] - self.border_line)
            close_to_border = False
            if distance_to_border < 50:
                reasons.append("Close to border zone")
                confidence += 15
                behavior_score += 10
                close_to_border = True
            
            # Classify based on detection type (from tracker)
            entity_type = "entity"  # Default generic term
            if obj_id in tracker.detection_classes:
                obj_class = tracker.detection_classes[obj_id]
                if obj_class in ['person']:
                    confidence += 10
                    reasons.append("Human entity detected")
                    entity_type = "human"
                elif obj_class in ['car', 'truck', 'bus', 'motorcycle']:
                    confidence += 5
                    reasons.append("Vehicle entity detected")
                    entity_type = "vehicle"
                else:
                    reasons.append("Entity detected")
            else:
                # Fallback: use generic entity term if class unknown
                reasons.append("Entity detected")
            
            # Calculate threat score (separate from confidence)
            threat_score = min(confidence + behavior_score, 100)
            
            # Generate AI summary (one-line explanation)
            summary = self._generate_summary(
                crossed_border=crossed_border if 'crossed_border' in locals() else False,
                is_night=is_night,
                speed_level=speed_level,
                has_erratic_movement=has_erratic_movement,
                close_to_border=close_to_border,
                entity_type=entity_type
            )
            
            # Determine threat level
            if confidence > 70:
                threat_level = "HIGH"
            elif confidence > 40:
                threat_level = "MEDIUM"
            else:
                threat_level = "LOW"
            
            if len(reasons) > 0:
                anomalies.append({
                    'object_id': obj_id,
                    'position': centroid,
                    'threat_level': threat_level,
                    'confidence': min(confidence, 99),
                    'threat_score': int(threat_score),
                    'reasons': reasons,
                    'summary': summary,
                    'timestamp': current_time
                })
        
        return anomalies
    
    def _generate_summary(self, crossed_border, is_night, speed_level, has_erratic_movement, close_to_border, entity_type):
        """Generate one-line AI explanation summary"""
        # Defensive guard: ensure entity_type is never None
        if not entity_type:
            entity_type = "entity"
        
        parts = []
        
        # Priority elements
        if crossed_border:
            parts.append("border crossing")
        
        if is_night:
            parts.append("night-time")
        
        if has_erratic_movement:
            parts.append("erratic")
        elif speed_level == "high":
            parts.append("high-speed")
        elif speed_level == "moderate":
            parts.append("rapid")
        
        # Entity type (with fallback)
        entity = entity_type if entity_type else "entity"
        
        # Close to border adds urgency
        proximity = "near border" if close_to_border else "movement"
        
        if len(parts) == 0:
            return f"Standard {entity} {proximity} detected"
        elif len(parts) == 1:
            return f"Suspicious {parts[0]} {entity} {proximity}"
        else:
            return f"Suspicious {' '.join(parts)} {entity} {proximity}"

def get_system_status(threat_history):
    """Calculate system status based on recent threat history"""
    if not threat_history:
        return "NORMAL", "🟢"
    
    # Look at last 10 threats
    recent = threat_history[-10:]
    high_count = sum(1 for t in recent if t['level'] == 'HIGH')
    medium_count = sum(1 for t in recent if t['level'] == 'MEDIUM')
    
    if high_count >= 3:
        return "ACTIVE THREAT ZONE", "🔴"
    elif high_count >= 1 or medium_count >= 5:
        return "ELEVATED ACTIVITY", "🟡"
    else:
        return "NORMAL", "🟢"

def load_model():
    """Load YOLO model"""
    try:
        model = YOLO('yolov8n.pt')  # Using nano model for speed
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

def process_frame(frame, model, tracker, anomaly_detector, show_trails=True, show_border=True):
    """Process a single frame with detection and tracking"""
    # Lower confidence threshold to detect more objects
    results = model(frame, conf=0.15, classes=[0, 1, 2, 3, 5, 7])  # person, bicycle, car, motorcycle, bus, truck
    
    detections = []
    detection_classes_map = {}  # Map centroid index to class
    annotated_frame = frame.copy()
    
    # Draw border line
    if show_border:
        cv2.line(annotated_frame, (0, anomaly_detector.border_line), 
                (frame.shape[1], anomaly_detector.border_line), (0, 0, 255), 2)
        cv2.putText(annotated_frame, "VIRTUAL BORDER (Configurable)", (10, anomaly_detector.border_line - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    detection_idx = 0
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            detection_class = result.names[cls]
            
            centroid_x = (x1 + x2) / 2
            centroid_y = (y1 + y2) / 2
            detections.append([centroid_x, centroid_y, conf, cls])
            detection_classes_map[detection_idx] = detection_class
            detection_idx += 1
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{detection_class}: {conf:.2f}"
            cv2.putText(annotated_frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Update tracker with detection classes
    objects = tracker.update(detections, detection_classes_map)
    
    # Draw trails and object IDs
    for obj_id, centroid in objects.items():
        cv2.circle(annotated_frame, tuple(map(int, centroid)), 4, (255, 0, 0), -1)
        cv2.putText(annotated_frame, f"ID:{obj_id}", 
                   (int(centroid[0]) + 10, int(centroid[1])),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Draw movement trail
        if show_trails and obj_id in tracker.trails:
            trail = list(tracker.trails[obj_id])
            for i in range(1, len(trail)):
                if trail[i-1] is None or trail[i] is None:
                    continue
                thickness = int(np.sqrt(32 / float(i + 1)) * 2)
                cv2.line(annotated_frame, tuple(map(int, trail[i-1])),
                        tuple(map(int, trail[i])), (0, 255, 255), thickness)
    
    # Detect anomalies (now uses per-object detection classes from tracker)
    anomalies = anomaly_detector.detect_anomalies(tracker, datetime.now())
    
    # Draw anomaly indicators
    for anomaly in anomalies:
        pos = tuple(map(int, anomaly['position']))
        color = (0, 0, 255) if anomaly['threat_level'] == "HIGH" else \
                (0, 165, 255) if anomaly['threat_level'] == "MEDIUM" else (0, 255, 0)
        cv2.circle(annotated_frame, pos, 30, color, 3)
    
    return annotated_frame, anomalies, len(detections)

def create_sample_video():
    """Create a sample video with detectable person-like shapes for demo"""
    st.info("🎬 Creating sample surveillance video...")
    
    width, height = 640, 480
    fps = 20
    duration = 10  # seconds
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_file.name, fourcc, fps, (width, height))
    
    for frame_num in range(fps * duration):
        # Create a more realistic surveillance-like frame
        frame = np.random.randint(40, 60, (height, width, 3), dtype=np.uint8)
        
        # Add some ground/background texture
        cv2.rectangle(frame, (0, height//2), (width, height), (60, 70, 60), -1)
        
        # Draw border line
        border_y = int(height * 0.5)
        cv2.line(frame, (0, border_y), (width, border_y), (100, 100, 100), 3)
        
        # Moving object 1 - Person-like shape (vertical rectangle with head)
        x1 = int(50 + (frame_num * 8)) % width
        y1 = int(250 + np.sin(frame_num * 0.15) * 60)
        
        # Draw person-like silhouette
        # Body
        cv2.rectangle(frame, (x1-15, y1-40), (x1+15, y1+20), (180, 160, 140), -1)
        # Head
        cv2.circle(frame, (x1, y1-50), 12, (200, 180, 160), -1)
        # Arms
        cv2.line(frame, (x1-15, y1-20), (x1-25, y1), (180, 160, 140), 5)
        cv2.line(frame, (x1+15, y1-20), (x1+25, y1), (180, 160, 140), 5)
        # Legs
        cv2.line(frame, (x1-5, y1+20), (x1-10, y1+50), (180, 160, 140), 6)
        cv2.line(frame, (x1+5, y1+20), (x1+10, y1+50), (180, 160, 140), 6)
        
        # Moving object 2 - Another person crossing border
        x2 = int(width - 80 - (frame_num * 6)) % width
        y2 = int(200 + np.sin(frame_num * 0.3) * 40)
        
        # Draw person-like silhouette
        cv2.rectangle(frame, (x2-15, y2-40), (x2+15, y2+20), (160, 180, 160), -1)
        cv2.circle(frame, (x2, y2-50), 12, (180, 200, 180), -1)
        cv2.line(frame, (x2-15, y2-20), (x2-25, y2), (160, 180, 160), 5)
        cv2.line(frame, (x2+15, y2-20), (x2+25, y2), (160, 180, 160), 5)
        cv2.line(frame, (x2-5, y2+20), (x2-10, y2+50), (160, 180, 160), 6)
        cv2.line(frame, (x2+5, y2+20), (x2+10, y2+50), (160, 180, 160), 6)
        
        # Add subtle motion blur
        frame = cv2.GaussianBlur(frame, (3, 3), 0)
        
        # Add slight noise for realism
        noise = np.random.randint(-10, 10, (height, width, 3), dtype=np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        out.write(frame)
    
    out.release()
    st.success("✅ Sample video created with detectable objects!")
    return temp_file.name

def main():
    # Hero Header Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-logo">🛡️</div>
        <h1 class="hero-title">SENTINEL-X</h1>
        <p style="color: #1a1a1a !important; font-size: 1.5rem; font-weight: 400; opacity: 0.8; margin: 1rem 0;">
            Autonomous Border & Coastal Intrusion Intelligence
        </p>
        <p style="color: #1a1a1a !important; font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.7;">
            Powered by Threat Intelligence Engine
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Global Disclaimer - Better styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(224, 242, 254, 0.95), rgba(186, 230, 253, 0.95)); 
                backdrop-filter: blur(10px); 
                border-radius: 15px; 
                padding: 1.2rem 2rem; 
                text-align: center; 
                margin: 1.5rem auto 2rem auto; 
                max-width: 900px;
                border: 1px solid rgba(0, 212, 255, 0.3);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
        <p style="color: #1a1a1a; font-size: 1rem; margin: 0; font-weight: 500;">
            <strong style="color: #0077b6;">ℹ️ Prototype Demonstration:</strong> 
            This is a simulated prototype demonstrating AI-based border surveillance logic.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.title("⚙️ System Configuration")
    
    mode = st.sidebar.radio("Operation Mode", 
                            ["🎥 Operational Surveillance", "📊 Post-Event Intelligence", "🎮 Demo Mode"])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Detection Settings")
    
    show_trails = st.sidebar.checkbox("Show Movement Trails", value=True)
    show_border = st.sidebar.checkbox("Show Border Line", value=True)
    show_raw = st.sidebar.checkbox("Before/After Comparison", value=False)
    
    confidence_threshold = st.sidebar.slider("Detection Confidence (%)", 0.0, 1.0, 0.3, 0.05)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Border Configuration")
    border_position = st.sidebar.slider(
        "Border Position (%)", 
        min_value=30, 
        max_value=70, 
        value=50,
        help="Adjust the virtual border line position (% from top)"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🌐 Deployment Mode")
    deployment = st.sidebar.selectbox("Select Mode", ["☁️ Cloud Processing", "⚡ Edge Computing"])
    
    if deployment == "⚡ Edge Computing":
        st.sidebar.success("✅ Edge mode enabled - Low latency processing")
    else:
        st.sidebar.info("☁️ Cloud mode - High accuracy processing")
    
    # Main content
    if mode == "🎥 Operational Surveillance":
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2.5rem;">
            <h2 style="color: #00d4ff !important; margin-bottom: 0.5rem;">🎥 Operational Surveillance Feed</h2>
            <p style="color: #1a1a1a; opacity: 0.7; font-size: 1rem;">Real-time threat detection and behavioral analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="glass-card" style="padding: 1.5rem;">
                <h4 style="color: #00d4ff !important; margin-bottom: 1rem;">📹 Video Source</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            video_source = st.radio("Select video input", 
                                   ["Upload Video", "Use Sample Video", "Webcam (Live)"],
                                   label_visibility="collapsed")
            
            video_file = None
            
            if video_source == "Upload Video":
                uploaded = st.file_uploader("Upload surveillance footage", 
                                            type=['mp4', 'avi', 'mov'])
                if uploaded:
                    video_file = uploaded
                    
            elif video_source == "Use Sample Video":
                st.markdown("""
                <div class="glass-alert-warning" style="padding: 1rem; margin: 1rem 0;">
                    <strong>⚠️ Note:</strong> Sample video uses simple shapes. For best detection results, upload real surveillance footage with people or vehicles.
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🎬 Generate Sample Video"):
                    with st.spinner("📹 Creating sample surveillance video..."):
                        video_file = create_sample_video()
                        st.session_state.sample_video_path = video_file
                        st.success("✅ Sample video created!")
                        st.rerun()
                
                # Use the stored sample video if it exists
                if 'sample_video_path' in st.session_state:
                    video_file = st.session_state.sample_video_path
            
            if video_file is not None:
                # Save uploaded file temporarily
                if isinstance(video_file, str):
                    tfile = video_file
                else:
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                    tfile.write(video_file.read())
                    tfile = tfile.name
                
                # Store video path in session state
                if 'video_path' not in st.session_state or st.session_state.video_path != tfile:
                    st.session_state.video_path = tfile
                    st.session_state.processing_complete = False
                
                # Load model
                with st.spinner("🔄 Loading AI detection model..."):
                    if not st.session_state.model_loaded:
                        model = load_model()
                        st.session_state.model = model
                        st.session_state.model_loaded = True
                    else:
                        model = st.session_state.model
                
                if model is not None:
                    # Get video properties
                    cap_info = cv2.VideoCapture(st.session_state.video_path)
                    frame_width = int(cap_info.get(cv2.CAP_PROP_FRAME_WIDTH))
                    frame_height = int(cap_info.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    total_frames = int(cap_info.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = int(cap_info.get(cv2.CAP_PROP_FPS))
                    cap_info.release()
                    
                    st.markdown(f"""
                    <div class="glass-alert-info" style="padding: 1rem;">
                        <strong>📹 Video Info:</strong> {frame_width}x{frame_height} | {total_frames} frames | {fps} FPS
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Process button - simplified
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2:
                        process_clicked = st.button("▶️ START PROCESSING", type="primary", use_container_width=True)
                    
                    if process_clicked:
                        st.info("🚀 Starting video processing...")
                        
                        # Open video for processing
                        cap = cv2.VideoCapture(st.session_state.video_path)
                        
                        if not cap.isOpened():
                            st.error(f"❌ Error opening video file: {st.session_state.video_path}")
                        else:
                            st.success("✅ Video opened successfully!")
                            
                            # Initialize tracker and anomaly detector
                            tracker = ObjectTracker()
                            anomaly_detector = AnomalyDetector(frame_width, frame_height, border_position)
                            
                            # Video display
                            video_placeholder = st.empty()
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            frame_count = 0
                            
                            try:
                                while cap.isOpened():
                                    ret, frame = cap.read()
                                    if not ret:
                                        break
                                    
                                    # Process frame
                                    annotated_frame, anomalies, num_detections = process_frame(
                                        frame, model, tracker, anomaly_detector, 
                                        show_trails, show_border
                                    )
                                    
                                    # Update event log
                                    for anomaly in anomalies:
                                        event = {
                                            'timestamp': anomaly['timestamp'].strftime("%H:%M:%S"),
                                            'id': anomaly['object_id'],
                                            'threat': anomaly['threat_level'],
                                            'confidence': f"{anomaly['confidence']:.1f}%",
                                            'threat_score': anomaly['threat_score'],
                                            'summary': anomaly['summary'],
                                            'reason': ', '.join(anomaly['reasons'])
                                        }
                                        if event not in st.session_state.event_log:
                                            st.session_state.event_log.append(event)
                                    
                                    # Performance safeguard: Cap event log size (keep most recent 200)
                                    if len(st.session_state.event_log) > 200:
                                        st.session_state.event_log = st.session_state.event_log[-200:]
                                    
                                    # Display frame
                                    if show_raw:
                                        display_frame = np.hstack([
                                            cv2.resize(frame, (frame_width//2, frame_height//2)),
                                            cv2.resize(annotated_frame, (frame_width//2, frame_height//2))
                                        ])
                                    else:
                                        display_frame = annotated_frame
                                    
                                    video_placeholder.image(display_frame, channels="BGR", use_container_width=True)
                                    
                                    # Update progress
                                    frame_count += 1
                                    progress = min(frame_count / total_frames, 1.0)
                                    progress_bar.progress(progress)
                                    status_text.markdown(f"**Processing:** Frame {frame_count}/{total_frames} | Detections: {num_detections}")
                                    
                                    # Store threat history
                                    if anomalies:
                                        max_threat = max(anomalies, key=lambda x: x['confidence'])
                                        st.session_state.threat_history.append({
                                            'frame': frame_count,
                                            'level': max_threat['threat_level'],
                                            'confidence': max_threat['confidence'],
                                            'threat_score': max_threat['threat_score']
                                        })
                                        
                                        # Performance safeguard: Cap threat history size (keep most recent 200)
                                        if len(st.session_state.threat_history) > 200:
                                            st.session_state.threat_history = st.session_state.threat_history[-200:]
                                
                                cap.release()
                                st.session_state.processing_complete = True
                                progress_bar.progress(1.0)
                                status_text.empty()
                                st.success("✅ Processing complete! Check the Threat Intelligence panel for results.")
                                
                            except Exception as e:
                                st.error(f"❌ Error during processing: {str(e)}")
                                cap.release()
                    
                    elif st.session_state.get('processing_complete', False):
                        st.info("✅ Video processed. View results in the Threat Intelligence panel or switch to Post-Event Intelligence mode.")
        
        with col2:
            st.markdown("""
            <div class="glass-card" style="padding: 1.5rem;">
                <h3 style="color: #00d4ff !important; text-align: center; margin-bottom: 1rem;">🚨 Threat Intelligence</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # System Status Badge
            system_status, status_icon = get_system_status(st.session_state.threat_history)
            st.markdown(f"""
            <div class="metric-glass-card" style="padding: 2rem;">
                <h4 style="color: #e0e0e0 !important; margin-bottom: 1rem;">{status_icon} System Status</h4>
                <div class="metric-value" style="font-size: 2rem; margin-top: 0.5rem; color: #00d4ff;">{system_status}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Current threat level
            if st.session_state.threat_history:
                latest_threat = st.session_state.threat_history[-1]
                threat_level = latest_threat['level']
                confidence = latest_threat['confidence']
                threat_score = latest_threat.get('threat_score', int(confidence))
                
                if threat_level == "HIGH":
                    st.markdown(f"""
                    <div class="threat-high" style="padding: 2rem;">
                        🔴 HIGH THREAT<br>
                        <div style="font-size: 3rem; margin: 1rem 0; text-shadow: 0 0 20px rgba(255, 68, 68, 0.5); font-weight: 900;">{threat_score}/100</div>
                        <div style="font-size: 0.95rem; opacity: 0.95;">Threat Score (0-100)</div>
                        <div style="font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;">Detection Confidence (%): {confidence:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif threat_level == "MEDIUM":
                    st.markdown(f"""
                    <div class="threat-medium" style="padding: 2rem;">
                        🟡 MEDIUM THREAT<br>
                        <div style="font-size: 3rem; margin: 1rem 0; text-shadow: 0 0 20px rgba(255, 170, 0, 0.5); font-weight: 900;">{threat_score}/100</div>
                        <div style="font-size: 0.95rem; opacity: 0.95;">Threat Score (0-100)</div>
                        <div style="font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;">Detection Confidence (%): {confidence:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="threat-low" style="padding: 2rem;">
                        🟢 LOW THREAT<br>
                        <div style="font-size: 3rem; margin: 1rem 0; text-shadow: 0 0 20px rgba(68, 255, 68, 0.5); font-weight: 900;">{threat_score}/100</div>
                        <div style="font-size: 0.95rem; opacity: 0.95;">Threat Score (0-100)</div>
                        <div style="font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;">Detection Confidence (%): {confidence:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="glass-alert-info" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem; margin-bottom: 1.5rem; opacity: 0.6;">⏳</div>
                    <div style="font-size: 1.2rem; color: #e0e0e0; font-weight: 500;">Awaiting surveillance data...</div>
                    <div style="font-size: 0.95rem; color: #e0e0e0; opacity: 0.7; margin-top: 0.5rem;">Upload or generate video to begin</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Event Log
            st.markdown("""
            <div class="glass-card" style="padding: 1.5rem;">
                <h4 style="color: #00d4ff !important; text-align: center; margin-bottom: 1rem;">📋 Threat Intelligence Log</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.session_state.event_log:
                for event in reversed(st.session_state.event_log[-10:]):
                    with st.expander(f"🔍 ID:{event['id']} - {event['threat']} ({event['timestamp']})"):
                        # AI Summary at top
                        if 'summary' in event:
                            st.markdown(f"""
                            <div class="glass-alert-info" style="padding: 1rem; margin-bottom: 1rem;">
                                <strong style="color: #00d4ff; font-size: 1rem;">🤖 AI Analysis:</strong><br>
                                <em style="font-size: 1.05rem; color: #e0e0e0; line-height: 1.6;">{event['summary']}</em>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="glass-card" style="margin-top: 0.5rem; padding: 1rem;">
                            <div style="color: #e0e0e0; line-height: 1.8;">
                                <strong style="color: #00d4ff;">Threat Score (0-100):</strong> {event.get('threat_score', 'N/A')}/100<br>
                                <strong style="color: #00d4ff;">Detection Confidence (%):</strong> {event['confidence']}<br>
                                <strong style="color: #00d4ff;">Detailed Analysis:</strong> {event['reason']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="glass-alert-warning" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.6;">📭</div>
                    <div style="font-size: 1.1rem; color: #e0e0e0;">No threats detected yet</div>
                    <div style="font-size: 0.9rem; color: #e0e0e0; opacity: 0.7; margin-top: 0.5rem;">Process surveillance feed to populate log</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Clear log button
            if st.button("🗑️ Clear Event Log"):
                st.session_state.event_log = []
                st.rerun()
    
    elif mode == "📊 Post-Event Intelligence":
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2.5rem;">
            <h2 style="color: #00d4ff !important; margin-bottom: 0.5rem;">📊 Post-Event Intelligence Analysis</h2>
            <p style="color: #1a1a1a; opacity: 0.7; font-size: 1rem;">Comprehensive threat analysis and mission review</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not st.session_state.threat_history:
            st.markdown("""
            <div class="glass-alert-info" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⏳</div>
                <strong>No surveillance data available.</strong><br>
                <span style="opacity: 0.8;">Process a video in Operational Surveillance mode first.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_events = len(st.session_state.event_log)
            high_threats = sum(1 for e in st.session_state.event_log if e['threat'] == 'HIGH')
            medium_threats = sum(1 for e in st.session_state.event_log if e['threat'] == 'MEDIUM')
            avg_confidence = np.mean([e.get('confidence', 0) for e in st.session_state.threat_history]) if st.session_state.threat_history else 0
            
            col1.metric("Total Events", total_events)
            col2.metric("High Threats", high_threats, delta=f"{high_threats/max(total_events,1)*100:.0f}%")
            col3.metric("Medium Threats", medium_threats)
            col4.metric("Avg Detection Confidence (%)", f"{avg_confidence:.1f}%")
            
            st.markdown("---")
            
            # Threat Timeline
            st.subheader("📈 Threat Timeline")
            
            df_threats = pd.DataFrame(st.session_state.threat_history)
            
            if not df_threats.empty:
                # Create visualization data
                threat_levels = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
                df_threats['level_num'] = df_threats['level'].map(threat_levels)
                
                st.line_chart(df_threats[['frame', 'confidence']].set_index('frame'))
            
            st.markdown("---")
            
            # Event Table
            st.subheader("📊 Detailed Event Analysis")
            if st.session_state.event_log:
                df_events = pd.DataFrame(st.session_state.event_log)
                st.dataframe(df_events, use_container_width=True)
                
                # Download button
                csv = df_events.to_csv(index=False)
                st.download_button(
                    label="📥 Download Report (CSV)",
                    data=csv,
                    file_name=f"sentinel_x_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    else:  # Demo Mode
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h2 style="color: #00d4ff !important;">🎮 Demo Mode - Interactive Simulation</h2>
            <h4 style="color: #e0e0e0 !important; margin-top: 1rem;">🎯 Simulation of Real-World Border Intrusion Scenario</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-alert-info">
            <strong>Demo Features:</strong>
            <ul style="margin-top: 0.5rem;">
                <li>Simulated border surveillance scenario</li>
                <li>Real-time threat intelligence detection</li>
                <li>Interactive threat assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: #00d4ff !important; text-align: center;">Simulated Surveillance Zone</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Create demo visualization
            demo_frame = np.zeros((400, 600, 3), dtype=np.uint8)
            demo_frame[:] = (10, 15, 30)  # Dark background
            
            # Border line
            cv2.line(demo_frame, (0, 200), (600, 200), (0, 212, 255), 3)
            cv2.putText(demo_frame, "BORDER LINE", (10, 190), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 212, 255), 2)
            
            # Simulate some objects
            positions = [(100, 150), (300, 180), (450, 220), (200, 300)]
            colors = [(0, 212, 255), (0, 180, 216), (255, 68, 68), (68, 255, 68)]
            for i, (pos, color) in enumerate(zip(positions, colors)):
                cv2.circle(demo_frame, pos, 15, color, -1)
                cv2.putText(demo_frame, f"ID:{i}", (pos[0]+20, pos[1]), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            st.image(demo_frame, channels="BGR", use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: #00d4ff !important; text-align: center;">System Capabilities</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="glass-alert-success" style="margin: 0.5rem 0;">✅ Multi-modal Vision</div>
            <div class="glass-alert-success" style="margin: 0.5rem 0;">✅ Real-time Detection</div>
            <div class="glass-alert-success" style="margin: 0.5rem 0;">✅ Movement Tracking</div>
            <div class="glass-alert-success" style="margin: 0.5rem 0;">✅ Threat Intelligence Engine</div>
            <div class="glass-alert-success" style="margin: 0.5rem 0;">✅ Threat Classification</div>
            <div class="glass-alert-success" style="margin: 0.5rem 0;">✅ Explainable AI</div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-glass-card">
                <h4 style="color: #e0e0e0 !important;">Detection Types</h4>
                <div style="margin-top: 1rem;">
                    <span class="tech-badge">🚶 Human Detection</span>
                    <span class="tech-badge">🚗 Vehicle Detection</span>
                    <span class="tech-badge">🌊 Maritime Objects</span>
                    <span class="tech-badge">✈️ Aerial Objects</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="footer">
        <div class="hero-logo" style="font-size: 3rem;">🛡️</div>
        <h2 style="color: #00d4ff !important; margin: 1rem 0;">SENTINEL-X</h2>
        <p style="font-size: 1.3rem; color: #1a1a1a !important; margin-bottom: 1.5rem; opacity: 0.8;">
            Autonomous Border & Coastal Intrusion Intelligence
        </p>
        <div style="margin: 1.5rem 0;">
            <span class="tech-badge">🤖 YOLOv8</span>
            <span class="tech-badge">⚡ Threat Intelligence Engine</span>
            <span class="tech-badge">🎯 Behavioral Analysis</span>
            <span class="tech-badge">🚀 Real-time Processing</span>
        </div>
        <div style="margin: 2rem 0;">
            <a href="#" style="color: #0077b6; text-decoration: none; margin: 0 1rem; transition: opacity 0.3s;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'">GitHub</a>
            <a href="#" style="color: #0077b6; text-decoration: none; margin: 0 1rem; transition: opacity 0.3s;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'">Documentation</a>
            <a href="#" style="color: #0077b6; text-decoration: none; margin: 0 1rem; transition: opacity 0.3s;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'">API</a>
            <a href="#" style="color: #0077b6; text-decoration: none; margin: 0 1rem; transition: opacity 0.3s;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'">Contact</a>
        </div>
        <p style="opacity: 0.7; font-size: 0.95rem; margin-top: 2rem; color: #1a1a1a !important;">
            Built for Border Security Innovation | Hackathon 2025<br>
            Powered by YOLOv8 + Threat Intelligence Engine + Streamlit | © 2025 Sentinel-X
        </p>
        <p style="opacity: 0.6; font-size: 0.85rem; margin-top: 1rem; color: #1a1a1a !important;">
            Version 2.0.0 | Defense-Grade AI
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Initialize session state
    if 'event_log' not in st.session_state:
        st.session_state.event_log = []
    if 'threat_history' not in st.session_state:
        st.session_state.threat_history = []
    if 'frame_count' not in st.session_state:
        st.session_state.frame_count = 0
    if 'model_loaded' not in st.session_state:
        st.session_state.model_loaded = False
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
    if 'sample_video_path' not in st.session_state:
        st.session_state.sample_video_path = None
    
    main()

