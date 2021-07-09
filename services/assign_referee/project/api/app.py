from project.api.config import *
from project.api.helper import *
import json

assign_referee_blueprint = Blueprint('assign_referee', __name__)


@assign_referee_blueprint.route('/srv/assign_referee/<match_id>',
                                methods=['GET'])
def assign_referee(match_id: int):
    data = dict()
    data['referees'] = get_all_available_referees(match_id)
    data['match_id'] = match_id
    data['ref_id'] = get_match(match_id)['ref_ID']
    return jsonify(data), 200


@assign_referee_blueprint.route('/srv/assign_referee/<match_id>',
                                methods=['PUT'])
def update_assign_referee(match_id: int):
    resp = requests.put(f'http://database:5000/db/assign_referee/{match_id}',
                        json=json.dumps(json.loads(request.get_json())))
    return jsonify(resp.json()), resp.status_code

