#!/usr/bin/env python3
"""
Generate sample prediction requests to populate metrics with data.
"""

import requests
import time
import random
import json

def generate_sample_requests():
    """Generate sample prediction requests to populate metrics."""
    base_url = "http://127.0.0.1:8000"
    
    # Sample data variations for California housing
    sample_variations = [
        {
            "total_rooms": 4500.0,
            "total_bedrooms": 900.0,
            "population": 3000.0,
            "households": 1000.0,
            "median_income": 5.5,
            "housing_median_age": 26.0,
            "latitude": 37.86,
            "longitude": -122.27,
        },
        {
            "total_rooms": 3200.0,
            "total_bedrooms": 650.0,
            "population": 2100.0,
            "households": 750.0,
            "median_income": 4.2,
            "housing_median_age": 35.0,
            "latitude": 34.05,
            "longitude": -118.24,
        },
        {
            "total_rooms": 6800.0,
            "total_bedrooms": 1200.0,
            "population": 4500.0,
            "households": 1500.0,
            "median_income": 8.1,
            "housing_median_age": 15.0,
            "latitude": 37.77,
            "longitude": -122.42,
        },
        {
            "total_rooms": 2800.0,
            "total_bedrooms": 580.0,
            "population": 1800.0,
            "households": 620.0,
            "median_income": 3.8,
            "housing_median_age": 42.0,
            "latitude": 32.71,
            "longitude": -117.16,
        },
        {
            "total_rooms": 5200.0,
            "total_bedrooms": 1050.0,
            "population": 3500.0,
            "households": 1200.0,
            "median_income": 6.7,
            "housing_median_age": 28.0,
            "latitude": 37.39,
            "longitude": -122.08,
        }
    ]
    
    print("🚀 Generating sample prediction requests...")
    
    successful_requests = 0
    failed_requests = 0
    
    for i in range(20):  # Generate 20 sample requests
        try:
            # Pick a random sample and add some variation
            base_sample = random.choice(sample_variations)
            sample = base_sample.copy()
            
            # Add small random variations
            sample["total_rooms"] *= random.uniform(0.8, 1.2)
            sample["total_bedrooms"] *= random.uniform(0.8, 1.2)
            sample["population"] *= random.uniform(0.8, 1.2)
            sample["households"] *= random.uniform(0.8, 1.2)
            sample["median_income"] *= random.uniform(0.9, 1.1)
            sample["housing_median_age"] *= random.uniform(0.9, 1.1)
            sample["latitude"] += random.uniform(-0.1, 0.1)
            sample["longitude"] += random.uniform(-0.1, 0.1)
            
            # Make prediction request
            response = requests.post(f"{base_url}/predict", json=sample, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                predicted_price = result.get('predicted_price', 'N/A')
                print(f"✅ Request {i+1}: Predicted price = {predicted_price}")
                successful_requests += 1
            else:
                print(f"❌ Request {i+1}: HTTP {response.status_code}")
                failed_requests += 1
                
            # Small delay between requests
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Request {i+1}: {e}")
            failed_requests += 1
    
    print(f"\n📊 Summary:")
    print(f"- Successful requests: {successful_requests}")
    print(f"- Failed requests: {failed_requests}")
    print(f"- Total requests: {successful_requests + failed_requests}")
    
    return successful_requests, failed_requests

def check_updated_metrics():
    """Check the updated metrics after generating sample data."""
    print("\n🔍 Checking updated metrics...")
    
    try:
        # Check app metrics
        response = requests.get("http://127.0.0.1:8000/app-metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            print(f"✅ App metrics - Total predictions: {metrics.get('total_predictions', 'N/A')}")
        
        # Check Prometheus metrics for our custom metrics
        response = requests.get("http://127.0.0.1:8000/metrics", timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            
            # Look for our custom metrics
            custom_metrics = [
                "mlops_api_requests_total",
                "mlops_model_predictions_total", 
                "mlops_model_prediction_latency_seconds",
                "mlops_daily_predictions"
            ]
            
            for metric in custom_metrics:
                if metric in metrics_text:
                    print(f"✅ Prometheus metric found: {metric}")
                else:
                    print(f"⚠️  Prometheus metric not found: {metric}")
        
    except Exception as e:
        print(f"❌ Error checking metrics: {e}")

def main():
    """Main function."""
    print("📈 MLOps Housing Pipeline - Sample Data Generator")
    print("=" * 55)
    
    # Check if API is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code != 200:
            print("❌ API server is not responding properly")
            return
    except:
        print("❌ API server is not running. Start it with:")
        print("   uvicorn api.housing_api:app --host 127.0.0.1 --port 8000")
        return
    
    print("✅ API server is running")
    
    # Generate sample requests
    successful, failed = generate_sample_requests()
    
    if successful > 0:
        # Check updated metrics
        check_updated_metrics()
        
        print(f"\n🎯 Metrics populated with {successful} predictions!")
        print("🌐 View metrics at:")
        print("   - App metrics: http://127.0.0.1:8000/app-metrics")
        print("   - Prometheus metrics: http://127.0.0.1:8000/metrics")
        print("   - Prometheus UI: http://localhost:9090")
        print("   - Grafana dashboard: http://localhost:3001")

if __name__ == "__main__":
    main()
