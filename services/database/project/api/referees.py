from project.api.config import *

referee_blueprint = Blueprint('referees', __name__)


@referee_blueprint.route('/db/referee', methods=['POST'])
def add_referee():
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    firstName = post_data.get('firstName')
    lastName = post_data.get('lastName')
    address = post_data.get('address')
    zipCode = post_data.get('zipCode')
    city = post_data.get('city')
    phoneNumber = post_data.get('phoneNumber')
    email = post_data.get('email')
    dateOfBirth = post_data.get('dateOfBirth')
    try:
        referee = Referee.query.filter_by(email=email).first()
        if not referee:
            db.session.add(
                Referee(firstName=firstName, lastName=lastName, address=address,
                        zipCode=zipCode, city=city, phoneNumber=phoneNumber,
                        email=email, dateOfBirth=dateOfBirth))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'{email} was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That email already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@referee_blueprint.route('/db/referee/<referee_id>', methods=['GET'])
def get_single_referee(referee_id):
    """Get single referee details"""
    response_object = {
        'status': 'fail',
        'message': 'referee does not exist'
    }
    try:
        referee = Referee.query.filter_by(ID=int(referee_id)).first()
        if not referee:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': referee.to_json()
            }

            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@referee_blueprint.route('/db/referee/<referee_id>', methods=['DELETE'])
def delete_referee(referee_id):
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for referee existence
        referee = Referee.query.filter_by(ID=referee_id).first()
        if not referee:
            response_object['message'] = 'Sorry. Can\'t delete referee'
            return jsonify(response_object), 400
        else:
            db.session.delete(referee)
            db.session.commit()
            response_object = {'status': 'success',
                               'message': 'Referee deleted.'}
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@referee_blueprint.route('/db/referee/<referee_id>', methods=['PUT'])
def update_referee(referee_id=0):
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    firstName = post_data.get('firstName')
    lastName = post_data.get('lastName')
    address = post_data.get('address')
    zipCode = post_data.get('zipCode')
    city = post_data.get('email')
    phoneNumber = post_data.get('phoneNumber')
    email = post_data.get('email')
    dateOfBirth = post_data.get('dateOfBirth')
    try:
        # Check for referee existence
        referee = Referee.query.filter_by(ID=referee_id).first()
        if not referee:
            response_object['message'] = 'Sorry. Can\'t update referee'
            return jsonify(response_object), 400
        else:
            referee.firstName = firstName
            referee.lastName = lastName
            referee.address = address
            referee.zipCode = zipCode
            referee.city = city
            referee.phoneNumber = phoneNumber
            referee.email = email
            referee.dateOfBirth = dateOfBirth
            db.session.commit()
            response_object['status'] = 'success'
            response_object[
                'message'] = f'Updated referee {firstName} {lastName}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@referee_blueprint.route('/db/all_referees', methods=['GET'])
def get_all_referees():
    """Get all referees"""
    response_object = {
        'status': 'success',
        'data': {
            'referees': [referee.to_json() for referee in Referee.query.all()]
        }
    }
    return jsonify(response_object), 200
