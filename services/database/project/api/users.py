from project.api.config import *

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/db/add_user', methods=['POST'])
def add_user():
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    teamID = int(post_data.get('teamID'))
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            if teamID == -1:
                teamID = None
            new_user = User(username=username, email=email,
                 password=password, teamID=teamID)
            db.session.add(new_user)
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{username} was added!'
            response_object['user_id'] = new_user.ID
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That email already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@user_blueprint.route('/db/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for user existence
        user = User.query.filter_by(ID=user_id).first()
        if not user:
            response_object['message'] = 'Sorry. Can\'t delete user'
            return jsonify(response_object), 400
        else:
            db.session.delete(user)
            db.session.commit()
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@user_blueprint.route('/db/update_user/<user_id>', methods=['PUT'])
def update_user(user_id):
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    teamID = post_data.get('teamID')
    try:
        # Check for user existence
        user = User.query.filter_by(ID=user_id).first()
        if not user:
            response_object['message'] = 'Sorry. Can\'t update user'
            return jsonify(response_object), 400
        else:
            user.username = username
            user.email = email
            user.password = password
            user.teamID = teamID
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Updated user {username}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@user_blueprint.route('/db/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get single user details"""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user = User.query.filter_by(ID=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': user.ID,
                    'username': user.username,
                    'email': user.email,
                    'password': user.password,
                    'teamID': user.teamID
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@user_blueprint.route('/db/user_id/<email>')
def get_user_id(email):
    """Get user id"""
    user = User.query.filter_by(email=email).first()
    response_object = {
        'status': 'success',
        'data': user.to_json()
    }
    return jsonify(response_object), 200


@user_blueprint.route('/db/all_users')
def get_all_users():
    """Get all users"""
    response_object = {
        'status': 'success',
        'data': {
            'users': [user.to_json() for user in User.query.all()]
        }
    }
    return jsonify(response_object), 200
