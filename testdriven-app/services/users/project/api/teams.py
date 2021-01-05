from project.api.config import *

team_blueprint = Blueprint('teams', __name__)


@team_blueprint.route('/db/teams', methods=['POST'])
def add_team():
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    suffix = post_data.get('suffix')
    awayColor = post_data.get('awayColor')
    homeColor = post_data.get('homeColor')
    clubID = post_data.get('clubID')
    try:
        team = Team.query.filter_by(suffix=suffix).first()
        if not team:
            db.session.add(Team(suffix=suffix, awayColor=awayColor,
                                homeColor=homeColor, clubID=clubID))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Team was added!'
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That team already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@team_blueprint.route('/db/delete_team/<team_id>', methods=['DELETE'])
def delete_team(team_id):
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for team existence
        team = Team.query.filter_by(ID=team_id).first()
        if not team:
            response_object['message'] = 'Sorry. Can\'t delete team'
            return jsonify(response_object), 400
        else:
            team.delete()
            db.session.commit()
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@team_blueprint.route('/db/update_team', methods=['UPDATE'])
def update_team():
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    team_id = post_data.get('ID')
    suffix = post_data.get('suffix')
    awayColor = post_data.get('awayColor')
    homeColor = post_data.get('homeColor')
    clubID = post_data.get('clubID')
    try:
        # Check for team existence
        team = Team.query.filter_by(ID=team_id).first()
        if not team:
            response_object['message'] = 'Sorry. Can\'t update team'
            return jsonify(response_object), 400
        else:
            team.update({Team.suffix: suffix, Team.awayColor: awayColor,
                         Team.homeColor: homeColor, Team.clubID: clubID})

            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Updated team {team_id}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()


@team_blueprint.route('/teams/<team_id>', methods=['GET'])
def get_single_team(team_id):
    """Get single team details"""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        team = Team.query.filter_by(ID=int(team_id)).first()
        if not team:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': team.ID,
                    'suffix': team.suffix,
                    'awayColor': team.awayColor,
                    'homeColor': team.homeColor,
                    'clubID': team.clubID
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@team_blueprint.route('/db/all_teams', methods=['GET'])
def get_all_teams():
    """Get all teams"""
    response_object = {
        'status': 'success',
        'data': {
            'teams': [team.to_json() for team in Team.query.all()]
        }
    }
    return jsonify(response_object), 200
