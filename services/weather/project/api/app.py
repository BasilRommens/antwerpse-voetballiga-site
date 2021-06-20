from project.api.config import *
from project.api.weather import get_weather_day

weather_blueprint = Blueprint('weather', __name__)


@weather_blueprint.route('/srv/weather/get_weather', methods=['GET'])
def get_weather():
    day = int(request.args.get('day'))
    return jsonify(get_weather_day(day))
