"""
Real-Time Animal Detection System using YOLOv8 and OpenCV
Research-Grade Implementation for Drone Vision Applications

Author: Research Team
Date: 2024
Institution: OpenCV Project

This module implements a robust real-time object detection pipeline optimized
for minimal latency and maximum throughput using:
- YOLOv8 (Ultralytics) for state-of-the-art object detection
- OpenCV for advanced image preprocessing and enhancement
- Adaptive frame skipping for real-time performance
- Comprehensive performance metrics and logging
"""

import io
import time
import logging
import threading
from collections import deque
from datetime import datetime
from typing import Tuple, Dict, List, Optional, Any

import cv2
import numpy as np
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image
import base64

from facts import get_fact

# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

# Configure logging for research-grade tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('drone_vision.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app connectivity

# Performance tracking
performance_metrics = {
    'total_requests': 0,
    'total_frames_processed': 0,
    'average_inference_time': 0.0,
    'average_preprocessing_time': 0.0,
    'total_processing_time': 0.0,
    'fps_history': deque(maxlen=100),  # Track last 100 FPS measurements
    'error_count': 0,
    'start_time': datetime.now()
}

# Thread lock for metrics updates
metrics_lock = threading.Lock()

# Real-time processing configuration
REAL_TIME_CONFIG = {
    'frame_skip_rate': 2,  # Process every Nth frame for real-time performance
    'target_fps': 15,  # Target frames per second
    'conf_threshold': 0.25,  # YOLO confidence threshold
    'max_frame_size': (1280, 720),  # Max resolution for performance
    'enable_thermal': True,
    'enable_clahe': True,
    'enable_blur_detection': True
}

# ============================================================================
# MODEL LOADING
# ============================================================================

logger.info("Initializing YOLOv8 Model (Large) for optimal accuracy...")
try:
    model = YOLO('yolov8l.pt')
    # Warm up model with dummy inference
    dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
    _ = model(dummy_img, verbose=False)
    logger.info("✓ Model loaded and warmed up successfully")
except Exception as e:
    logger.error(f"✗ Model loading failed: {e}")
    raise

# ============================================================================
# PREPROCESSING PIPELINE (Research-Grade OpenCV)
# ============================================================================

def compute_image_quality_metrics(img_bgr: np.ndarray) -> Dict[str, float]:
    """
    Compute comprehensive image quality metrics for research analysis.
    
    Args:
        img_bgr: Input image in BGR format
        
    Returns:
        Dictionary containing quality metrics
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # 1. Blur Detection (Laplacian Variance)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # 2. Brightness Analysis
    brightness_mean = np.mean(gray)
    brightness_std = np.std(gray)
    
    # 3. Contrast Analysis (Standard Deviation)
    contrast = np.std(gray)
    
    # 4. Sharpness (Gradient Magnitude)
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sharpness = np.sqrt(grad_x**2 + grad_y**2).mean()
    
    return {
        'blur_score': round(float(laplacian_var), 2),
        'brightness_mean': round(float(brightness_mean), 2),
        'brightness_std': round(float(brightness_std), 2),
        'contrast': round(float(contrast), 2),
        'sharpness': round(float(sharpness), 2)
    }


def apply_clahe_enhancement(img_bgr: np.ndarray) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
    in LAB color space to preserve color balance.
    
    Args:
        img_bgr: Input image in BGR format
        
    Returns:
        Enhanced image in BGR format
    """
    if not REAL_TIME_CONFIG['enable_clahe']:
        return img_bgr
        
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel only
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    
    lab_enhanced = cv2.merge((l_enhanced, a, b))
    img_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    
    return img_enhanced


def generate_thermal_visualization(img_bgr: np.ndarray) -> Tuple[np.ndarray, str]:
    """
    Generate thermal-style visualization using color mapping.
    
    Args:
        img_bgr: Input image in BGR format
        
    Returns:
        Tuple of (thermal image array, base64 encoded string)
    """
    if not REAL_TIME_CONFIG['enable_thermal']:
        return img_bgr, ""
        
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    thermal_sim = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    
    # Encode to base64 for transmission
    _, buffer = cv2.imencode('.jpg', thermal_sim, [cv2.IMWRITE_JPEG_QUALITY, 85])
    thermal_b64 = base64.b64encode(buffer).decode('utf-8')
    
    return thermal_sim, thermal_b64


def preprocess_frame(img_bgr: np.ndarray, frame_idx: int = 0) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Research-grade preprocessing pipeline for optimal detection performance.
    
    Args:
        img_bgr: Input frame in BGR format
        frame_idx: Frame index for tracking
        
    Returns:
        Tuple of (PIL Image for YOLO, metrics dictionary)
    """
    start_time = time.time()
    
    # Resize if too large for performance
    h, w = img_bgr.shape[:2]
    max_w, max_h = REAL_TIME_CONFIG['max_frame_size']
    if w > max_w or h > max_h:
        scale = min(max_w / w, max_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img_bgr = cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Compute quality metrics
    quality_metrics = compute_image_quality_metrics(img_bgr) if REAL_TIME_CONFIG['enable_blur_detection'] else {}
    
    # Apply CLAHE enhancement
    img_enhanced = apply_clahe_enhancement(img_bgr)
    
    # Generate thermal visualization
    thermal_img, thermal_b64 = generate_thermal_visualization(img_bgr)
    
    # Convert to RGB for YOLO (PIL format)
    img_rgb = cv2.cvtColor(img_enhanced, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    
    preprocessing_time = time.time() - start_time
    
    metrics = {
        **quality_metrics,
        'resolution': f"{img_bgr.shape[1]}x{img_bgr.shape[0]}",
        'preprocessing_time_ms': round(preprocessing_time * 1000, 2),
        'processor': 'OpenCV + YOLOv8-Large',
        'frame_index': frame_idx
    }
    
    return pil_img, metrics


def research_preprocess(file: io.BytesIO) -> Tuple[Image.Image, str, Dict[str, Any]]:
    """
    Legacy support for single image preprocessing (backward compatibility).
    
    Args:
        file: File-like object containing image data
        
    Returns:
        Tuple of (PIL Image, thermal base64, metrics)
    """
    file.seek(0)
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if img_bgr is None:
        raise ValueError("Failed to decode image")
    
    pil_img, metrics = preprocess_frame(img_bgr)
    _, thermal_b64 = generate_thermal_visualization(img_bgr)
    
    return pil_img, thermal_b64, metrics


# ============================================================================
# INFERENCE PIPELINE
# ============================================================================

def run_detection(pil_img: Image.Image, conf_threshold: float = None) -> Tuple[Any, float]:
    """
    Run YOLO inference with performance tracking.
    
    Args:
        pil_img: PIL Image ready for inference
        conf_threshold: Confidence threshold (uses config default if None)
        
    Returns:
        Tuple of (YOLO results, inference time in seconds)
    """
    start_time = time.time()
    conf = conf_threshold if conf_threshold is not None else REAL_TIME_CONFIG['conf_threshold']
    
    results = model(pil_img, conf=conf, verbose=False, imgsz=640)
    inference_time = time.time() - start_time
    
    return results, inference_time


def process_detections(results: Any, model: YOLO) -> Tuple[List[Dict], Optional[Dict]]:
    """
    Process YOLO detection results into structured format.
    
    Args:
        results: YOLO inference results
        model: YOLO model instance
        
    Returns:
        Tuple of (list of all detections, best match detection)
    """
    detections = []
    
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]
                
                details = get_fact(label)
                detections.append({
                    'label': label,
                    'confidence': confidence,
                    'bbox': bbox,
                    'details': details
                })
    
    best_match = sorted(detections, key=lambda x: x['confidence'], reverse=True)[0] if detections else None
    
    return detections, best_match


def update_performance_metrics(preprocessing_time: float, inference_time: float, 
                               frame_count: int = 1) -> None:
    """Update global performance metrics thread-safely."""
    with metrics_lock:
        performance_metrics['total_frames_processed'] += frame_count
        performance_metrics['total_processing_time'] += preprocessing_time + inference_time
        
        if performance_metrics['total_frames_processed'] > 0:
            performance_metrics['average_preprocessing_time'] = (
                performance_metrics['total_processing_time'] * 
                (1 - inference_time / (preprocessing_time + inference_time)) /
                performance_metrics['total_frames_processed']
            )
            performance_metrics['average_inference_time'] = (
                performance_metrics['total_processing_time'] * 
                (inference_time / (preprocessing_time + inference_time)) /
                performance_metrics['total_frames_processed']
            )
        
        # Calculate FPS
        total_time = preprocessing_time + inference_time
        if total_time > 0:
            fps = 1.0 / total_time
            performance_metrics['fps_history'].append(fps)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Health check and system status endpoint."""
    uptime = (datetime.now() - performance_metrics['start_time']).total_seconds()
    
    avg_fps = 0.0
    if performance_metrics['fps_history']:
        avg_fps = np.mean(list(performance_metrics['fps_history']))
    
    return jsonify({
        'status': 'Drone Vision Backend Running',
        'version': '2.0.0-research',
        'model': 'YOLOv8-Large',
        'uptime_seconds': round(uptime, 2),
        'performance': {
            'total_requests': performance_metrics['total_requests'],
            'total_frames_processed': performance_metrics['total_frames_processed'],
            'average_fps': round(avg_fps, 2),
            'average_inference_time_ms': round(performance_metrics['average_inference_time'] * 1000, 2),
            'error_count': performance_metrics['error_count']
        },
        'config': REAL_TIME_CONFIG
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Single image prediction endpoint with comprehensive preprocessing.
    Optimized for real-time performance with minimal latency.
    """
    global performance_metrics
    
    start_request = time.time()
    performance_metrics['total_requests'] += 1
    
    try:
        if 'file' not in request.files:
            performance_metrics['error_count'] += 1
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            performance_metrics['error_count'] += 1
            return jsonify({'error': 'Empty file'}), 400
        
        # Preprocessing
        try:
            pil_img, thermal_b64, metrics = research_preprocess(file)
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            performance_metrics['error_count'] += 1
            return jsonify({'error': f'Image processing failed: {str(e)}'}), 500
        
        preprocessing_time = metrics.get('preprocessing_time_ms', 0) / 1000.0
        
        # Inference
        results, inference_time = run_detection(pil_img)
        
        # Process results
        detections, best_match = process_detections(results, model)
        
        # Generate annotated frame
        annotated_frame = results[0].plot()  # Returns BGR numpy array
        _, buffer_anno = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        annotated_b64 = base64.b64encode(buffer_anno).decode('utf-8')
        
            # Update metrics
        update_performance_metrics(preprocessing_time, inference_time)
        
        total_time = time.time() - start_request
        
        logger.info(f"Request processed in {total_time*1000:.2f}ms "
                   f"(preprocessing: {preprocessing_time*1000:.2f}ms, "
                   f"inference: {inference_time*1000:.2f}ms), "
                   f"detections: {len(detections)}")
        
        return jsonify({
            'detections': detections,
            'best_match': best_match,
            'research_metrics': {
                **metrics,
                'inference_time_ms': round(inference_time * 1000, 2),
                'total_processing_time_ms': round(total_time * 1000, 2)
            },
            'thermal_image': thermal_b64,
            'annotated_image': annotated_b64,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        performance_metrics['error_count'] += 1
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/stream', methods=['POST'])
def stream_detections():
    """
    Real-time video stream processing endpoint.
    Accepts frames sequentially and returns detections with minimal latency.
    Optimized with adaptive frame skipping for real-time performance.
    """
    global performance_metrics
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No frame data'}), 400
        
        file = request.files['file']
        frame_idx = int(request.form.get('frame_idx', 0))
        
        # Adaptive frame skipping for real-time performance
        skip_rate = REAL_TIME_CONFIG['frame_skip_rate']
        if frame_idx % skip_rate != 0:
            return jsonify({
                'skipped': True,
                'frame_idx': frame_idx,
                'message': 'Frame skipped for real-time performance'
            }), 200
        
        # Decode frame
        file.seek(0)
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if img_bgr is None:
            return jsonify({'error': 'Invalid frame data'}), 400
        
        # Preprocess
        pil_img, metrics = preprocess_frame(img_bgr, frame_idx)
        preprocessing_time = metrics.get('preprocessing_time_ms', 0) / 1000.0
        
        # Inference
        results, inference_time = run_detection(pil_img)
        detections, best_match = process_detections(results, model)
        
        # Generate annotated frame (lightweight for streaming)
        annotated_frame = results[0].plot()
        _, buffer_anno = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        annotated_b64 = base64.b64encode(buffer_anno).decode('utf-8')
        
        # Update metrics
        update_performance_metrics(preprocessing_time, inference_time)
        performance_metrics['total_frames_processed'] += 1
        
        return jsonify({
            'detections': detections,
            'best_match': best_match,
            'annotated_image': annotated_b64,
            'frame_idx': frame_idx,
            'metrics': {
                **metrics,
                'inference_time_ms': round(inference_time * 1000, 2),
                'fps': round(1.0 / (preprocessing_time + inference_time), 2)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Stream processing error: {e}", exc_info=True)
        performance_metrics['error_count'] += 1
        return jsonify({'error': f'Stream processing failed: {str(e)}'}), 500


@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Research endpoint for performance metrics and analytics."""
    uptime = (datetime.now() - performance_metrics['start_time']).total_seconds()
    
    avg_fps = 0.0
    if performance_metrics['fps_history']:
        fps_list = list(performance_metrics['fps_history'])
        avg_fps = np.mean(fps_list)
        min_fps = np.min(fps_list)
        max_fps = np.max(fps_list)
    else:
        min_fps = 0.0
        max_fps = 0.0
    
    return jsonify({
        'system_metrics': {
            'uptime_seconds': round(uptime, 2),
            'uptime_hours': round(uptime / 3600, 2),
            'start_time': performance_metrics['start_time'].isoformat(),
            'current_time': datetime.now().isoformat()
        },
        'processing_metrics': {
            'total_requests': performance_metrics['total_requests'],
            'total_frames_processed': performance_metrics['total_frames_processed'],
            'average_inference_time_ms': round(performance_metrics['average_inference_time'] * 1000, 2),
            'average_preprocessing_time_ms': round(performance_metrics['average_preprocessing_time'] * 1000, 2),
            'error_count': performance_metrics['error_count'],
            'error_rate': round(performance_metrics['error_count'] / max(performance_metrics['total_requests'], 1), 4)
        },
        'performance_metrics': {
            'average_fps': round(avg_fps, 2),
            'min_fps': round(min_fps, 2),
            'max_fps': round(max_fps, 2),
            'fps_samples': len(performance_metrics['fps_history'])
        },
        'configuration': REAL_TIME_CONFIG
    })


@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration management endpoint."""
    if request.method == 'GET':
        return jsonify(REAL_TIME_CONFIG)
    
    # POST: Update configuration
    try:
        new_config = request.json
        for key, value in new_config.items():
            if key in REAL_TIME_CONFIG:
                REAL_TIME_CONFIG[key] = value
                logger.info(f"Updated config: {key} = {value}")
        
        return jsonify({
            'status': 'Configuration updated',
            'config': REAL_TIME_CONFIG
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Drone Vision Backend - Research Edition")
    logger.info("Real-Time Animal Detection System")
    logger.info("=" * 60)
    logger.info(f"Model: YOLOv8-Large")
    logger.info(f"Target FPS: {REAL_TIME_CONFIG['target_fps']}")
    logger.info(f"Frame Skip Rate: {REAL_TIME_CONFIG['frame_skip_rate']}")
    logger.info(f"Confidence Threshold: {REAL_TIME_CONFIG['conf_threshold']}")
    logger.info("=" * 60)
    logger.info("Starting server on 0.0.0.0:5000...")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Disable debug mode for production
        threaded=True,  # Enable threading for concurrent requests
        use_reloader=False
    )