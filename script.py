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
        "Auth-Token": "eyJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiZGlyIn0..jro4z6L_kDP5d14E.C86_tpwwmv_S8AQC_kp9-Y5uWrH4ewy4MZbxEunW10wiGSba11RRg5ZzyLY6EkRbUsTAcTrHJWWyQgVtZ8YqL9zsQJ6v8WulLUX6CCjZc0s82QA0siNF9r_ZtZQb32idienDgQlVS1pAyGEz_T2hhi1-mc619XbVkm-KifjeDyufUKP_Z601MChdEY52C9iWuHyiBBvb08SL4F5Wme826HcvKWgjFfduVZiFoS6xnpW-2XGz4FL3KJd8vRbiqhya7ENen1fdxSfvatJWqD91E6FonXL-zuiAU2jZQAvgm6hu70gFxNW1OplzgTSUCyp0wXwftXjVZlHMNYiqFysbDvq9bNSAQoq0UI15RX1w6mOaR4aD6FuZy8Gxlx9rhxK_fXl5A8PLoXZPWBXD3aaPjunfVhTIidZ10JA1NzPal3ReWf2pCyGNfQuRPk_-bx90JcT8GQEUYYLdNMHTqhWsCldl7Uo3CazS_4qvshMUJojrjG_d1XD092Y8laVlG0W-hhbgp88uIxg4LNnI_Mq1xnp8H3XTa4ijYOT8AjoH7CXiF5-UdOt43Yqex-l9.IeVTf1gsGjA-s0mfj3wLBA",
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
                "ukid": user.get("ukid"),
                "userType": user.get("userType"),
                "phone": user.get("phone")
            })

        return jsonify(filtered_users)
        # return users

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except ValueError:
        return jsonify({"error": "Invalid JSON response"}), 500

if __name__ == '__main__':
    app.run(debug=True)
