#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 14:20:28 (ywatanabe)"
# File: ./scitex_repo/src/scitex/life/_monitor_rain.py

"""Imports"""
import time

import requests
import warnings

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        from plyer import notification
except:
    pass

"""Functions & Classes"""
API_KEY = "your_api_key"
CITY = "your_city"
API_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"


def check_rain():
    response = requests.get(API_URL)
    data = response.json()
    if "rain" in data:
        notify_rain()


def notify_rain():
    notification.notify(
        title="Rain Alert",
        message="It's starting to rain in your area!",
        timeout=10,
    )


def monitor_rain():
    while True:
        check_rain()
        time.sleep(300)  # Check every 5 minutes


if __name__ == "__main__":
    monitor_rain()

# EOF
