from project.api.config import *

test_blueprint = Blueprint('tests', __name__)


@test_blueprint.route('/test', methods=['GET'])
def add_season():
    return "test"
