from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess
import sys

app = Flask(__name__)

# =========================
# FOLDERS
# =========================

VIDEO_FOLDER = "videos"
OUTPUT_FOLDER = "output"

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# ANALYZE VIDEO
# =========================

@app.route("/analyze", methods=["POST"])
def analyze():

    if "video" not in request.files:
        return jsonify({
            "success": False,
            "message": "No video uploaded"
        }), 400

    video = request.files["video"]

    if video.filename == "":
        return jsonify({
            "success": False,
            "message": "No video selected"
        }), 400

    # Save uploaded video
    input_path = os.path.join(
        VIDEO_FOLDER,
        "factory.mp4"
    )

    video.save(input_path)

    # Remove previous output
    output_path = os.path.join(
        OUTPUT_FOLDER,
        "factory_safety.mp4"
    )

    if os.path.exists(output_path):
        os.remove(output_path)

    try:

        # Run your existing YOLO program
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode != 0:

            print(result.stderr)

            return jsonify({
                "success": False,
                "message": "Error while running YOLO analysis",
                "error": result.stderr
            }), 500

        if not os.path.exists(output_path):

            return jsonify({
                "success": False,
                "message": "Output video was not created"
            }), 500

        return jsonify({
            "success": True,
            "message": "Analysis completed",
            "video": "/processed-video"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================
# SERVE PROCESSED VIDEO
# =========================

@app.route("/processed-video")
def processed_video():

    output_path = os.path.join(
        OUTPUT_FOLDER,
        "factory_safety.mp4"
    )

    if not os.path.exists(output_path):
        return "Processed video not found", 404

    return send_file(
        output_path,
        mimetype="video/mp4"
    )


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )