from project.api.config import *

status_blueprint = Blueprint('status', __name__)


@status_blueprint.route('/db/all_statuses', methods=['GET'])
def get_all_statuses():
    """Get all referees"""
    response_object = {
        'status': 'success',
        'data': {
            'statuses': [status.to_json() for status in Status.query.all()]
        }
    }
    return jsonify(response_object), 200
