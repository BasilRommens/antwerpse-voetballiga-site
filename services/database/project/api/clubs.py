from project.api.config import *

club_blueprint = Blueprint('clubs', __name__)


@club_blueprint.route('/db/club', methods=['POST'])
def add_club():
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    name = post_data.get('name')
    address = post_data.get('address')
    zipCode = int(post_data.get('zipCode'))
    city = post_data.get('city')
    stamNumber = int(post_data.get('stamNumber'))
    website = post_data.get('website') if post_data.get('website') else ''
    if not len(website):
        website = None
    try:
        db.session.add(Club(name=name, address=address, zipCode=zipCode,
                            city=city, stamNumber=stamNumber, website=website))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = f'{name} was added!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@club_blueprint.route('/db/club/<club_id>', methods=['DELETE'])
def delete_club(club_id):
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for user existence
        club_user = Club.query.filter_by(stamNumber=club_id).first()
        if not club_user:
            response_object['message'] = 'Sorry. Can\'t delete club'
            return jsonify(response_object), 400
        else:
            db.session.delete(club_user)
            db.session.commit()
            response_object = {'status': 'success', 'message': f'{club_id} deleted.'}
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@club_blueprint.route('/db/club/<club_id>', methods=['PUT'])
def update_club(club_id=0):
    post_data = json.loads(request.get_json())

    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    name = post_data.get('name')
    address = post_data.get('address')
    zipCode = post_data.get('zipCode')
    city = post_data.get('city')
    stamNumber = post_data.get('stamNumber')
    website = post_data.get('website')
    try:
        # Check for user existence
        club = Club.query.filter_by(stamNumber=club_id).first()
        if not club:
            response_object['message'] = 'Sorry. Can\'t update club'
            return jsonify(response_object), 400
        else:
            club.name = name
            club.address = address
            club.city = city
            club.zipCode = zipCode
            club.stamNumber = stamNumber
            club.website = website
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Updated club {name}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@club_blueprint.route('/db/club/<club_id>', methods=['GET'])
def get_single_club(club_id):
    """Get single user details"""
    response_object = {
        'status': 'fail',
        'message': 'Club does not exist'
    }
    try:
        club = Club.query.filter_by(stamNumber=int(club_id)).first()
        if not club:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'name': club.name,
                    'address': club.address,
                    'zipCode': club.zipCode,
                    'city': club.city,
                    'stamNumber': club.stamNumber,
                    'website': club.website
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@club_blueprint.route('/db/all_clubs', methods=['GET'])
def get_all_clubs():
    """Get all clubs"""
    response_object = {
        'status': 'success',
        'data': {
            'clubs': [club.to_json() for club in Club.query.all()]
        }
    }
    return jsonify(response_object), 200
