from project.api.config import *

division_blueprint = Blueprint('divisions', __name__)


@division_blueprint.route('/db/division', methods=['POST'])
def add_division():
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    name = post_data.get('name')
    try:
        db.session.add(Division(name=name))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = f'{name} was added!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@division_blueprint.route('/db/division/<division_id>', methods=['GET'])
def get_single_division(division_id):
    """Get single division details"""
    response_object = {
        'status': 'fail',
        'message': 'Division does not exist'
    }
    try:
        division = Division.query.filter_by(ID=int(division_id)).first()
        if not division:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'ID': division.ID,
                    'name': division.name
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@division_blueprint.route('/db/division/<division_id>', methods=['DELETE'])
def delete_division(division_id):
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for division existence
        division = Division.query.filter_by(ID=division_id).first()
        if not division:
            response_object['message'] = 'Sorry. Can\'t delete division'
            return jsonify(response_object), 400
        else:
            db.session.delete(division)
            db.session.commit()
            response_object = {'status': 'success',
                               'message': f'{division_id} deleted.'}
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@division_blueprint.route('/db/update_division/<division_id>',
                          methods=['PUT'])
def update_division(division_id):
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    name = post_data.get('name')
    try:
        # Check for division existence
        division = Division.query.filter_by(ID=division_id).first()
        if not division:
            response_object['message'] = 'Sorry. Can\'t update division'
            return jsonify(response_object), 400
        else:
            division.name = name
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Updated division {division_id}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@division_blueprint.route('/db/all_divisions', methods=['GET'])
def get_all_divisions():
    """Get all divisions"""
    response_object = {
        'status': 'success',
        'data': {
            'divisions': [division.to_json() for division in
                          Division.query.all()]
        }
    }
    return jsonify(response_object), 200
