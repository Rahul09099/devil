from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

# ✅ Read Auth-Token from environment
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
USER_SEARCH_URL = "https://sitareuniv.digiicampus.com/rest/users/search/all"

# ✅ CloudFront base URL to make relative photo paths clickable
CLOUD_FRONT_BASE = "https://dli6r6oycdqaz.cloudfront.net/"
# ✅ Optional default profile image
DEFAULT_PROFILE_IMG = "https://d1reij146f0v46.cloudfront.net/version-1757958587/images/profile.png"

def convert_photo_url(photo):
    """Convert internal photo path to full CloudFront URL, or return default if None."""
    if not photo:
        return DEFAULT_PROFILE_IMG
    # Remove any extra prefixes like "testattachments.collpoll##"
    if "##" in photo:
        photo = photo.split("##", 1)[1]  # take part after ##
    # Prepend CloudFront base if not already full URL
    if not photo.startswith("http://") and not photo.startswith("https://"):
        photo = CLOUD_FRONT_BASE + photo
    return photo

@app.route('/search_users', methods=['GET'])
def search_users():
    key = request.args.get('key', '').strip()

    if not key:
        return jsonify({"error": "Missing search key"}), 400

    params = {"key": key}
    headers = {
        "Auth-Token": AUTH_TOKEN,
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(USER_SEARCH_URL, params=params, headers=headers)
        response.raise_for_status()
        users = response.json()

        filtered_users = []
        for user in users:
            filtered_users.append({
                "name": user.get("name"),
                "email": user.get("email"),
                "registrationId": user.get("registrationId"),
                "photo": convert_photo_url(user.get("photo")),
                "ID": user.get("ukid"),
                "userType": user.get("userType"),
            })

        return jsonify(filtered_users)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except ValueError:
        return jsonify({"error": "Invalid JSON response"}), 500

if __name__ == '__main__':
    app.run(debug=True)
