"""
Test script for the Drone Vision Backend
Validates all endpoints and performance metrics
"""

import requests
import time
import cv2
import numpy as np
from io import BytesIO

BASE_URL = "http://localhost:5000"

def create_test_image():
    """Create a test image with a simple pattern"""
    img = np.ones((640, 640, 3), dtype=np.uint8) * 128
    cv2.rectangle(img, (100, 100), (500, 500), (0, 255, 0), 3)
    cv2.putText(img, "TEST", (250, 320), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    # Encode to JPEG
    _, buffer = cv2.imencode('.jpg', img)
    return BytesIO(buffer)

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Status: {data['status']}")
    print(f"✓ Version: {data['version']}")
    print(f"✓ Model: {data['model']}")
    print()

def test_predict():
    """Test the prediction endpoint"""
    print("Testing prediction endpoint...")
    test_img = create_test_image()
    
    files = {'file': ('test.jpg', test_img, 'image/jpeg')}
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/predict", files=files)
    elapsed = time.time() - start_time
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Response time: {elapsed*1000:.2f}ms")
    print(f"✓ Detections: {len(data['detections'])}")
    print(f"✓ Inference time: {data['research_metrics'].get('inference_time_ms', 'N/A')}ms")
    print(f"✓ Preprocessing time: {data['research_metrics'].get('preprocessing_time_ms', 'N/A')}ms")
    print()

def test_stream():
    """Test the streaming endpoint"""
    print("Testing stream endpoint...")
    test_img = create_test_image()
    
    for i in range(3):
        test_img.seek(0)
        files = {'file': ('frame.jpg', test_img, 'image/jpeg')}
        data = {'frame_idx': str(i)}
        
        response = requests.post(f"{BASE_URL}/stream", files=files, data=data)
        assert response.status_code == 200
        
        result = response.json()
        if result.get('skipped'):
            print(f"  Frame {i}: Skipped (as expected)")
        else:
            print(f"  Frame {i}: Processed, FPS: {result['metrics'].get('fps', 'N/A')}")
    
    print()

def test_metrics():
    """Test the metrics endpoint"""
    print("Testing metrics endpoint...")
    response = requests.get(f"{BASE_URL}/metrics")
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Total requests: {data['processing_metrics']['total_requests']}")
    print(f"✓ Frames processed: {data['processing_metrics']['total_frames_processed']}")
    print(f"✓ Average FPS: {data['performance_metrics']['average_fps']}")
    print(f"✓ Error count: {data['processing_metrics']['error_count']}")
    print()

def test_config():
    """Test the configuration endpoint"""
    print("Testing configuration endpoint...")
    
    # Get current config
    response = requests.get(f"{BASE_URL}/config")
    assert response.status_code == 200
    config = response.json()
    print(f"✓ Current frame_skip_rate: {config['frame_skip_rate']}")
    
    # Update config
    new_config = {'frame_skip_rate': 3}
    response = requests.post(f"{BASE_URL}/config", json=new_config)
    assert response.status_code == 200
    
    # Verify update
    response = requests.get(f"{BASE_URL}/config")
    updated_config = response.json()
    assert updated_config['frame_skip_rate'] == 3
    print(f"✓ Updated frame_skip_rate: {updated_config['frame_skip_rate']}")
    
    # Reset
    requests.post(f"{BASE_URL}/config", json={'frame_skip_rate': 2})
    print()

def run_performance_test():
    """Run a performance benchmark"""
    print("Running performance benchmark...")
    test_img = create_test_image()
    
    times = []
    for i in range(10):
        test_img.seek(0)
        files = {'file': ('test.jpg', test_img, 'image/jpeg')}
        
        start = time.time()
        response = requests.post(f"{BASE_URL}/predict", files=files)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            times.append(elapsed)
    
    if times:
        avg_time = sum(times) / len(times)
        fps = 1.0 / avg_time
        print(f"✓ Average processing time: {avg_time*1000:.2f}ms")
        print(f"✓ Average FPS: {fps:.2f}")
        print(f"✓ Min time: {min(times)*1000:.2f}ms")
        print(f"✓ Max time: {max(times)*1000:.2f}ms")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Drone Vision Backend - Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_health_check()
        test_predict()
        test_stream()
        test_metrics()
        test_config()
        run_performance_test()
        
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to server.")
        print("  Make sure the server is running on", BASE_URL)
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
