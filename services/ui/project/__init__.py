import datetime
import os
import sys
from flask import Flask, jsonify, redirect, url_for, make_response, request
from flask_jwt_extended import JWTManager, jwt_refresh_token_required, \
    jwt_optional


def create_app(script_info=None):
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # Json web tokens
    jwt = JWTManager(app)

    # Naam van de cookie
    app.config['JWT_ACCESS_COOKIE_NAME'] = "CoronaKoekje"
    app.config['JWT_REFRESH_COOKIE_NAME'] = "FreshCoronaKoekje"
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    # Geen CSRF protection
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    # Token expired ni
    # app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    # De cookie zal verdwijnen als de browser wordt gesloten
    # app.config['JWT_SESSION_COOKIE'] = True
    # expiration
    # 30 min
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=1800)
    # 20 dagen
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(
        seconds=1728000)

    app.config[
        'SECRET_KEY'] = '*^*(*&)(*)(*afafafaSDD47j\3yX R~X@H!jmM]Lwf/,?KT'

    ### See https://www.ibm.com/developerworks/library/ws-restful/index.html ###
    @jwt.unauthorized_loader
    def my_unauthorized_token_callback(callback):
        resp = redirect(url_for('ui.login'))
        return resp

    # Using the expired_token_loader decorator, we will now call
    # this function whenever an expired but otherwise valid access
    # token attempts to access an endpoint
    @jwt.expired_token_loader
    @jwt_refresh_token_required
    def my_expired_token_callback(expired_token):
        user = get_jwt_identity()
        access_token = create_access_token(identity=user)
        resp = make_response(redirect(request.path))
        set_access_cookies(resp, access_token)
        return resp

    # register blueprints
    from project.api.app import ui_blueprint
    app.register_blueprint(ui_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app}

    return app
