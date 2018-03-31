from flask import jsonify, Response
import requests

def get_challenge_response(data, valid_token):
    if data['token'] == valid_token:
        return jsonify({ "challenge": data["challenge"] })
    else:
        return("Invalid token.")

def get_user_by_slack_id(slack_id):
    from slackertracker.instance.config import SLACK_LEGACY_TOKEN

    url = "https://slack.com/api/users.info?user="

    headers = { 
        "Authorization": "Bearer " + SLACK_LEGACY_TOKEN,
    }

    user = requests.get(url + slack_id, headers=headers).json().get('user')
    profile = user.get('profile')

    return({
        'display_name': profile.get('display_name_normalized'),
        'slack_id': slack_id,
        'team_id': user.get('team_id')
    })