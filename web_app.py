import os
import asyncio
import threading
from flask import Flask, jsonify
from scheduler import publish, main as scheduler_main

app = Flask(__name__)

_scheduler_started = False
_scheduler_lock = threading.Lock()


@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "service": "BOOST AFRICA MANAGER",
        "channels": [
            "BetBoostAfrica",
            "TechBoostAfrica24",
            "CryptoBoostAfrica"
        ],
        "scheduler": "running"
    })


@app.get("/run/<slot>")
def run_slot(slot):

    if slot not in ("08:00", "13:00", "19:00"):
        return jsonify({
            "status": "error",
            "message": "Invalid slot"
        }), 400

    try:
        asyncio.run(publish(slot))

        return jsonify({
            "status": "success",
            "slot": slot
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def start_scheduler():
    asyncio.run(scheduler_main())


def ensure_scheduler():
    global _scheduler_started

    with _scheduler_lock:
        if not _scheduler_started:
            thread = threading.Thread(
                target=start_scheduler,
                daemon=True
            )
            thread.start()
            _scheduler_started = True
            print("🤖 BOOST AFRICA MANAGER — Scheduler démarré")


ensure_scheduler()
