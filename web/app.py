from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime


# -------------------------------------------------
# FLASK
# -------------------------------------------------

app = Flask(__name__)


# -------------------------------------------------
# SÖKVÄGAR
# -------------------------------------------------

# app.py ligger i:
# KegScale/web/app.py
#
# BASE_DIR blir därför:
# KegScale/

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

JSON_FILE = os.path.join(
    BASE_DIR,
    "kegscale.json"
)

CONTROL_FILE = os.path.join(
    BASE_DIR,
    "control.json"
)


# -------------------------------------------------
# HUVUDSIDA
# -------------------------------------------------

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# -------------------------------------------------
# API - LÄS KEGSCALE
# -------------------------------------------------

@app.route("/api/weight")
def api_weight():

    try:

        with open(JSON_FILE, "r") as f:
            data = json.load(f)


        # -----------------------------------------
        # Kontrollera hur gammal mätningen är
        # -----------------------------------------

        timestamp = datetime.strptime(
            data["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )

        age = (
            datetime.now() - timestamp
        ).total_seconds()


        # Om data är yngre än 5 sekunder
        # betraktar vi KegScale som online.

        data["online"] = age < 5

        data["age_seconds"] = round(
            age,
            1
        )


        return jsonify(data)


    except Exception as e:

        return jsonify({
            "error": str(e),
            "online": False
        }), 500


# -------------------------------------------------
# API - NOLLSTÄLL VÅG
# -------------------------------------------------

@app.route(
    "/api/tare",
    methods=["POST"]
)
def api_tare():

    try:

        control_data = {
            "tare": True
        }


        # -----------------------------------------
        # Skriv kommando till control.json
        # -----------------------------------------

        with open(
            CONTROL_FILE,
            "w"
        ) as f:

            json.dump(
                control_data,
                f,
                indent=4
            )


        return jsonify({
            "success": True,
            "message": "Tarering begärd"
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -------------------------------------------------
# STARTA FLASK
# -------------------------------------------------

if __name__ == "__main__":

    print()
    print("------------------------------")
    print(" Keg-Scale Web")
    print("------------------------------")
    print()

    print(
        f"KegScale JSON: {JSON_FILE}"
    )

    print(
        f"Control JSON:  {CONTROL_FILE}"
    )

    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )