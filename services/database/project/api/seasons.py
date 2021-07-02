from project.api.config import *

season_blueprint = Blueprint('seasons', __name__)


@season_blueprint.route('/db/add_season')
def add_season():
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        db.session.add(Season())
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = 'Season was added!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@season_blueprint.route('/db/delete_season/<season_id>')
def delete_season(season_id):
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for season existence
        season = Season.query.filter_by(season=season_id).first()
        if not season:
            response_object['message'] = 'Sorry. Can\'t delete season'
            return jsonify(response_object), 400
        else:
            db.session.delete(season)
            db.session.commit()
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@season_blueprint.route('/seasons/<season_id>', methods=['GET'])
def get_single_season(season_id):
    """Get single user details"""
    response_object = {'status': 'fail', 'message': 'User does not exist'}
    try:
        season = Season.query.filter_by(season=int(season)).first()
        if not season:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'season': season.season
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@season_blueprint.route('/db/all_seasons', methods=['GET'])
def get_all_seasons():
    """Get all seasons"""
    response_object = {
        'status': 'success',
        'data': {
            'seasons': [season.to_json() for season in Season.query.all()]
        }
    }
    return jsonify(response_object), 200
