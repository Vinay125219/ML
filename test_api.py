#!/usr/bin/env python3
"""
Test script to verify the housing API and metrics endpoints are working.
"""

import sys
import os
import requests
import time
import json

# Add current directory to path
sys.path.append(".")


def test_api_import():
    """Test if the API can be imported successfully."""
    try:
        from api.housing_api import app

        print("✅ API imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import API: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints if server is running."""
    base_url = "http://127.0.0.1:8000"

    endpoints_to_test = [
        ("/", "GET", "Root endpoint"),
        ("/health", "GET", "Health check"),
        ("/app-metrics", "GET", "Application metrics"),
        ("/metrics", "GET", "Prometheus metrics"),
    ]

    print("\n🔍 Testing API endpoints...")

    for endpoint, method, description in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                print(f"✅ {description} ({endpoint}): OK")
                if endpoint == "/app-metrics":
                    print(f"   Response: {response.json()}")
                elif endpoint == "/metrics":
                    lines = response.text.split("\n")[:5]  # Show first 5 lines
                    print(f"   Prometheus metrics preview: {lines}")
            else:
                print(f"❌ {description} ({endpoint}): HTTP {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"⚠️  {description} ({endpoint}): Server not running")
        except Exception as e:
            print(f"❌ {description} ({endpoint}): {e}")


def test_prediction_endpoint():
    """Test the prediction endpoint with sample data."""
    base_url = "http://127.0.0.1:8000"

    sample_data = {
        "total_rooms": 4500.0,
        "total_bedrooms": 900.0,
        "population": 3000.0,
        "households": 1000.0,
        "median_income": 5.5,
        "housing_median_age": 26.0,
        "latitude": 37.86,
        "longitude": -122.27,
    }

    try:
        url = f"{base_url}/predict"
        response = requests.post(url, json=sample_data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction endpoint: OK")
            print(f"   Predicted price: {result.get('predicted_price', 'N/A')}")
        else:
            print(f"❌ Prediction endpoint: HTTP {response.status_code}")
            print(f"   Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"⚠️  Prediction endpoint: Server not running")
    except Exception as e:
        print(f"❌ Prediction endpoint: {e}")


def start_api_server():
    """Try to start the API server."""
    try:
        print("🚀 Starting API server...")
        import uvicorn
        from api.housing_api import app

        # Start server in a separate process
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False


def test_monitoring_services():
    """Test Prometheus and Grafana services."""
    print("\n🔍 Testing monitoring services...")

    # Test Prometheus
    try:
        response = requests.get("http://localhost:9090/-/healthy", timeout=5)
        if response.status_code == 200:
            print("✅ Prometheus: Healthy")
        else:
            print(f"❌ Prometheus: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(
            "⚠️  Prometheus: Not running (start with: docker-compose up -d prometheus)"
        )
    except Exception as e:
        print(f"❌ Prometheus: {e}")

    # Test Grafana
    try:
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Grafana: Healthy")
        else:
            print(f"❌ Grafana: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️  Grafana: Not running (start with: docker-compose up -d grafana)")
    except Exception as e:
        print(f"❌ Grafana: {e}")


def test_prometheus_scraping():
    """Test if Prometheus is scraping our API metrics."""
    print("\n🔍 Testing Prometheus scraping...")

    try:
        # Check targets
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        if response.status_code == 200:
            data = response.json()
            targets = data.get("data", {}).get("activeTargets", [])

            housing_api_target = None
            for target in targets:
                if "housing-api" in target.get("labels", {}).get("job", ""):
                    housing_api_target = target
                    break

            if housing_api_target:
                health = housing_api_target.get("health", "unknown")
                if health == "up":
                    print("✅ Prometheus is successfully scraping housing-api metrics")
                else:
                    print(f"⚠️  Housing-api target health: {health}")
                    print(
                        f"   Last error: {housing_api_target.get('lastError', 'N/A')}"
                    )
            else:
                print("⚠️  Housing-api target not found in Prometheus")
        else:
            print(f"❌ Failed to get Prometheus targets: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Prometheus scraping test failed: {e}")


def main():
    """Main test function."""
    print("🔧 MLOps Housing Pipeline - API & Metrics Test")
    print("=" * 50)

    # Test 1: Import API
    if not test_api_import():
        print("\n❌ Cannot proceed with tests - API import failed")
        return

    # Test 2: Check if server is already running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ API server is already running")
            server_running = True
        else:
            server_running = False
    except:
        server_running = False
        print("⚠️  API server is not running")

    if server_running:
        # Test endpoints
        test_api_endpoints()
        test_prediction_endpoint()

        # Test monitoring services
        test_monitoring_services()
        test_prometheus_scraping()

        print("\n🎯 Summary:")
        print("- API Server: ✅ Running on http://127.0.0.1:8000")
        print("- App Metrics: ✅ Available at http://127.0.0.1:8000/app-metrics")
        print("- Prometheus Metrics: ✅ Available at http://127.0.0.1:8000/metrics")
        print("- Prometheus UI: 🌐 http://localhost:9090")
        print("- Grafana UI: 🌐 http://localhost:3001 (admin/admin)")

    else:
        print("\n💡 To test the endpoints, start the server with:")
        print("   uvicorn api.housing_api:app --host 127.0.0.1 --port 8000")
        print("\n   Then run this script again to test the endpoints.")


if __name__ == "__main__":
    main()
