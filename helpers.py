from flask import jsonify, Response

def get_challenge_response(data, valid_token):
    if data['token'] == valid_token:
        return jsonify({ "challenge": data["challenge"] })
    else:
        return("Invalid token.")
