from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv, set_key

# --- Load .env and initialize token ---
ENV_FILE = ".env"
load_dotenv(override=True)  # Load .env on startup and override os.environ
AUTH_TOKEN = os.getenv("AUTH_TOKEN")  # keep in memory

# --- Flask setup ---
app = Flask(__name__)
CORS(app)

USER_SEARCH_URL = "https://sitareuniv.digiicampus.com/rest/users/search/all"
CLOUD_FRONT_BASE = "https://dli6r6oycdqaz.cloudfront.net/"
DEFAULT_PROFILE_IMG = "https://d1reij146f0v46.cloudfront.net/version-1757958587/images/profile.png"

# --- Helper functions ---
def get_auth_token():
    global AUTH_TOKEN
    return AUTH_TOKEN

def set_auth_token(token):
    global AUTH_TOKEN
    token = token.strip()
    if not token:
        raise ValueError("Token cannot be empty")
    # Update .env
    set_key(ENV_FILE, "AUTH_TOKEN", token)
    # Update memory
    AUTH_TOKEN = token
    os.environ["AUTH_TOKEN"] = token

def convert_photo_url(photo):
    if not photo:
        return DEFAULT_PROFILE_IMG
    if "##" in photo:
        photo = photo.split("##", 1)[1]
    if not photo.startswith("http"):
        photo = CLOUD_FRONT_BASE + photo
    return photo

# --- Routes ---
@app.route('/set_auth_token', methods=['POST'])
def set_token():
    data = request.get_json()
    token = data.get("token", "").strip()

    if not token:
        return jsonify({"error": "Token is missing"}), 400

    try:
        set_auth_token(token)
        return jsonify({"message": "Token set successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search_users', methods=['GET'])
def search_users():
    key = request.args.get('key', '').strip()
    if not key:
        return jsonify({"error": "Missing search key"}), 400

    token = get_auth_token()
    if not token:
        return jsonify({"error": "Auth token not set"}), 401

    headers = {
        "Auth-Token": token,
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(USER_SEARCH_URL, params={"key": key}, headers=headers)

        # If token is invalid, tell frontend to provide new one
        if response.status_code in (401, 403):
            return jsonify({"error": "Invalid or expired Auth token"}), 403

        response.raise_for_status()
        users = response.json()

        filtered_users = [
            {
                "name": u.get("name"),
                "email": u.get("email"),
                "registrationId": u.get("registrationId"),
                "photo": convert_photo_url(u.get("photo")),
                "ukid": u.get("ukid"),
                "userType": u.get("userType"),
                "phone": u.get("phone")
            } for u in users
        ]
        return jsonify(filtered_users)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except ValueError:
        return jsonify({"error": "Invalid JSON response"}), 500

# --- Run server ---
if __name__ == '__main__':
    print(f"Loaded token from .env: {AUTH_TOKEN}")  # debug info
    app.run(debug=True)
