from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

VALID_API_KEYS = {
    "GPL": "active"
}

def validate_api_key(api_key):
    if not api_key:
        return {"error": "API key is missing", "status_code": 401}
    if api_key not in VALID_API_KEYS:
        return {"error": "Invalid API key", "status_code": 401}
    status = VALID_API_KEYS[api_key]
    if status == "inactive":
        return {"error": "API key is changed", "status_code": 403}
    if status == "banned":
        return {"error": "API key is banned", "status_code": 403}
    return {"valid": True}

# ✅ التعديل هنا: قراءة الاسم من basicInfo.nickname
def get_player_name(player_id):
    try:
        url = f"https://7ama-info.vercel.app/info?uid={player_id}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if "basicInfo" in data and isinstance(data["basicInfo"], dict):
                return data["basicInfo"].get("nickname", "Unknown")
    except Exception as e:
        print(f"Error fetching nickname: {e}")
    return "Unknown"

def check_banned(player_id):
    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "referer": "https://ff.garena.com/en/support/",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)

            nickname = get_player_name(player_id)

            result = {
                "credits": "X7",
                "channel": "https://t.me/fjfbbfndbdbbdn",
                "uid": player_id,
                "nickname": nickname,
                "status": "BANNED" if is_banned else "NOT BANNED",
                "is_banned": bool(is_banned),
                "ban_period": period if is_banned else 0
            }

            return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Failed to fetch ban info", "status_code": 500}), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e), "status_code": 500}), mimetype="application/json")

@app.route("/bancheck", methods=["GET"])
def bancheck():
    api_key = request.args.get("key", "")
    player_id = request.args.get("uid", "")

    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    if not player_id:
        return Response(json.dumps({"error": "Player ID is required", "status_code": 400}), mimetype="application/json")

    return check_banned(player_id)

@app.route("/check_key", methods=["GET"])
def check_key():
    api_key = request.args.get("key", "")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    return Response(json.dumps({"status": "valid", "key_status": VALID_API_KEYS.get(api_key)}), mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)

