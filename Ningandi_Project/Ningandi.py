#!/usr/bin/env python3

import socket
import threading
import subprocess
import time
import platform
from flask import Flask, Response

app = Flask(__name__)

#Global variable to store current hotspot or whatever access point method you use's IP 
current_hotspot_ip = "Waiting for host IP..."

# ============================================================================
# GET HOTSPOT / HOST INTERFACE IP ADDRESS
# ============================================================================

def get_hotspot_ip():
    
    system = platform.system()
    
    if system == "Windows":  #Windows
        return get_hotspot_ip_windows()
    elif system == "Darwin":  #macOS
        return get_hotspot_ip_macos()
    elif system == "Linux":  #Linux
        return get_hotspot_ip_linux()
    else:
        return None    

def get_hotspot_ip_linux():
    try:
        result = subprocess.check_output(['hostname', '-I'])
        ips = result.decode().strip().split()
        #Return the first non-loopback IP
        for ip in ips:
            if ip and ip != '127.0.0.1':
                return ip
        return None
    except Exception:
        return None

def get_hotspot_ip_windows():
    try:
        result = subprocess.check_output(['ipconfig'], text=True)
        lines = result.split('\n')
        
        for line in lines:
            #Look for IPv4 Address lines
            if 'IPv4 Address' in line:
                #Extract the IP address (format: "IPv4 Address . . . . . . . . . . : 192.168.137.5 etc.")
                parts = line.split(':')
                if len(parts) > 1:
                    ip = parts[1].strip()
                    #Skip loopback
                    if ip and ip != '127.0.0.1' and not ip.startswith('169.254'):
                        return ip
        return None
    except Exception:
        return None

def get_hotspot_ip_macos():
    try:
        result = subprocess.check_output(['ifconfig'], text=True)
        lines = result.split('\n')
        
        for line in lines:
            #Look for inet lines (IPv4 addresses, but not inet6)
            if 'inet ' in line and 'inet6' not in line:
                #Format: "inet 192.168.1.100 netmask ..."
                parts = line.strip().split()
                if len(parts) >= 2:
                    ip = parts[1]
                    #Skip loopback and link-local (169.254.x.x)
                    if ip and ip != '127.0.0.1' and not ip.startswith('169.254'):
                        return ip
        return None
    except Exception:
        return None

def ip_monitor():
    #Background thread that continuously checks for hotspot IP
    global current_hotspot_ip
    last_ip = None
    
    while True:
        ip = get_hotspot_ip()
        if ip and ip != last_ip:
            current_hotspot_ip = ip
            print(f"\n[HOST] IP detected: {current_hotspot_ip}\n")
            last_ip = ip
        elif not ip and last_ip:
            current_hotspot_ip = "Waiting for hotspot..."
            print(f"\n[HOST] IP lost, waiting...\n")
            last_ip = None
        
        time.sleep(4)  #Check every 4 seconds seems reasonable 

# ============================================================================
# HTTP SERVER (conntest.nintendowifi.net)
# ============================================================================

@app.route('/') #Flask route decorator '/' root path so when the console connects the responces bellow are served 
def conntest():
    #Respond to console's connectivity check
    return Response('Nintendo', status=200, headers={'X-Organization': 'Nintendo'}) #Response body: Nintendo, Status code: 200 (OK), Custom header: 'X-Organization' : 'Nintendo'

def run_http_server():
    #Run Flask HTTP server on port 80
    print("[HTTP] Starting HTTP server on port 80...")
    app.run(host='0.0.0.0', port=80, debug=False, use_reloader=False)

# ============================================================================
# UDP SERVERS (nncs1/nncs2)
# ============================================================================

def udp_listener(port):
    #Listen on UDP port and echo back responses
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))  #listening on every available network interfaces on the current machine
    print(f"[UDP] Listening on port {port}...")
    
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"[UDP:{port}] Received {len(data)} bytes from {addr}")
            sock.sendto(data, addr)
            print(f"[UDP:{port}] Sent response back to {addr}")
    except KeyboardInterrupt:
        print(f"[UDP] Port {port} listener stopped")
    finally:
        sock.close()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 68)
    print("Ningandi: A personal connectivity validator server for Nintendo consoles")
    print("=" * 68)
    print("This project is NOT affiliated with, endorsed by or associated with Nintendo, Nintendo 3ds, Nintendo Switch,\nand other Nintendo products names and trademarks of Nintendo, Inc.")
    print("This project is an independent tool created to solve connectivity issues on local networks")
    print("=" * 68)
    print(f"OS Detected: {platform.system()}")
    #Check if OS is supported for IP detection
    system = platform.system()
    if system not in ["Windows", "Darwin", "Linux"]:
        print(f"[HOST] IP detection not supported on your {system} system")
    print(f"IP Address: {current_hotspot_ip}")
    print(f"HTTP Server: port 80")
    print(f"UDP Listeners: ports 10025, 33334")
    print("=" * 68)
    
    #Start IP monitoring thread
    monitor_thread = threading.Thread(target=ip_monitor, daemon=True)
    monitor_thread.start()
    
    #Start UDP listeners in separate threads
    thread_10025 = threading.Thread(target=udp_listener, args=(10025,), daemon=True)
    thread_33334 = threading.Thread(target=udp_listener, args=(33334,), daemon=True)
    
    thread_10025.start()
    thread_33334.start()
    
    try:
        run_http_server()
    except KeyboardInterrupt:
        print("\n[MAIN] Shutting down...")
