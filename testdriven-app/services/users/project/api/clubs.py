from project.api.config import *

clubs_blueprint = Blueprint('clubs', __name__)


@clubs_blueprint.route('/db/add_club', methods=['POST'])
def add_club():
    post_data = request.get_json()
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
        db.session.add(Club(name=name, address=address, zipCode=zipCode,
                            city=city, stamNumber=stamNumber, website=website))
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = f'{name} was added!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@clubs_blueprint.route('/db/clubs/<club_id>', methods=['GET'])
def get_single_club(club_id):
    """Get single user details"""
    response_object = {
        'status': 'fail',
        'message': 'Club does not exist'
    }
    try:
        club = Club.query.filter_by(ID=int(club_id)).first()
        if not club:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'ID': club.ID,
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


@clubs_blueprint.route('/db/all_clubs', methods=['GET'])
def get_all_clubs():
    """Get all clubs"""
    response_object = {
        'status': 'success',
        'data': {
            'clubs': [club.to_json() for club in Club.query.all()]
        }
    }
    return jsonify(response_object), 200
