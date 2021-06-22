from project.api.config import *
from project.api.helper import *

best_of_division_blueprint = Blueprint('best_of_division', __name__)


@best_of_division_blueprint.route('/srv/best_of_division', methods=['GET'])
def get_best_of_division():
    season = int(request.args.get('season'))
    division = int(request.args.get('division'))
    return jsonify(generate_best_of_division(season, division))
