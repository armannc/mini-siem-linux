#!/usr/bin/env python3
import time
import json
import requests
from datetime import datetime
from collections import defaultdict

LOG_FILE = "/var/log/auth.log"
ATTEMPTS_THRESHOLD = 1

TELEGRAM_TOKEN = ""
CHAT_ID = "920119538"

ip_counter = defaultdict(int)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def log_event(event):
    with open("/var/log/mini_siem.json", "a") as f:
        f.write(json.dumps(event) + "\n")

def extract_ip_user(line):
    if "Failed password" not in line:
        return None, None

    ip = line.split("from")[1].split()[0]

    if "invalid user" in line:
        user = line.split("invalid user")[1].split()[0]
    else:
        user = line.split("for")[1].split()[0]

    return ip, user

def follow(file):
    file.seek(0, 2)  # перейти в конец файла
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.2)
            continue
        yield line

def main():
    print("🚀 Mini‑SIEM real‑time started")

    with open(LOG_FILE, "r", errors="ignore") as f:
        for line in follow(f):
            ip, user = extract_ip_user(line)
            if not ip:
                continue

            ip_counter[ip] += 1
            now = datetime.now()

            print(f"[ALERT EVENT] {ip} → {user}")

            if ip_counter[ip] >= ATTEMPTS_THRESHOLD:
                msg = (
                    f"🚨 REAL‑TIME SIEM ALERT\n"
                    f"IP: {ip}\n"
                    f"User: {user}\n"
                    f"Attempts: {ip_counter[ip]}\n"
                    f"Time: {now}"
                )
                print(msg)
                send_telegram(msg)

                log_event({
                    "time": str(now),
                    "ip": ip,
                    "user": user,
                    "type": "ssh_failed_realtime"
                })

if __name__ == "__main__":
    main()