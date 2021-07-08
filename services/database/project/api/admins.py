from project.api.config import *

admin_blueprint = Blueprint('admins', __name__)


def add_admin(admin_id, admin_number):
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for user existence
        user = User.query.filter_by(ID=admin_id).first()
        if not user:
            return jsonify(response_object), 400

        admin_user = Admin.query.filter_by(userID=admin_id).first()
        if not admin_user:
            isSuper = admin_number == 2
            db.session.add(Admin(admin_id, isSuper))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{admin_id} was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That user is already admin.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


def delete_admin(admin_id):
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for user existence
        admin_user = Admin.query.filter_by(userID=admin_id).first()
        if not admin_user:
            response_object['message'] = 'Sorry. Can\'t delete admin'
            return jsonify(response_object), 400
        else:
            db.session.delete(admin_user)
            db.session.commit()
            response_object = {'status': 'success',
                               'message': f'Delete admin {admin_id}'}
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


def admin_exists(user_id: int) -> bool:
    admin_user = Admin.query.filter_by(userID=user_id).first()
    return admin_user is not None


@admin_blueprint.route('/db/admin/<admin_id>', methods=['PUT'])
def update_admin(admin_id):
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    adminNumber = int(post_data.get('admin'))
    if not admin_exists(admin_id) and adminNumber == 0:
        response_object['status'] = 'success'
        response_object['message'] = 'No update required.'
        return jsonify(response_object), 200
    elif admin_exists(admin_id) and adminNumber == 0:
        return delete_admin(admin_id)
    elif not admin_exists(admin_id) and adminNumber != 0:
        return add_admin(admin_id, adminNumber)
    try:
        # Check for user existence
        admin_user = Admin.query.filter_by(userID=admin_id).first()
        if not admin_user:
            response_object['message'] = 'Sorry. Can\'t update admin'
            return jsonify(response_object), 400
        else:
            isSuper = adminNumber == 2
            admin_user.isSuper = isSuper
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
                'data': admin.to_json()
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
