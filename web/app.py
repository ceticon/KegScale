from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)


# -------------------------------------------------
# SÖKVÄGAR
# -------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

JSON_FILE = os.path.join(
    BASE_DIR,
    "kegscale.json"
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "config.json"
)

CONTROL_FILE = os.path.join(
    BASE_DIR,
    "control.json"
)


# -------------------------------------------------
# WEBBSIDOR
# -------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/setup")
def setup():
    return render_template("setup.html")


# -------------------------------------------------
# API - VÅGDATA
# -------------------------------------------------

@app.route("/api/weight")
def api_weight():
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)

        timestamp = datetime.strptime(
            data["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )

        age = (
            datetime.now()
            - timestamp
        ).total_seconds()

        data["online"] = (
            age < 5
        )

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
# API - TARERING
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
# CONFIG
# -------------------------------------------------

def read_config():
    with open(
        CONFIG_FILE,
        "r"
    ) as f:
        return json.load(f)


def write_config(config):
    with open(
        CONFIG_FILE,
        "w"
    ) as f:
        json.dump(
            config,
            f,
            indent=4,
            ensure_ascii=False
        )


# -------------------------------------------------
# API - ÖLNAMN
# -------------------------------------------------

@app.route(
    "/api/beer-name",
    methods=["GET"]
)
def get_beer_name():
    try:
        config = read_config()

        beer_name = config.get(
            "beer_name",
            ""
        )

        return jsonify({
            "success": True,
            "beer_name": beer_name
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route(
    "/api/beer-name",
    methods=["POST"]
)
def set_beer_name():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Ingen data mottagen"
            }), 400

        beer_name = data.get(
            "beer_name",
            ""
        ).strip()

        if not beer_name:
            return jsonify({
                "success": False,
                "error": "Ölnamnet får inte vara tomt"
            }), 400

        config = read_config()

        config["beer_name"] = beer_name

        write_config(
            config
        )

        return jsonify({
            "success": True,
            "beer_name": beer_name,
            "message": "Ölnamnet sparades"
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
    print(" KegScale Web")
    print("------------------------------")
    print()

    print(
        f"KegScale JSON: {JSON_FILE}"
    )

    print(
        f"Config JSON:   {CONFIG_FILE}"
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