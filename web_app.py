import os
import asyncio
from flask import Flask, jsonify
from scheduler import publish

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "service": "BOOST AFRICA MANAGER",
        "channels": [
            "BetBoostAfrica",
            "TechBoostAfrica24",
            "CryptoBoostAfrica"
        ]
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))

    app.run(
        host="0.0.0.0",
        port=port
    )
