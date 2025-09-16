from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Allow requests from any origin (you can restrict if needed)

# ✅ Hardcoded Auth-Token
AUTH_TOKEN = "eyJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiZGlyIn0..jro4z6L_kDP5d14E.C86_tpwwmv_S8AQC_kp9-Y5uWrH4ewy4MZbxEunW10wiGSba11RRg5ZzyLY6EkRbUsTAcTrHJWWyQgVtZ8YqL9zsQJ6v8WulLUX6CCjZc0s82QA0siNF9r_ZtZQb32idienDgQlVS1pAyGEz_T2hhi1-mc619XbVkm-KifjeDyufUKP_Z601MChdEY52C9iWuHyiBBvb08SL4F5Wme826HcvKWgjFfduVZiFoS6xnpW-2XGz4FL3KJd8vRbiqhya7ENen1fdxSfvatJWqD91E6FonXL-zuiAU2jZQAvgm6hu70gFxNW1OplzgTSUCyp0wXwftXjVZlHMNYiqFysbDvq9bNSAQoq0UI15RX1w6mOaR4aD6FuZy8Gxlx9rhxK_fXl5A8PLoXZPWBXD3aaPjunfVhTIidZ10JA1NzPal3ReWf2pCyGNfQuRPk_-bx90JcT8GQEUYYLdNMHTqhWsCldl7Uo3CazS_4qvshMUJojrjG_d1XD092Y8laVlG0W-hhbgp88uIxg4LNnI_Mq1xnp8H3XTa4ijYOT8AjoH7CXiF5-UdOt43Yqex-l9.IeVTf1gsGjA-s0mfj3wLBA"
USER_SEARCH_URL = "https://sitareuniv.digiicampus.com/rest/users/search/all"

@app.route('/search_users', methods=['GET'])
def search_users():
    key = request.args.get('key', '')

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
                "photo": user.get("photo"),
                "ukid": user.get("ukid"),
                "userType": user.get("userType"),
            })

        return jsonify(filtered_users)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except ValueError:
        return jsonify({"error": "Invalid JSON response"}), 500

if __name__ == '__main__':
    app.run(debug=True)
