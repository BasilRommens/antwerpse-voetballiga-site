from project.api.config import *
from project.api.helper import generate_league_table

league_table_blueprint = Blueprint('weather', __name__)


@league_table_blueprint.route('/srv/league_table/get_league_table', methods=['GET'])
def get_league_table():
    season = int(request.args.get('season'))
    division = int(request.args.get('division'))
    return jsonify(generate_league_table(season, division))
