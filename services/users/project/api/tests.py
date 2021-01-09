from project.api.config import *

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route('/srv/user/log_in', methods=['POST'])
def log_in():
    data = request.get_json()
    username = data['username']
    password = data['password']
    users = requests.get('http://database:5000/db/all_users')
    users = users.json()['data']
    for user in users['users']:
        if user['username'] == username:
            if user['password'] == password:
                return jsonify(user)
            return jsonify(False)
    return jsonify(False)
