import requests
from flask import render_template, request, Blueprint, redirect, \
    make_response, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, \
    unset_jwt_cookies
from flask_jwt_extended import jwt_required, jwt_optional
from flask_jwt_extended import get_jwt_identity

ui_blueprint = Blueprint('ui', __name__)


def setup_nav(data_dict, user_id):
    data_dict['nav'] = {}
    if user_id is None:
        data_dict['nav']['logged'] = 0
        data_dict['nav']['user_club'] = 0
        data_dict['nav']['admin'] = 0
        data_dict['nav']['super_admin'] = 0
        return data_dict
    data_dict['nav']['logged'] = True
    data_dict['nav']['user_club'] = \
        requests.get(f'http://users:5000/srv/user/{user_id}').json()['clubID']
    admin_data = requests.get(
        f'http://admin:5000/srv/admin/get_admin/{user_id}').json()
    if admin_data['status'] == 'fail':
        data_dict['nav']['admin'] = 0
        data_dict['nav']['super_admin'] = False
        return data_dict
    data_dict['nav']['admin'] = admin_data['data']['adminID']
    data_dict['nav']['super_admin'] = admin_data['data']['isSuper']
    return data_dict


@ui_blueprint.route('/', methods=['GET'])
@jwt_optional
def render_login():
    data = setup_nav(dict(), get_jwt_identity())
    if get_jwt_identity():
        resp = make_response(redirect(url_for('ui.league_table')))
        return resp
    return render_template('login.html', data=data)


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
        print(login_response['ID'])
        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=login_response['ID'])
        refresh_token = create_refresh_token(identity=login_response['ID'])

        # redirect the user to home
        resp = make_response(redirect(url_for('ui.league_table')))
        # Set the JWT cookies in the response
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp


def get_division_name(data: dict, division: int):
    data['division_name'] = \
        requests.get(f'http://database:5000/db/divisions/{division}').json()[
            'data']['name']
    return data


def get_all_divisions():
    return requests.get('http://database:5000/db/all_divisions').json()['data'][
        'divisions']


def get_all_seasons():
    return requests.get('http://database:5000/db/all_seasons').json()['data'][
        'seasons']


def get_all_seasons_and_divisions(data: dict):
    data['divisions'] = get_all_divisions()
    data['seasons'] = get_all_seasons()
    return data


def get_league_table_data(season: int, division: int):
    data = setup_nav(dict(), get_jwt_identity())
    data['season'] = int(season)
    data['division'] = int(division)
    data['league_table'] = requests.get(
        f'http://league_table:5000/srv/league_table?season={season}&division={division}').json()
    data = get_all_seasons_and_divisions(data)
    data = get_division_name(data, division)
    return data


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


def get_team_name(team_id: int):
    team = requests.get(
        f'http://database:5000/db/teams/{team_id}').json()['data']
    team_suffix = team['suffix']
    stam_number = int(team['stamNumber'])
    club_name = requests.get(
        f'http://database:5000/db/clubs/{stam_number}').json()[
        'data']['name']
    team_name = f'{club_name} {team_suffix}'
    return team_name


def set_vs_team_name_match(match: dict):
    home_team_id = int(match['team_home_ID'])
    home_team_name = get_team_name(home_team_id)
    away_team_id = int(match['team_away_ID'])
    away_team_name = get_team_name(away_team_id)
    match['teams'] = f'{home_team_name} (H) - {away_team_name} (A)'
    return match


def is_team_in_here(teams: dict, team_id: int):
    for team in teams:
        if team['team_id'] == team_id:
            return True
    return False


def create_default_team():
    return {
        'team_id': None,
        'stam_number': None,
        'name': None
    }


def is_valid_match(match, season: int, division: int):
    return match['season_ID'] == season and match['division_ID'] == division


def get_matches(season: int, division: int) -> list:
    all_matches = \
        requests.get(f'http://database:5000/db/all_matches').json()['data'][
            'matches']
    ret_matches = list()
    for match in all_matches:
        if is_valid_match(match, season, division):
            ret_matches.append(match)
    return ret_matches


def get_teams(division: int, season: int):
    matches = get_matches(season, division)
    teams = list()
    for match in matches:
        for team_id_name in ["team_home_ID", "team_away_ID"]:
            team = \
                requests.get(
                    f'http://database:5000/db/teams/{match[team_id_name]}').json()[
                    'data']
            team_id = team['id']
            stam_number = team['stamNumber']
            if not is_team_in_here(teams, team_id):
                team_suffix = team['suffix']
                club_name = requests.get(
                    f'http://database:5000/db/clubs/{stam_number}').json()[
                    'data']['name']
                team = create_default_team()
                team['team_id'] = team_id
                team['stam_number'] = stam_number
                team['name'] = f'{club_name} {team_suffix}'
                teams.append(team)
    return teams


def get_match_weeks(matches):
    match_weeks = set()

    print(matches)
    for match in matches:
        match_weeks.add(int(match['week']))
    return list(match_weeks)


@ui_blueprint.route('/fixtures')
@jwt_optional
def fixtures():
    data = setup_nav(dict(), get_jwt_identity())
    week = int(request.args.get('week')) if request.args.get(
        'week') is not None else 1
    season = int(request.args.get('season')) if request.args.get(
        'season') is not None else 1
    division = int(request.args.get('division')) if request.args.get(
        'division') is not None else 1
    team = int(request.args.get('team')) if request.args.get(
        'team') is not None else -1
    data['week'] = week
    data['season'] = season
    data['division_id'] = division
    data['team_id'] = team
    all_matches = requests.get(
        f'http://database:5000/db/all_matches_div_season?division={division}&season={season}').json()[
        'data']['matches']
    if team == -1:
        data['matches'] = requests.get(
            f'http://database:5000/db/matches_week_all?division={division}&season={season}&week={week}').json()[
            'data']['matches']
        for match in data['matches']:
            match = set_vs_team_name_match(match)
    else:
        data['matches'] = requests.get(
            f'http://database:5000/db/matches_team_week?division={division}&season={season}&week={week}&team={team}').json()[
            'data']['matches']
        for match in data['matches']:
            match = set_vs_team_name_match(match)

    data['teams'] = get_teams(division, season)
    data['match_weeks'] = get_match_weeks(all_matches)
    data = get_all_seasons_and_divisions(data)
    return render_template('fixtures.html', data=data)


def get_best_of_division_data(season: int, division: int):
    data = setup_nav(dict(), get_jwt_identity())
    data['season'] = int(season)
    data['division'] = int(division)
    data['best_of_division'] = requests.get(
        f'http://best_of_division:5000/srv/best_of_division?season={season}&division={division}').json()[
        'best_of_division']
    data = get_all_seasons_and_divisions(data)
    data = get_division_name(data, division)
    return data


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
    data['team'] = team_id
    data['previous_matches'] = [{
        "id": 0,
        "date": "20/12/2020",
        "teams": "team 1 (h) - team 2 (a)",
        "score": "2 - 2"
    }]
    data['future_matches'] = [{
        "id": 0,
        "date": "20/12/2020",
        "teams": "team 1 (h) - team 2 (a)",
        "score": "2 - 2"
    }]
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
@ui_blueprint.route('/editFixture')
@jwt_optional
def edit_fixture(match_id=0):
    data = dict()
    data = setup_nav(dict(), get_jwt_identity())
    data['teams'] = "team 1 (h) - team 2 (a)"
    data['home_team'] = "team 1"
    data['away_team'] = "team 7"
    data['home_score'] = 0
    data['away_score'] = 2
    return render_template('edit_fixture.html', data=data, admin=0)


@ui_blueprint.route('/editClub/<club_id>')
@ui_blueprint.route('/editClub')
@jwt_optional
def edit_club(club_id=0):
    data = dict()
    data = setup_nav(dict(), get_jwt_identity())
    data['name'] = "fc twente"
    data['stam_number'] = 32
    data['address'] = 'chickenstreet'
    data['zip_code'] = 33892
    data['city'] = 'Antwerpen'
    data['phone_number'] = 783498745923
    data['website'] = 'http://yeet.com'
    return render_template('edit_club.html', data=data, admin=1)


@ui_blueprint.route('/editTeam/<team_id>')
@ui_blueprint.route('/editTeam')
@jwt_required
def edit_team(team_id=0):
    data = dict()
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
    data['referees'] = [{'name': 'John Doe', 'ID': 0}]
    return render_template('admin/view_referees.html', data=data, admin=1)


@ui_blueprint.route('/admin/addReferee')
@jwt_optional
def admin_add_referee():
    data = setup_nav(dict(), get_jwt_identity())
    return render_template('admin/add_referee.html', admin=1)


@ui_blueprint.route('/admin/editReferee/<referee_id>')
@ui_blueprint.route('/admin/editReferee')
@jwt_optional
def admin_edit_referee(referee_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['first_name'] = "george"
    data['last_name'] = "george"
    data['address'] = 'chickenstreet'
    data['zip_code'] = 33892
    data['city'] = 'Antwerpen'
    data['phone_number'] = 783498745923
    data['birthday'] = '22/2/2000'
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


@ui_blueprint.route('/yeet')
def view_weather():
    day = 0
    admin_data = requests.get(
        f'http://weather:5000/srv/weather/get_weather?day={day}').json()
    return admin_data


if __name__ == '__main__':
    app.run()
