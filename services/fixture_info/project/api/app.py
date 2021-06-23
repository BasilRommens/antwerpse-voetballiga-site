from project.api.config import *
from project.api.helper import *

fixture_info_blueprint = Blueprint('fixture_info', __name__)


@fixture_info_blueprint.route('/srv/fixture_info/<fixture_id>', methods=['GET'])
def get_admin(fixture_id=0):
    return jsonify(get_fixture_info(fixture_id))
