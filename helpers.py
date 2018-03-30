from flask import jsonify, Response

def get_challenge_response(data):
    return jsonify({ "challenge": data["challenge"] })
    