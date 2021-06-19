from project.api.config import *

admin_blueprint = Blueprint('admins', __name__)


@admin_blueprint.route('/db/new_admin', methods=['POST'])
def add_admin():
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    userID = post_data.get('userID')
    isSuper = post_data.get('isSuper')
    try:
        # Check for user existence
        user = User.query.filter_by(ID=userID).first()
        if not user:
            return jsonify(response_object), 400

        admin_user = Admin.query.filter_by(userID=userID).first()
        if not admin_user:
            db.session.add(Admin(userID, isSuper))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{userID} was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That user is already admin.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@admin_blueprint.route('/db/delete_admin/<admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for user existence
        admin_user = Admin.query.filter_by(userID=admin_id).first()
        if not admin_user:
            response_object['message'] = 'Sorry. Can\'t delete admin'
            return jsonify(response_object), 400
        else:
            Admin.query.filter_by(userID=admin_id).delete()
            db.session.commit()
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@admin_blueprint.route('/db/update_admin', methods=['UPDATE'])
def update_admin():
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    admin_id = post_data.get('userID')
    isSuper = post_data.get('isSuper')
    try:
        # Check for user existence
        admin_user = Admin.query.filter_by(userID=admin_id).first()
        if not admin_user:
            response_object['message'] = 'Sorry. Can\'t update admin'
            return jsonify(response_object), 400
        else:
            admin_user.update({Admin.isSuper: isSuper})
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Updated admin {admin_id}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@admin_blueprint.route('/db/admin/<admin_id>', methods=['GET'])
def get_single_admin(admin_id):
    """Get single admin details"""
    response_object = {
        'status': 'fail',
        'message': 'Admin does not exist'
    }
    try:
        admin = Admin.query.filter_by(userID=int(admin_id)).first()
        if not admin:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'adminID': admin.userID,
                    'isSuper': admin.isSuper
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@admin_blueprint.route('/db/all_admin', methods=['GET'])
def get_all_admins():
    """Get all admins"""
    response_object = {
        'status': 'success',
        'data': {
            'admins': [admin.to_json() for admin in Admin.query.all()]
        }
    }
    return jsonify(response_object), 200
