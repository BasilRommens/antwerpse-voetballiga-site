from project.api.config import *
from project.api.helper import *

league_table_blueprint = Blueprint('league_table', __name__)


@league_table_blueprint.route('/srv/league_table', methods=['GET'])
def get_league_table():
    season = int(request.args.get('season'))
    division = int(request.args.get('division'))
    return jsonify(generate_league_table(season, division))
