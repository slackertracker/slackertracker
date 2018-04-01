from faker import Faker
from slackertracker.app import User
from slackertracker.factories.utils import generate_id

fake = Faker()

def generate_user(team_id=None):
    slack_id = generate_id("U")
    if not team_id:
        team_id = generate_id("T")
    display_name = fake.first_name()

    return User(
        slack_id = slack_id,
        team_id = team_id,
        display_name = display_name,
    )

if __name__=='__main__':
    print(generate_user())