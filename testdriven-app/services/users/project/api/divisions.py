from project.api.config import *

division_blueprint = Blueprint('divisions', __name__)


@division_blueprint.route('/db/divisions', methods=['POST'])
def add_division():
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    name = post_date.get('name')
    try:
        db.session.add(Division(name=name))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = f'{email} was added!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@division_blueprint.route('/divisions/<division_id>', methods=['GET'])
def get_single_division(division_id):
    """Get single division details"""
    response_object = {
        'status': 'fail',
        'message': 'Division does not exist'
    }
    try:
        division = User.query.filter_by(id=int(division_id)).first()
        if not division:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': division.id,
                    'name': division.name
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@division_blueprint.route('/db/all_divisions', methods=['GET'])
def get_all_divisions():
    """Get all divisions"""
    response_object = {
        'status': 'success',
        'data': {
            'divisions': [division.to_json() for division in Division.query.all()]
        }
    }
    return jsonify(response_object), 200
