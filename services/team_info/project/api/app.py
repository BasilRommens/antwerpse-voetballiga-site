from project.api.config import *
from project.api.helper import *

team_info_blueprint = Blueprint('team_info', __name__)


@team_info_blueprint.route('/srv/team_info/public_fixtures',
                           methods=['GET'])
def get_public_fixtures_data():
    week = int(request.args.get('week')) if request.args.get(
        'week') is not None else 1
    season = int(request.args.get('season')) if request.args.get(
        'season') is not None else 1
    division = int(request.args.get('division')) if request.args.get(
        'division') is not None else 1
    team = int(request.args.get('team')) if request.args.get(
        'team') is not None else -1
    return jsonify(get_public_fixtures(team, week, season, division))


@team_info_blueprint.route('/srv/team_info/private_fixtures/<team_id>',
                           methods=['GET'])
def get_private_fixtures_data(team_id=0):
    return jsonify(get_private_fixtures(team_id)), 200


@team_info_blueprint.route('/srv/team_info/info/<team_id>', methods=['GET'])
def get_info(team_id=0):
    return jsonify(get_team_info(team_id)), 200
