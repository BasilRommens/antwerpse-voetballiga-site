# services/users/project/__init__.py
import os
import sys
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

# Instantiate the database
db = SQLAlchemy()


def create_app(script_info=None):
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    from project.api.admins import admin_blueprint
    app.register_blueprint(admin_blueprint)

    from project.api.clubs import club_blueprint
    app.register_blueprint(club_blueprint)

    from project.api.divisions import division_blueprint
    app.register_blueprint(division_blueprint)

    from project.api.matches import match_blueprint
    app.register_blueprint(match_blueprint)

    from project.api.referees import referee_blueprint
    app.register_blueprint(referee_blueprint)

    from project.api.seasons import season_blueprint
    app.register_blueprint(season_blueprint)

    from project.api.teams import team_blueprint
    app.register_blueprint(team_blueprint)

    from project.api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
