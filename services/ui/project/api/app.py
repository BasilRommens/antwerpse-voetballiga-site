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
    json_data = get_form_data(request)
    status = requests.put(
        f'http://database:5000/db/update_match_score/{match_id}',
        json=json_data).json()['status']
    return redirect(f'/editFixture/{match_id}')


@ui_blueprint.route('/editClub/<club_id>', methods=['POST'])
@jwt_required
def post_edit_club(club_id=0):
    if get_club_id(get_jwt_identity()) is None:
        abort(403)
    json_data = get_form_data(request)
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
    user_id = get_jwt_identity()
    data = setup_nav(dict(), user_id)
    data['club_id'] = club_id
    return render_template('add_team.html', data=data,
                           admin=get_admin_number(user_id))


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
@jwt_required
def admin_view_matches():
    user_id = get_jwt_identity()
    data = \
        requests.get(
            f'http://database:5000/db/all_matches_in_range?min=1&max=25').json()[
            'data']
    data['matches'] = get_match_names(data['matches'])
    data = setup_nav(data, user_id)
    admin = get_admin_number(user_id)
    return render_template('admin/view_matches.html', data=data, admin=admin)


@ui_blueprint.route('/admin/getMatches')
@jwt_required
def admin_get_matches_in_range():
    min = int(request.args.get('min'))
    max = int(request.args.get('max'))
    data = \
        requests.get(
            f'http://database:5000/db/all_matches_in_range?min={min}&max={max}').json()[
            'data']
    data['matches'] = get_match_names(data['matches'])
    return render_template('admin/append_matches.html', data=data)


@ui_blueprint.route('/admin/editMatch/<match_id>')
@jwt_required
def admin_edit_match(match_id):
    user_id = get_jwt_identity()
    data = \
        requests.get(
            f'http://database:5000/db/matches/{match_id}').json()[
            'data']
    if data['team_home_ID'] is not None:
        data['team_home_ID'] = int(data['team_home_ID'])
    if data['team_away_ID'] is not None:
        data['team_away_ID'] = int(data['team_away_ID'])
    if data['match_status'] is not None:
        data['match_status'] = int(data['match_status'])
    if data['week'] is not None:
        data['week'] = int(data['week'])
    data['team_names'] = set_match_team_names(data)['teams']
    data = setup_nav(data, user_id)
    admin = get_admin_number(user_id)
    data['teams'] = get_all_teams()
    data['divisions'] = get_all_divisions()
    data['seasons'] = get_all_seasons()
    data['statuses'] = get_all_statuses()
    return render_template('admin/edit_match.html', data=data, admin=admin)


@ui_blueprint.route('/admin/editMatch/<match_id>', methods=['POST'])
@jwt_required
def post_admin_edit_match(match_id):
    json_data = get_form_data(request)
    status = requests.put(f'http://database:5000/db/update_match/{match_id}',
                          json=json_data).json()['status']
    return redirect(f'/admin/editMatch/{match_id}')


@ui_blueprint.route('/admin/deleteMatch/<match_id>', methods=['POST'])
@jwt_required
def admin_delete_match(match_id):
    status = \
        requests.delete(
            f'http://database:5000/db/delete_match/{match_id}').json()[
            'status']
    return redirect(f'/admin/viewMatches')


@ui_blueprint.route('/admin/addMatch')
@jwt_required
def admin_add_match():
    user_id = get_jwt_identity()
    data = setup_nav(dict(), user_id)
    admin = get_admin_number(user_id)
    data['teams'] = get_all_teams()
    data['divisions'] = get_all_divisions()
    data['seasons'] = get_all_seasons()
    data['statuses'] = get_all_statuses()
    data['referees'] = get_all_referees()
    return render_template('admin/add_match.html', data=data, admin=admin)


@ui_blueprint.route('/admin/addMatch', methods=['POST'])
@jwt_required
def post_admin_add_match():
    json_data = get_form_data(request)
    status = requests.post(f'http://database:5000/db/add_match',
                           json=json_data).json()['status']
    return redirect('/admin/viewMatches')


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
    admin = get_admin_number(get_jwt_identity())
    return render_template('admin/add_referee.html', data=data, admin=admin)


@ui_blueprint.route('/admin/addReferee', methods=['POST'])
@jwt_optional
def post_admin_add_referee():
    json_data = get_form_data(request)
    status = requests.post(
        f'http://database:5000/db/add_referee',
        json=json_data).json()['status']
    return redirect('/admin/viewReferees')


@ui_blueprint.route('/admin/editReferee/<referee_id>')
@jwt_optional
def admin_edit_referee(referee_id=0):
    data = get_referee(referee_id)
    data = setup_nav(data, get_jwt_identity())
    admin = get_admin_number(get_jwt_identity())
    return render_template('admin/edit_referee.html', data=data, admin=admin)


@ui_blueprint.route('/admin/editReferee/<referee_id>', methods=['POST'])
@jwt_optional
def post_admin_edit_referee(referee_id=0):
    json_data = get_form_data(request)
    status = requests.put(
        f'http://database:5000/db/update_referee/{referee_id}',
        json=json_data).json()['status']
    return redirect(f'/admin/editReferee/{referee_id}')


@ui_blueprint.route('/admin/delete-referee/<referee_id>', methods=['POST'])
@jwt_optional
def delete_admin_edit_referee(referee_id=0):
    json_data = get_form_data(request)
    status = requests.delete(
        f'http://database:5000/db/delete_referee/{referee_id}',
        json=json_data).json()['status']
    return redirect(f'/admin/viewReferees')


@ui_blueprint.route('/admin/viewUsers')
@jwt_optional
def admin_view_users():
    data = setup_nav(dict(), get_jwt_identity())
    data['users'] = get_all_users()
    return render_template('admin/view_users.html', data=data)


@ui_blueprint.route('/admin/editUser/<user_id>')
@jwt_required
def admin_edit_user(user_id=0):
    data = get_single_user(user_id)
    data['teams'] = get_all_teams()
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/edit_user.html', data=data)


@ui_blueprint.route('/admin/editUser/<user_id>', methods=['POST'])
@jwt_required
def post_admin_edit_user(user_id=0):
    json_data = get_form_data(request)
    status = requests.put(
        f'http://database:5000/db/update_user/{user_id}',
        json=json_data).json()['status']
    status = requests.put(
        f'http://database:5000/db/update_admin/{user_id}',
        json=json_data).json()['status']
    return redirect(f'/admin/editUser/{user_id}')


@ui_blueprint.route('/admin/deleteUser/<user_id>', methods=['POST'])
@jwt_required
def admin_delete_user(user_id: int = 0):
    status = requests.delete(
        f'http://database:5000/db/delete_user/{user_id}').json()['status']
    return redirect(f'/admin/viewUsers')


@ui_blueprint.route('/admin/addUser')
@jwt_optional
def admin_add_user():
    data = setup_nav(dict(), get_jwt_identity())
    admin = get_admin_number(get_jwt_identity())
    data['teams'] = get_all_teams()
    return render_template('admin/add_user.html', data=data, admin=admin)


@ui_blueprint.route('/admin/addUser', methods=['POST'])
@jwt_optional
def post_admin_add_user():
    json_data = get_form_data(request)
    status = requests.post(
        f'http://database:5000/db/add_user',
        json=json_data).json()
    user_id = int(status['user_id'])
    status = requests.put(
        f'http://database:5000/db/update_admin/{user_id}',
        json=json_data).json()['status']
    return redirect('/admin/viewUsers')


@ui_blueprint.route('/admin/addClub')
@jwt_optional
def admin_add_club():
    # TODO
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_club.html', admin=1)


@ui_blueprint.route('/admin/viewTeams/<club_id>')
@ui_blueprint.route('/admin/viewTeams')
@jwt_optional
def admin_view_teams(club_id=0):
    # TODO
    data = setup_nav(dict(), get_jwt_identity())
    data['teams'] = [{'name': 'A', 'ID': 0}]
    data['club'] = {'name': 'club 1', 'ID': club_id}
    return render_template('admin/view_teams.html', data=data, admin=1)


@ui_blueprint.route('/admin/assignReferee/<referee_id>')
@ui_blueprint.route('/admin/assignReferee')
@jwt_optional
def admin_assign_referee(referee_id=0):
    # TODO
    data = setup_nav(dict(), get_jwt_identity())
    data['matches'] = [{'ID': 0, 'teams': 'Team 1 (h) - Team 2 (a)'}]
    return render_template('admin/assign_referee.html', data=data, admin=1)


@ui_blueprint.route('/admin/viewSeasons')
@jwt_required
def admin_view_season():
    data = setup_nav(dict(), get_jwt_identity())
    data['seasons'] = get_all_seasons()
    return render_template('admin/view_seasons.html', data=data)


@ui_blueprint.route('/admin/deleteSeason/<season>')
@jwt_required
def admin_delete_season(season):
    status = \
        requests.get(f'http://database:5000/db/delete_season/{season}').json()[
            'status']
    return redirect('/admin/viewSeasons')


@ui_blueprint.route('/admin/addSeason')
@jwt_required
def admin_add_season():
    status = requests.get(f'http://database:5000/db/add_season').json()[
        'status']
    return redirect('/admin/viewSeasons')


@ui_blueprint.route('/admin/viewStatuses')
@jwt_required
def admin_view_statuses():
    data = setup_nav(dict(), get_jwt_identity())
    data['statuses'] = get_all_statuses()
    return render_template('admin/view_statuses.html', data=data)


@ui_blueprint.route('/admin/editStatus/<status_id>')
@jwt_required
def admin_edit_status(status_id):
    data = get_status(status_id)
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/edit_status.html', data=data)


@ui_blueprint.route('/admin/editStatus/<status_id>', methods=['POST'])
@jwt_required
def post_admin_edit_status(status_id):
    json_data = get_form_data(request)
    status = requests.put(f'http://database:5000/db/update_status/{status_id}',
                          json=json_data).json()['status']
    return redirect(f'/admin/editStatus/{status_id}')


@ui_blueprint.route('/admin/deleteStatus/<status_id>', methods=['POST'])
@jwt_required
def admin_delete_status(status_id):
    status = \
        requests.delete(
            f'http://database:5000/db/delete_status/{status_id}').json()[
            'status']
    return redirect('/admin/viewStatuses')


@ui_blueprint.route('/admin/addStatus')
@jwt_required
def admin_add_status():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_status.html', data=data)


@ui_blueprint.route('/admin/addStatus', methods=['POST'])
@jwt_required
def post_admin_add_status():
    json_data = get_form_data(request)
    status = \
        requests.post(f'http://database:5000/db/add_status',
                      json=json_data).json()['status']
    return redirect('/admin/viewStatuses')


@ui_blueprint.route('/admin/viewDivisions')
@jwt_optional
def admin_view_division():
    data = dict()
    data['divisions'] = get_all_divisions()
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/view_divisions.html', data=data, admin=1)


@ui_blueprint.route('/admin/addDivision')
@jwt_optional
def admin_add_division():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_division.html', data=data)


@ui_blueprint.route('/admin/addDivision', methods=['POST'])
@jwt_optional
def post_admin_add_division():
    json_data = get_form_data(request)
    status = requests.post(f'http://database:5000/db/add_division',
                           json=json_data).json()['status']
    return redirect('/admin/viewDivisions')


@ui_blueprint.route('/admin/editDivision/<division_id>')
@jwt_optional
def admin_edit_division(division_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['division'] = get_division(division_id)
    return render_template('admin/edit_division.html', data=data, admin=1)


@ui_blueprint.route('/admin/editDivision/<division_id>', methods=['POST'])
@jwt_optional
def post_admin_edit_division(division_id=0):
    json_data = get_form_data(request)
    status = \
        requests.put(f'http://database:5000/db/update_division/{division_id}',
                     json=json_data).json()['status']
    return redirect(f'/admin/editDivision/{division_id}')


@ui_blueprint.route('/admin/deleteDivision/<division_id>', methods=['POST'])
@jwt_optional
def admin_delete_division(division_id=0):
    status = \
        requests.delete(
            f'http://database:5000/db/delete_division/{division_id}').json()[
            'status']
    return redirect(f'/admin/viewDivisions')


if __name__ == '__main__':
    app.run()
