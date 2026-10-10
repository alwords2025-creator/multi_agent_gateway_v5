# Copyright (c) 2026 [Your Name]. All Rights Reserved.
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Structured Logging
"""

from datetime import datetime
from typing import List, Dict

class GatewayLogger:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.events: List[Dict] = []

    def log(self, level: str, component: str, message: str, data: dict = None):
        if not self.enabled:
            return
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = {
            "ts": ts,
            "level": level,
            "component": component,
            "message": message,
            "data": data or {}
        }
        self.events.append(entry)
        print(f"{ts} [{level:7}] {component:12} {message}")

    def info(self, component: str, msg: str, data: dict = None):
        self.log("INFO", component, msg, data)

    def success(self, component: str, msg: str, data: dict = None):
        self.log("SUCCESS", component, msg, data)

    def warn(self, component: str, msg: str, data: dict = None):
        self.log("WARN", component, msg, data)

    def error(self, component: str, msg: str, data: dict = None):
        self.log("ERROR", component, msg, data)

    def show_summary(self, title: str = "Execution Summary"):
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        for e in self.events[-15:]:
            print(f"  {e['ts']} [{e['level']}] {e['component']}: {e['message'][:55]}")
        print(f"{'='*60}\n")

logger = GatewayLogger()
