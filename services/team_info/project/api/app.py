from project.api.config import *
from project.api.helper import *

team_info_blueprint = Blueprint('fixture_info', __name__)


@team_info_blueprint.route('/srv/team_info/<team_id>', methods=['GET'])
def get_admin(team_id=0):
    return jsonify(get_team_info(team_id))
