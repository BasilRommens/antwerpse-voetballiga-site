import json
import requests
from project.api.helper import *
from flask import render_template, request, Blueprint, redirect, \
    make_response, url_for, abort
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required, jwt_optional
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, \
    unset_jwt_cookies

ui_blueprint = Blueprint('ui', __name__)


@ui_blueprint.route('/', methods=['GET'])
@jwt_optional
def render_login():
    data = setup_nav(dict(), get_jwt_identity())
    if not get_jwt_identity():
        return render_template('login.html', data=data)
    team_id = get_team_id(get_jwt_identity())
    if team_id == -1 or team_id is None:
        return make_response(redirect(url_for('ui.league_table')))
    else:
        return make_response(redirect(url_for(f'ui.view_fixtures')))


@ui_blueprint.route('/logout')
def logout():
    resp = make_response(redirect("/"))
    unset_jwt_cookies(resp)
    return resp


@ui_blueprint.route('/', methods=['POST'])
@jwt_optional
def login():
    username = str(request.form.get('Username'))
    password = str(request.form.get('Password'))
    # Check login over network
    data = {'username': username, 'password': password}
    login_response = requests.post('http://users:5000/srv/user/log_in',
                                   json=data)
    login_response = login_response.json()
    # The user does not have an email or password
    if not login_response:
        data = setup_nav(dict(), get_jwt_identity())
        return render_template('login.html', data=data)
    else:
        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=login_response['ID'])
        refresh_token = create_refresh_token(identity=login_response['ID'])

        # redirect the user to home
        resp = None
        team_id = get_team_id(login_response['ID'])
        if team_id == -1 or team_id is None:
            resp = make_response(redirect(url_for('ui.league_table')))
        else:
            resp = make_response(redirect(url_for('ui.view_fixtures')))
        # Set the JWT cookies in the response
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp


@ui_blueprint.route('/leagueTable', methods=['POST'])
@jwt_optional
def post_league_table():
    season = request.form.get('season')
    division = request.form.get('division')
    data = get_league_table_data(season, division)
    return render_template('league_table.html', data=data)


@ui_blueprint.route('/leagueTable')
@jwt_optional
def league_table():
    season = int(request.args.get('season')) if request.args.get(
        'season') is not None else 1
    division = int(request.args.get('division')) if request.args.get(
        'division') is not None else 1
    data = get_league_table_data(season, division)
    return render_template('league_table.html', data=data)


@ui_blueprint.route('/fixtures')
@jwt_optional
def fixtures():
    week = int(request.args.get('week')) if request.args.get(
        'week') is not None else 1
    season = int(request.args.get('season')) if request.args.get(
        'season') is not None else 1
    division = int(request.args.get('division')) if request.args.get(
        'division') is not None else 1
    team = int(request.args.get('team')) if request.args.get(
        'team') is not None else -1

    data = requests.get(
        f'http://team_info:5000/srv/team_info/public_fixtures?week={week}&season={season}&division={division}&team={team}').json()
    data = setup_nav(data, get_jwt_identity())

    return render_template('fixtures.html', data=data)


@ui_blueprint.route('/bestOfDivision', methods=['POST'])
@jwt_optional
def post_best_of_division():
    season = request.form.get('season')
    division = request.form.get('division')
    data = get_best_of_division_data(season, division)
    return render_template('best_of_division.html', data=data)


@ui_blueprint.route('/bestOfDivision')
@jwt_optional
def best_of_division():
    season = int(request.args.get('season')) if request.args.get(
        'season') is not None else 1
    division = int(request.args.get('division')) if request.args.get(
        'division') is not None else 1
    data = get_best_of_division_data(season, division)
    return render_template('best_of_division.html', data=data)


@ui_blueprint.route('/team/<team_id>')
@ui_blueprint.route('/team')
@jwt_optional
def team(team_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['team_info'] = requests.get(
        f'http://team_info:5000/srv/team_info/info/{team_id}').json()
    return render_template('team.html', data=data, admin=0)


@ui_blueprint.route('/viewClub/<club_id>')
@ui_blueprint.route('/viewClub')
@jwt_optional
def view_club(club_id=0):
    data = dict()
    data = setup_nav(dict(), get_jwt_identity())
    data['club_name'] = club_id
    data['club_id'] = club_id
    data['home_matches'] = [{
        "id": 0,
        "date": "20/12/2020",
        "teams": "team 1 (h) - team 2 (a)",
        "score": "2 - 2"
    }]
    data['teams'] = [{"id": 0, "name": "A"}]
    return render_template('view_club.html', data=data, admin=0)


@ui_blueprint.route('/editFixture/<match_id>')
@jwt_optional
def edit_fixture(match_id):
    data = get_fixture(match_id)
    data = setup_nav(data, get_jwt_identity())
    return render_template('edit_fixture.html', data=data)


@ui_blueprint.route('/editFixture/<match_id>', methods=['POST'])
@jwt_optional
def post_edit_fixture(match_id):
    json_data = json.dumps(remove_redundant_array(dict(request.form.lists())))
    status = requests.put(
        f'http://database:5000/db/update_match_score/{match_id}',
        json=json_data).json()['status']
    return redirect(f'/editFixture/{match_id}')


@ui_blueprint.route('/editClub/<club_id>', methods=['POST'])
@jwt_required
def post_edit_club(club_id=0):
    if get_club_id(get_jwt_identity()) is None:
        abort(403)
    json_data = json.dumps(remove_redundant_array(dict(request.form.lists())))
    requests.put(
        f'http://database:5000/db/update_club/{club_id}',
        json=json_data)
    return redirect(f'/editClub/{club_id}')


@ui_blueprint.route('/editClub/<club_id>')
@ui_blueprint.route('/editClub')
@jwt_required
def edit_club(club_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['club_info'] = requests.get(
        f'http://database:5000/db/clubs/{club_id}').json()['data']
    return render_template('edit_club.html', data=data)


@ui_blueprint.route('/editTeam/<team_id>')
@ui_blueprint.route('/editTeam')
@jwt_required
def edit_team(team_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['suffix'] = "A"
    data['home_color'] = "red"
    data['away_color'] = "green"
    return render_template('edit_team.html', data=data, admin=0)


@ui_blueprint.route('/addTeam/<club_id>')
@ui_blueprint.route('/addTeam')
@jwt_required
def add_team(club_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['club_id'] = club_id
    return render_template('add_team.html', data=data, admin=0)


@ui_blueprint.route('/viewFixtures/<team_id>')
@ui_blueprint.route('/viewFixtures')
@jwt_required
def view_fixtures(team_id=0):
    if team_id == 0:
        team_id = get_team_id(get_jwt_identity())
    data = requests.get(
        f'http://team_info:5000/srv/team_info/private_fixtures/{team_id}').json()
    data = setup_nav(data, get_jwt_identity())
    return render_template('view_fixtures.html', data=data)


@ui_blueprint.route('/viewMatch/<match_id>')
@ui_blueprint.route('/viewMatch')
@jwt_optional
def view_match(match_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['match_info'] = requests.get(
        f'http://fixture_info:5000/srv/fixture_info/{match_id}').json()
    return render_template('view_match.html', data=data)


@ui_blueprint.route('/admin/viewMatches')
@jwt_optional
def admin_view_matches():
    data = setup_nav(dict(), get_jwt_identity())
    data['matches'] = [
        {'ID': 1, 'teams': 'team 1 (h) - team 2 (a)', 'date': '22/12'}]
    return render_template('admin/view_matches.html', data=data, admin=1)


@ui_blueprint.route('/admin/viewClubs')
@jwt_optional
def admin_view_clubs():
    data = setup_nav(dict(), get_jwt_identity())
    data['clubs'] = [{'name': 'John', 'ID': 0}]
    return render_template('admin/view_clubs.html', data=data, admin=1)


@ui_blueprint.route('/admin/viewReferees')
@jwt_optional
def admin_view_referees():
    data = setup_nav(dict(), get_jwt_identity())
    data['referees'] = get_all_referees()
    return render_template('admin/view_referees.html', data=data, admin=1)


@ui_blueprint.route('/admin/addReferee')
@jwt_optional
def admin_add_referee():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_referee.html', data=data, admin=1)


@ui_blueprint.route('/admin/editReferee/<referee_id>')
@ui_blueprint.route('/admin/editReferee')
@jwt_optional
def admin_edit_referee(referee_id=0):
    data = get_referee(referee_id)
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/edit_referee.html', data=data, admin=1)


@ui_blueprint.route('/admin/viewUsers')
@jwt_optional
def admin_view_users():
    data = setup_nav(dict(), get_jwt_identity())
    data['users'] = [{'username': 'John Doe', 'email': 'yeet@yeet', 'ID': 0,
                      'tags': [
                          {'class': 'badge bg-custom-red', 'text': 'Club'}]}]
    return render_template('admin/view_users.html', data=data, admin=1)


@ui_blueprint.route('/admin/addFixture')
@jwt_optional
def admin_add_match():
    data = setup_nav(dict(), get_jwt_identity())
    data['teams'] = [{'name': 'test', 'ID': 0}]
    data['status'] = ['status']
    data['seasons'] = ['season 1', 'season 2']
    data['divsions'] = ['division 1']
    data['referees'] = ['John Doe']
    return render_template('admin/add_match.html', data=data, admin=1)


@ui_blueprint.route('/admin/addClub')
@jwt_optional
def admin_add_club():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_club.html', admin=1)


@ui_blueprint.route('/admin/viewTeams/<club_id>')
@ui_blueprint.route('/admin/viewTeams')
@jwt_optional
def admin_view_teams(club_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['teams'] = [{'name': 'A', 'ID': 0}]
    data['club'] = {'name': 'club 1', 'ID': club_id}
    return render_template('admin/view_teams.html', data=data, admin=1)


@ui_blueprint.route('/admin/assignReferee/<referee_id>')
@ui_blueprint.route('/admin/assignReferee')
@jwt_optional
def admin_assign_referee(referee_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['matches'] = [{'ID': 0, 'teams': 'Team 1 (h) - Team 2 (a)'}]
    return render_template('admin/assign_referee.html', data=data, admin=1)


@ui_blueprint.route('/admin/editUser/<user_id>')
@ui_blueprint.route('/admin/editUser')
@jwt_optional
def admin_edit_user(user_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['ID'] = 'ID'
    data['username'] = 'John Doe'
    data['password'] = 'password'
    data['email'] = 'email'
    return render_template('admin/edit_user.html', data=data)


@ui_blueprint.route('/admin/addUser')
@jwt_optional
def admin_add_user():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_user.html', data=data)


@ui_blueprint.route('/admin/viewSeasons')
@jwt_optional
def admin_view_season():
    seasons = [1, 2, 3]
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/view_seasons.html', seasons=seasons,
                           data=data)


@ui_blueprint.route('/admin/viewDivisions')
@jwt_optional
def admin_view_division():
    data = setup_nav(dict(), get_jwt_identity())
    data['divisions'] = [{'name': 'Division A', 'ID': 0}]
    return render_template('admin/view_divisions.html', data=data, admin=1)


@ui_blueprint.route('/admin/addDivision')
@jwt_optional
def admin_add_division():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_division.html', admin=1)


@ui_blueprint.route('/admin/editDivision/<division_id>')
@ui_blueprint.route('/admin/editDivision')
@jwt_optional
def admin_edit_division(division_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['division'] = {'name': 'Division A', 'ID': 0}
    return render_template('admin/edit_division.html', data=data, admin=1)


if __name__ == '__main__':
    app.run()
