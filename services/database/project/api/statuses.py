from project.api.config import *

status_blueprint = Blueprint('status', __name__)


@status_blueprint.route('/db/add_status', methods=['POST'])
def add_status():
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    name = post_data.get('name')
    try:
        db.session.add(Status(name=name))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = f'Status was added!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@status_blueprint.route('/db/delete_status/<status_id>', methods=['DELETE'])
def delete_status(status_id):
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for match existence
        status = Status.query.filter_by(ID=status_id).first()
        if not status:
            response_object['message'] = 'Sorry. Can\'t delete status'
            return jsonify(response_object), 400
        else:
            db.session.delete(status)
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Status was deleted!'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@status_blueprint.route('/db/update_status/<status_id>', methods=['PUT'])
def update_status(status_id):
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    name = post_data.get('name')
    try:
        # Check for match existence
        status = Status.query.filter_by(ID=status_id).first()
        if not status:
            response_object['message'] = 'Sorry. Can\'t update status'
            return jsonify(response_object), 400
        else:
            status.name = name
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Updated status {status_id}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@status_blueprint.route('/db/status/<status_id>', methods=['GET'])
def get_single_status(status_id):
    """Get single match details"""
    response_object = {
        'status': 'fail',
        'message': 'Status does not exist'
    }
    try:
        status = Status.query.filter_by(ID=int(status_id)).first()
        if not status:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': status.to_json()
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@status_blueprint.route('/db/all_statuses', methods=['GET'])
def get_all_statuses():
    """Get all referees"""
    response_object = {
        'status': 'success',
        'data': {
            'statuses': [status.to_json() for status in Status.query.all()]
        }
    }
    return jsonify(response_object), 200
