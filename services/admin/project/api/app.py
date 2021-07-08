from project.api.config import *

admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('/srv/admin/get_admin/<admin_id>', methods=['GET'])
def get_admin(admin_id=0):
    admin_data = requests.get(f'http://database:5000/db/admin/{admin_id}').json()
    return jsonify(admin_data), 200
