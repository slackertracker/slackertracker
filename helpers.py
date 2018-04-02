import requests

from flask import jsonify, Response, current_app

def get_challenge_response(data):
    if data['token'] == current_app.config.get('SLACK_VERIFICATION_TOKEN'):
        if current_app.debug:
            print("Responding to valid challenge.")
        return jsonify({ "challenge": data["challenge"] })
    else:
        response = "Invalid challenge token."
        if current_app.debug:
            print(response)
        return(response)

def get_user_by_slack_id(slack_id):
    """
    queries the slack web API for information about the user.
    """

    url = "https://slack.com/api/users.info?user="

    headers = { 
        "Authorization": "Bearer " + current_app.config.get('SLACK_LEGACY_TOKEN'),
    }

    response = requests.get(url + slack_id, headers=headers).json()

    if current_app.debug:
        print("get_user API data: " + str(response))

    user = response.get('user')

    if user is None:
        return({})
        
    profile = user.get('profile')

    return({
        'display_name': profile.get('display_name_normalized'),
        'slack_id': slack_id,
        'team_id': user.get('team_id')
    })

def get_channel_by_slack_id(slack_id):
    from slackertracker.instance.config import SLACK_LEGACY_TOKEN
    
    url = "https://slack.com/api/conversations.info?channel="

    headers = { 
        "Authorization": "Bearer " + SLACK_LEGACY_TOKEN,
    }

    response = requests.get(url + slack_id, headers=headers).json()

    if current_app.debug:
        print("get_channel API data: " + str(response))

    # handle private messages, which won't return a response
    if response.get('error'):
       return({'slack_id': slack_id, 'is_private': True})
	
    channel = response.get('channel')
    if not channel:
        return({})

    return({
        'slack_id': slack_id,
        'name': channel.get('name'),
        'is_private': channel.get('is_private') or channel.get('is_im')
    })

