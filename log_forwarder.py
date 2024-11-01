import subprocess
import requests
import sys
import time
import threading

CONTAINER_NAME = "nginx"
HTTP_ENDPOINT = "https://6755-2405-201-d003-d80e-fb7c-ab03-d407-b361.ngrok-free.app/log" 
NGINX_URL = "http://localhost:80"

def stream_docker_logs():
    process = subprocess.Popen(
        ["docker", "logs", "-f", CONTAINER_NAME],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return process

def forward_log_to_http(log_line):
    try:
        log_data = {
            "container_name": CONTAINER_NAME,
            "log": log_line,
        }
        response = requests.post(HTTP_ENDPOINT, json=log_data)
        response.raise_for_status() 
        print(f"Sent log: {log_data}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send log: {e}")

def main():
    # Stream logs from Docker
    process = stream_docker_logs()
    print(f"Streaming logs for container: {CONTAINER_NAME}")

    # Call to Nginx in a separate thread
    threading.Thread(target=periodic_nginx_request, daemon=True).start()

    try:
        for log_line in process.stdout:
            log_line = log_line.strip()
            if log_line:
                print(log_line)
                forward_log_to_http(log_line)
    except KeyboardInterrupt:
        print("\nStopping log forwarder...")
    finally:
        process.terminate()

def periodic_nginx_request():
    while True:
        for _ in range(10):
            try:
                response = requests.get(NGINX_URL)
                print(f"Pinged Nginx: Status Code {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to ping Nginx: {e}")
            time.sleep(0.1) 

if __name__ == "__main__":
    main()
