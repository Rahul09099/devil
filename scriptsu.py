from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv, set_key

load_dotenv()  # Load .env file

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

ENV_FILE = ".env"
USER_SEARCH_URL = "https://sitareuniv.digiicampus.com/rest/users/search/all"
CLOUD_FRONT_BASE = "https://dli6r6oycdqaz.cloudfront.net/"
DEFAULT_PROFILE_IMG = "https://d1reij146f0v46.cloudfront.net/version-1757958587/images/profile.png"

def get_auth_token():
    return os.getenv("AUTH_TOKEN")

def set_auth_token(token):
    set_key(ENV_FILE, "AUTH_TOKEN", token)
    os.environ["AUTH_TOKEN"] = token  # Update current environment too

def convert_photo_url(photo):
    if not photo:
        return DEFAULT_PROFILE_IMG
    if "##" in photo:
        photo = photo.split("##", 1)[1]
    if not photo.startswith("http"):
        photo = CLOUD_FRONT_BASE + photo
    return photo

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

        # If the token is invalid, tell frontend
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

if __name__ == '__main__':
    app.run(debug=True)
