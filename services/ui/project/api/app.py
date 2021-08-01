import json
import requests
from project.api.helper import *
from flask import render_template, request, Blueprint, redirect, \
    make_response, url_for, abort, flash
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required, jwt_optional
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, \
    unset_jwt_cookies
from project.api.constants import *

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
        return make_response(redirect(url_for('ui.view_fixtures')))


@ui_blueprint.route('/logout')
def logout():
    resp = make_response(redirect("/"))
    unset_jwt_cookies(resp)
    flash(('Logged out', ALERT_SUCCESS))
    return resp


@ui_blueprint.route('/', methods=['POST'])
@jwt_optional
def login():
    username = str(request.form.get('Username'))
    password = str(request.form.get('Password'))
    # Check login over network
    data = {'username': username, 'password': password}
    login_response = requests.post('http://login:5000/srv/user/log_in',
                                   json=data)
    login_response = login_response.json()
    # The user does not have an email or password
    if not login_response:
        flash(('No account with this username and password', ALERT_ERROR))
        data = setup_nav(dict(), get_jwt_identity())
        return render_template('login.html', data=data)
    else:
        flash(('Logged in', ALERT_SUCCESS))
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
    data = dict()
    try:
        data = get_league_table_data(season, division)
    except Exception as e:
        message = 'incorrect parameters'
        flash((message, ALERT_ERROR))
        data = setup_nav(data, get_jwt_identity())
    return render_template('league_table.html', data=data)


@ui_blueprint.route('/leagueTable')
@jwt_optional
def league_table():
    season = int(request.args.get('season')) if request.args.get(
        'season') is not None else 1
    division = int(request.args.get('division')) if request.args.get(
        'division') is not None else 1
    data = dict()
    try:
        data = get_league_table_data(season, division)
    except Exception as e:
        message = 'incorrect parameters'
        flash((message, ALERT_ERROR))
        data = setup_nav(data, get_jwt_identity())
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

    data = dict()
    try:
        data = requests.get(
            f'http://team_info:5000/srv/team_info/public_fixtures?week={week}&season={season}&division={division}&team={team}').json()
    except Exception as e:
        message = 'incorrect parameters'
        flash((message, ALERT_ERROR))
        data = setup_nav(data, get_jwt_identity())
    data = setup_nav(data, get_jwt_identity())

    return render_template('fixtures.html', data=data)


@ui_blueprint.route('/bestOfDivision', methods=['POST'])
@jwt_optional
def post_best_of_division():
    season = request.form.get('season')
    division = request.form.get('division')
    data = dict()
    try:
        data = get_best_of_division_data(season, division)
    except Exception as e:
        message = 'incorrect parameters'
        flash((message, ALERT_ERROR))
        data = setup_nav(data, get_jwt_identity())
    return render_template('best_of_division.html', data=data)


@ui_blueprint.route('/bestOfDivision')
@jwt_optional
def best_of_division():
    season = int(request.args.get('season')) if request.args.get(
        'season') is not None else 1
    division = int(request.args.get('division')) if request.args.get(
        'division') is not None else 1

    data = dict()
    try:
        data = get_best_of_division_data(season, division)
    except Exception as e:
        message = 'incorrect parameters'
        flash((message, ALERT_ERROR))
        data = setup_nav(data, get_jwt_identity())
    return render_template('best_of_division.html', data=data)


@ui_blueprint.route('/team/<team_id>')
@jwt_optional
def team(team_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['team_info'] = requests.get(
            f'http://team_info:5000/srv/team_info/info/{team_id}').json()
    except Exception as e:
        message = f'team with id {team_id} not found'
        flash((message, ALERT_ERROR))
    return render_template('team.html', data=data)


@ui_blueprint.route('/editFixture/<match_id>')
@jwt_optional
def edit_fixture(match_id):
    data = dict()
    try:
        data = get_fixture(match_id)
    except Exception as e:
        message = f'match with id {match_id} not found'
        flash((message, ALERT_ERROR))
    data = setup_nav(data, get_jwt_identity())
    return render_template('edit_fixture.html', data=data)


@ui_blueprint.route('/editFixture/<match_id>', methods=['POST'])
@jwt_optional
def post_edit_fixture(match_id):
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.put(
            f'http://database:5000/db/update_match_score/{match_id}',
            json=json_data).json()
    except Exception as e:
        message = 'failed to update the matches score'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/editFixture/{match_id}')


@ui_blueprint.route('/editClub/<club_id>', methods=['POST'])
@jwt_required
def post_edit_club(club_id=0):
    user_id = get_jwt_identity()
    if get_club_id(user_id) is None and not is_admin(user_id):
        abort(403)
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.put(
            f'http://database:5000/db/club/{club_id}',
            json=json_data).json()
    except Exception as e:
        message = f'Failed to update club with id {club_id}'
        flash((message, ALERT_ERROR))

    response_flash(response)
    return redirect(f'/editClub/{club_id}')


@ui_blueprint.route('/editClub/<club_id>')
@jwt_required
def edit_club(club_id=0):
    user_id = get_jwt_identity()
    data = setup_nav(dict(), user_id)
    try:
        data['club_info'] = requests.get(
            f'http://database:5000/db/club/{club_id}').json()['data']
    except Exception as e:
        message = f'club with id {club_id} not found'
        flash((message, ALERT_ERROR))
    admin = get_admin_number(user_id)
    return render_template('edit_club.html', data=data, admin=admin)


@ui_blueprint.route('/admin/editTeam/<team_id>')
@jwt_required
def admin_edit_team(team_id=0):
    data = dict()
    try:
        data = get_single_team(team_id)
        data['clubs'] = get_all_clubs()
    except Exception as e:
        message = f'team with id {team_id} not found'
        flash((message, ALERT_ERROR))
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/edit_team.html', data=data)


@ui_blueprint.route('/admin/editTeam/<team_id>', methods=['POST'])
@jwt_required
def post_admin_edit_team(team_id=0):
    json_data = get_form_data(request)
    response = requests.put(f'http://database:5000/db/team/{team_id}',
                            json=json_data).json()
    response_flash(response)
    return redirect(f'/admin/editTeam/{team_id}')


@ui_blueprint.route('/admin/addTeam')
@jwt_required
def admin_add_team():
    data = dict()
    data = setup_nav(data, get_jwt_identity())
    try:
        data['clubs'] = get_all_clubs()
    except Exception as e:
        message = 'not able to fetch all the clubs'
        flash((message, ALERT_ERROR))
        data['clubs'] = []
    return render_template(f'admin/add_team.html', data=data)


@ui_blueprint.route('/admin/addTeam', methods=['POST'])
@jwt_required
def post_admin_add_team():
    json_data = get_form_data(request)
    response = requests.post(f'http://database:5000/db/team',
                             json=json_data).json()
    response_flash(response)
    return redirect(f'/admin/viewTeams')


@ui_blueprint.route('/admin/deleteTeam/<team_id>', methods=['POST'])
@jwt_required
def admin_delete_team(team_id):
    try:
        response = requests.delete(
            f'http://database:5000/db/team/{team_id}').json()
    except Exception as e:
        message = f'Not able to delete team with id {team_id}'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect('/admin/viewTeams')


@ui_blueprint.route('/viewFixtures/<team_id>')
@ui_blueprint.route('/viewFixtures')
@jwt_required
def view_fixtures(team_id=0):
    if team_id == 0:
        team_id = get_team_id(get_jwt_identity())
    response = dict()
    try:
        response = requests.get(
            f'http://team_info:5000/srv/team_info/private_fixtures/{team_id}').json()
    except Exception as e:
        message = f'Team with id {team_id} does not exist'
        flash((message, ALERT_ERROR))
    data = setup_nav(response, get_jwt_identity())
    return render_template('view_fixtures.html', data=data)


@ui_blueprint.route('/viewMatch/<match_id>')
@ui_blueprint.route('/viewMatch')
@jwt_optional
def view_match(match_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['match_info'] = requests.get(
            f'http://fixture_info:5000/srv/fixture_info/{match_id}').json()
    except Exception as e:
        message = f'Match with id {match_id} not found'
        flash((message, ALERT_ERROR))
    return render_template('view_match.html', data=data)


@ui_blueprint.route('/admin/viewMatches')
@jwt_required
def admin_view_matches():
    user_id = get_jwt_identity()
    data = dict()
    try:
        data = \
            requests.get(
                f'http://database:5000/db/all_matches_in_range?min=1&max=25').json()[
                'data']
        data['matches'] = get_match_names(data['matches'])
    except Exception as e:
        message = 'Unable to fetch the matches'
        flash((message, ALERT_ERROR))
    data = setup_nav(data, user_id)
    admin = get_admin_number(user_id)
    return render_template('admin/view_matches.html', data=data, admin=admin)


@ui_blueprint.route('/admin/getMatches')
@jwt_required
def admin_get_matches_in_range():
    min = int(request.args.get('min'))
    max = int(request.args.get('max'))
    data = dict()
    try:
        data = \
            requests.get(
                f'http://database:5000/db/all_matches_in_range?min={min}&max={max}').json()[
                'data']
        data['matches'] = get_match_names(data['matches'])
    except Exception as e:
        message = f'Unable to fetch matches in range [{min}, {max}]'
        flash((message, ALERT_ERROR))
    return render_template('admin/append_matches.html', data=data)


@ui_blueprint.route('/admin/editMatch/<match_id>')
@jwt_required
def admin_edit_match(match_id):
    user_id = get_jwt_identity()
    data = dict()
    try:
        data = \
            requests.get(
                f'http://database:5000/db/match/{match_id}').json()[
                'data']
    except Exception as e:
        message = f'Match with id {match_id} was not found'
        flash((message, ALERT_ERROR))
        data = setup_nav(data, user_id)
        admin = get_admin_number(user_id)
        return render_template('admin/edit_match.html', data=data, admin=admin)
    if data['team_home_id'] is not None:
        data['team_home_id'] = int(data['team_home_id'])
    if data['team_away_id'] is not None:
        data['team_away_id'] = int(data['team_away_id'])
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
    response = None
    try:
        response = requests.put(f'http://database:5000/db/match/{match_id}',
                                json=json_data).json()
    except:
        message = f"match with id {match_id} could not be updated"
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/admin/editMatch/{match_id}')


@ui_blueprint.route('/admin/deleteMatch/<match_id>', methods=['POST'])
@jwt_required
def admin_delete_match(match_id):
    response = None
    try:
        response = \
            requests.delete(f'http://database:5000/db/match/{match_id}').json()
    except Exception as e:
        message = f'Can not delete match with id {match_id}'
        flash((message, match_id))
    response_flash(response)
    return redirect(f'/admin/viewMatches')


@ui_blueprint.route('/admin/addMatch')
@jwt_required
def admin_add_match():
    user_id = get_jwt_identity()
    data = setup_nav(dict(), user_id)
    admin = get_admin_number(user_id)
    try:
        data['teams'] = get_all_teams()
        data['divisions'] = get_all_divisions()
        data['seasons'] = get_all_seasons()
        data['statuses'] = get_all_statuses()
        data['referees'] = get_all_referees()
    except:
        message = 'Failed to fetch necessary data for rendering add match'
        flash((message, ALERT_ERROR))
    return render_template('admin/add_match.html', data=data, admin=admin)


@ui_blueprint.route('/admin/addMatch', methods=['POST'])
@jwt_required
def post_admin_add_match():
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.post(f'http://database:5000/db/match',
                                 json=json_data).json()
    except Exception as e:
        message = 'Could not add match because errors were found in the form'
        flash((message, ALERT_ERROR))
        return redirect('/admin/addMatch')
    response_flash(response)
    return redirect('/admin/viewMatches')


@ui_blueprint.route('/admin/viewClubs')
@jwt_optional
def admin_view_clubs():
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['clubs'] = get_all_clubs()
    except Exception as e:
        message = 'Not able to fetch all the clubs'
        flash((message, ALERT_ERROR))
        data['clubs'] = []
    return render_template('admin/view_clubs.html', data=data)


@ui_blueprint.route('/admin/deleteClub/<club_id>', methods=['POST'])
@jwt_optional
def admin_delete_club(club_id: int):
    response = None
    try:
        response = requests.delete(
            f'http://database:5000/db/club/{club_id}').json()
    except Exception as e:
        message = f'Not able to delete club with id {club_id}'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect('/admin/viewClubs')


@ui_blueprint.route('/admin/addClub')
@jwt_optional
def admin_add_club():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_club.html', data=data)


@ui_blueprint.route('/admin/addClub', methods=['POST'])
@jwt_optional
def post_admin_add_club():
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.post(f'http://database:5000/db/club',
                                 json=json_data).json()
    except Exception as e:
        message = 'Not able to add the club to the database'
        flash((message, ALERT_ERROR))
        return redirect('/admin/addClub')
    response_flash(response)
    if is_failed_response(response):
        return redirect('/admin/addClub')
    return redirect('/admin/viewClubs')


@ui_blueprint.route('/admin/viewReferees')
@jwt_optional
def admin_view_referees():
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['referees'] = get_all_referees()
    except Exception as e:
        message = 'Unable to fetch all the referees'
        flash((message, ALERT_ERROR))
        data['referees'] = []
    return render_template('admin/view_referees.html', data=data)


@ui_blueprint.route('/admin/addReferee')
@jwt_optional
def admin_add_referee():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_referee.html', data=data)


@ui_blueprint.route('/admin/addReferee', methods=['POST'])
@jwt_optional
def post_admin_add_referee():
    json_data = get_form_data(request)
    try:
        response = requests.post(
            f'http://database:5000/db/referee',
            json=json_data).json()
    except Exception as e:
        message = 'Not able to add referee'
        flash((message, ALERT_ERROR))
        return redirect('/admin/addReferee')
    response_flash(response)
    return redirect('/admin/viewReferees')


@ui_blueprint.route('/admin/editReferee/<referee_id>')
@jwt_optional
def admin_edit_referee(referee_id=0):
    data = dict()
    try:
        data = get_referee(referee_id)
    except Exception as e:
        message = f'Not able to fetch the referee with id {referee_id} to edit'
        flash((message, ALERT_ERROR))
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/edit_referee.html', data=data)


@ui_blueprint.route('/admin/editReferee/<referee_id>', methods=['POST'])
@jwt_optional
def post_admin_edit_referee(referee_id=0):
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.put(
            f'http://database:5000/db/referee/{referee_id}',
            json=json_data).json()
    except Exception as e:
        message = f'The referee with id {referee_id} could not be updated'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/admin/editReferee/{referee_id}')


@ui_blueprint.route('/admin/delete-referee/<referee_id>', methods=['POST'])
@jwt_optional
def delete_admin_edit_referee(referee_id=0):
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.delete(
            f'http://database:5000/db/referee/{referee_id}',
            json=json_data).json()
    except Exception as e:
        message = f"Not able to delete the referee with id {referee_id}"
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/admin/viewReferees')


@ui_blueprint.route('/admin/viewUsers')
@jwt_optional
def admin_view_users():
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['users'] = get_all_users()
    except Exception as e:
        message = 'Not able to display all the users'
        flash((message, ALERT_ERROR))
        data['users'] = []
    return render_template('admin/view_users.html', data=data)


@ui_blueprint.route('/admin/editUser/<user_id>')
@jwt_required
def admin_edit_user(user_id=0):
    data = dict()
    try:
        data = get_single_user(user_id)
    except Exception as e:
        message = f'User with id {user_id} could not be retrieved'
        flash((message, ALERT_ERROR))

    try:
        data['teams'] = get_all_teams()
    except Exception as e:
        message = 'Not able to retrieve all the teams'
        flash((message, ALERT_ERROR))
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/edit_user.html', data=data)


@ui_blueprint.route('/admin/editUser/<user_id>', methods=['POST'])
@jwt_required
def post_admin_edit_user(user_id=0):
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.put(
            f'http://database:5000/db/user/{user_id}',
            json=json_data).json()
    except Exception as e:
        message = 'Not able to update user'
        flash((message, ALERT_ERROR))
    response_flash(response)
    try:
        response = requests.put(
            f'http://database:5000/db/admin/{user_id}',
            json=json_data).json()
    except Exception as e:
        message = 'Not able to make admin'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/admin/editUser/{user_id}')


@ui_blueprint.route('/admin/deleteUser/<user_id>', methods=['POST'])
@jwt_required
def admin_delete_user(user_id: int = 0):
    response = None
    try:
        response = requests.delete(
            f'http://database:5000/db/user/{user_id}').json()
    except Exception as e:
        message = f'Not able to delete user with id {user_id}'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/admin/viewUsers')


@ui_blueprint.route('/admin/addUser')
@jwt_required
def admin_add_user():
    data = setup_nav(dict(), get_jwt_identity())
    admin = get_admin_number(get_jwt_identity())
    try:
        data['teams'] = get_all_teams()
    except Exception as e:
        message = 'Not able to fetch all the teams'
        flash((message, ALERT_ERROR))
    return render_template('admin/add_user.html', data=data, admin=admin)


@ui_blueprint.route('/admin/addUser', methods=['POST'])
@jwt_required
def post_admin_add_user():
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.post(
            f'http://database:5000/db/user',
            json=json_data).json()
    except Exception as e:
        message = 'Not able to update the user'
        flash((message, ALERT_ERROR))
    response_flash(response)
    user_id = int(status['user_id'])
    try:
        response = requests.put(
            f'http://database:5000/db/admin/{user_id}',
            json=json_data).json()['status']
    except Exception as e:
        message = 'Not able to update admin element'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect('/admin/viewUsers')


@ui_blueprint.route('/admin/viewTeams')
@jwt_required
def admin_view_teams():
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['teams'] = get_all_teams()
    except Exception as e:
        message = 'Not able to get all the teams'
        flash((message, ALERT_ERROR))
    return render_template('admin/view_teams.html', data=data)


@ui_blueprint.route('/admin/assignReferee/<match_id>')
@jwt_required
def admin_assign_referee(match_id: int):
    data = dict()
    try:
        data = requests.get(
            f'http://assign_referee:5000/srv/assign_referee/{match_id}').json()
    except:
        message = f'unable to fetch referee for match with id {match_id}'
        flash((message, ALERT_ERROR))
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/assign_referee.html', data=data)


@ui_blueprint.route('/admin/assignReferee/<match_id>', methods=['POST'])
@jwt_required
def post_admin_assign_referee(match_id):
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.put(
            f'http://assign_referee:5000/srv/assign_referee/{match_id}',
            json=json_data).json()
    except Exception as e:
        message = f'Not able to assign referee to match with id {match_id}'
        flash((message, response))
    response_flash(response)
    return redirect('/admin/viewMatches')


@ui_blueprint.route('/admin/viewSeasons')
@jwt_required
def admin_view_season():
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['seasons'] = get_all_seasons()
    except Exception as e:
        message = 'Seasons were not available to be fetched'
        flash((message, ALERT_ERROR))
    return render_template('admin/view_seasons.html', data=data)


@ui_blueprint.route('/admin/deleteSeason/<season>')
@jwt_required
def admin_delete_season(season):
    response = None
    try:
        response = requests.get(
            f'http://database:5000/db/season/{season}').json()
    except Exception as e:
        message = 'season can not be deleted'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect('/admin/viewSeasons')


@ui_blueprint.route('/admin/addSeason')
@jwt_required
def admin_add_season():
    response = None
    try:
        response = requests.get(f'http://database:5000/db/season').json()
    except Exception as e:
        message = 'season can not be added'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect('/admin/viewSeasons')


@ui_blueprint.route('/admin/viewStatuses')
@jwt_required
def admin_view_statuses():
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['statuses'] = get_all_statuses()
    except Exception as e:
        message = 'Not able to fetch all the statuses'
        flash((message, ALERT_ERROR))
    return render_template('admin/view_statuses.html', data=data)


@ui_blueprint.route('/admin/editStatus/<status_id>')
@jwt_required
def admin_edit_status(status_id):
    data = dict()
    try:
        data = get_status(status_id)
    except Exception as e:
        message = f'Not able to fetch the status with id {status_id}'
        flash((message, ALERT_ERROR))
    data = setup_nav(data, get_jwt_identity())
    return render_template('admin/edit_status.html', data=data)


@ui_blueprint.route('/admin/editStatus/<status_id>', methods=['POST'])
@jwt_required
def post_admin_edit_status(status_id):
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.put(f'http://database:5000/db/status/{status_id}',
                                json=json_data).json()
    except Exception as e:
        message = f'Not able to update status with id {status_id}'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/admin/editStatus/{status_id}')


@ui_blueprint.route('/admin/deleteStatus/<status_id>', methods=['POST'])
@jwt_required
def admin_delete_status(status_id):
    response = None
    try:
        response = requests.delete(
            f'http://database:5000/db/status/{status_id}').json()
    except Exception as e:
        message = f'Not able to delete status with id {status_id}'
        flash((message, ALERT_ERROR))
    response_flash(response)
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
    response = None
    try:
        response = requests.post(f'http://database:5000/db/status',
                                 json=json_data).json()
    except Exception as e:
        message = 'Not able to add new status'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect('/admin/viewStatuses')


@ui_blueprint.route('/admin/viewDivisions')
@jwt_optional
def admin_view_division():
    data = dict()
    try:
        data['divisions'] = get_all_divisions()
    except Exception as e:
        message = 'not able to fetch all the divisions'
        flash((message, ALERT_ERROR))
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
    response = None
    try:
        response = requests.post(f'http://database:5000/db/division',
                                 json=json_data).json()
    except Exception as e:
        message = 'Not able to add a new division'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect('/admin/viewDivisions')


@ui_blueprint.route('/admin/editDivision/<division_id>')
@jwt_optional
def admin_edit_division(division_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    try:
        data['division'] = get_division(division_id)
    except Exception as e:
        message = f'Not able to fetch the division with id {division_id}'
        flash((message, ALERT_ERROR))
    return render_template('admin/edit_division.html', data=data, admin=1)


@ui_blueprint.route('/admin/editDivision/<division_id>', methods=['POST'])
@jwt_optional
def post_admin_edit_division(division_id=0):
    json_data = get_form_data(request)
    response = None
    try:
        response = requests.put(
            f'http://database:5000/db/update_division/{division_id}',
            json=json_data).json()
    except Exception as e:
        message = f'Not able to update division with id {division_id}'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/admin/editDivision/{division_id}')


@ui_blueprint.route('/admin/deleteDivision/<division_id>', methods=['POST'])
@jwt_optional
def admin_delete_division(division_id=0):
    response = None
    try:
        response = requests.delete(
            f'http://database:5000/db/division/{division_id}').json()
    except Exception as e:
        message = f'Not able to delete division with id {division_id}'
        flash((message, ALERT_ERROR))
    response_flash(response)
    return redirect(f'/admin/viewDivisions')


if __name__ == '__main__':
    app.run()
