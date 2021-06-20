from flask import Flask, render_template, request, Blueprint, jsonify, redirect, make_response, url_for
from flask_jwt_extended import *
import requests
import subprocess, socket

ui_blueprint = Blueprint('ui', __name__)


def setup_nav(data_dict, user_id):
    data_dict['nav'] = {}
    if not user_id:
        data_dict['nav']['logged'] = 0
        data_dict['nav']['user_club'] = 0
        data_dict['nav']['admin'] = 0
        data_dict['nav']['super_admin'] = 0
        return data_dict
    data_dict['nav']['logged'] = True
    data_dict['nav']['user_club'] = requests.get(f'http://users:5000/srv/user/{user_id}').json()['clubID']
    admin_data = requests.get(f'http://admin:5000/srv/admin/get_admin/{user_id}').json()
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
    login_response = requests.post('http://users:5000/srv/user/log_in', json=data)
    login_response = login_response.json()
    # de user heeft zijn email fout
    if not login_response:
        data = setup_nav(dict(), get_jwt_identity())
        return render_template('login.html', data=data)
    else:
        # Create the tokens we will be sending back to the user
        access_token = create_access_token(
            identity=login_response['ID'])
        refresh_token = create_refresh_token(
            identity=login_response['ID'])

        # redirect the user to home
        resp = make_response(redirect(url_for('ui.league_table')))
        # Set the JWT cookies in the response
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp


@ui_blueprint.route('/leagueTable/<season>/<division_id>')
@ui_blueprint.route('/leagueTable')
@jwt_optional
def league_table(season=0, division_id=0):
    data = setup_nav(dict(), get_jwt_identity())
    data['season'] = season
    data['divisions'] = [{"link": "/link", "name": "test"}]
    data['ranking'] = {
        "length":
            1,
        "teams": [{
            "TeamName": "Team",
            "TeamLink": "/link",
            "GP": 0,
            "W": 0,
            "D": 0,
            "L": 0,
            "F": 0,
            "A": 0,
            "P": 0
        }]
    }
    return render_template('league_table.html', data=data)


@ui_blueprint.route('/fixtures/<division_id>/<team_id>/<week>')
@ui_blueprint.route('/fixtures/<division_id>/<week>')
@ui_blueprint.route('/fixtures')
@jwt_optional
def fixtures(week=1, division_id=0, team_id=0):
    data = dict()
    data = setup_nav(dict(), get_jwt_identity())
    data['week'] = week
    data['division_id'] = division_id
    data['team_id'] = team_id

    data['matches'] = [{
        "id": 0,
        "date": "20/12/2020",
        "teams": "team 1 (h) - team 2 (a)",
        "link": "/match"
    }]

    data['divisions'] = [{"link": "/link", "name": "test"}]
    data['teams'] = [{"link": "/link", "name": "Team"}]
    return render_template('fixtures.html', data=data)


@ui_blueprint.route('/bestOfDivision/<division_id>')
@ui_blueprint.route('/bestOfDivision')
@jwt_optional
def best_of_division(division_id=0):
    data = dict()
    data = setup_nav(dict(), get_jwt_identity())
    data['division'] = division_id
    data['divisions'] = [{"link": "/link", "name": "name"}]
    data['bestattack'] = {"link": "/link", "name": "name"}
    data['bestdefense'] = {"link": "/link", "name": "name"}
    data['mostcleansheets'] = {"link": "/link", "name": "name"}
    return render_template('best_of_division.html', data=data, admin=0)


@ui_blueprint.route('/team/<team_id>')
@ui_blueprint.route('/team')
@jwt_optional
def team(team_id=0):
    data = dict()
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
    day = 0
    data['weather'] = weather.get_weather(day)
    data['date'] = {'day': 'friday', 'slash': '12/12', 'time': '20:00'}
    data['referee'] = 'John Doe'
    fg_color = 'white'
    bg_color = '#008055'
    data['status'] = {
        'text':
            'To be played',
        'style':
            f'background-color: {bg_color}; color: {fg_color}; font-weight: bold;'
    }
    data['teams'] = "Team 1 (home) - Team 2 (away)"
    data['home_team'] = 'Team 1'
    data['away_team'] = 'Team 2'
    data['current_form'] = {'home_team': 'WWDLWW', 'away_team': 'LLDWW'}
    data['head_to_head'] = {'home_team': 3, 'away_team': 1, 'draw': 4}
    data['last_3'] = {'home_team': [2, 3, 0], 'away_team': [2, 4, 0]}
    return render_template('view_match.html', data=data, admin=0)


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
                      'tags': [{'class': 'badge bg-custom-red', 'text': 'Club'}]}]
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
    return render_template('admin/view_seasons.html', seasons=seasons, data=data)


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
    admin_data = requests.get(f'http://weather:5000/srv/weather/get_weather?day={day}').json()
    return admin_data


if __name__ == '__main__':
    app.run()
