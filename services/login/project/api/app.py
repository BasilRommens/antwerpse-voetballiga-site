from project.api.config import *

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route('/srv/user/log_in', methods=['POST'])
def log_in():
    data = request.get_json()
    username = data['username']
    password = data['password']
    users = requests.get('http://database:5000/db/all_users').json()['data']
    for user in users['users']:
        if user['username'] != username:
            continue
        if user['password'] == password:
            return jsonify(user), 200
        else:
            jsonify(False), 400
    return jsonify(False), 400


@user_blueprint.route('/srv/user/<user_id>', methods=['GET'])
def get_user(user_id=1):
    user = requests.get(f'http://database:5000/db/user/{user_id}')
    user = user.json()
    if user['status'] == 'fail':
        return jsonify(user), 404
    return jsonify(user['data'])
