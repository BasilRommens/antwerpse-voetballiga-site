from flask import Flask, render_template, request
import subprocess
import requests
import weather

app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/leagueTable/<season>/<division_id>')
@app.route('/leagueTable')
def league_table(season=0, division_id=0):
    data = dict()
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
    return render_template('league_table.html', data=data, admin=0)


@app.route('/fixtures/<division_id>/<team_id>/<week>')
@app.route('/fixtures/<division_id>/<week>')
@app.route('/fixtures')
def fixtures(week=1, division_id=0, team_id=0):
    data = dict()
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
    return render_template('fixtures.html', data=data, admin=0)


@app.route('/bestOfDivision/<division_id>')
@app.route('/bestOfDivision')
def best_of_division(division_id=0):
    data = dict()
    data['division'] = division_id
    data['divisions'] = [{"link": "/link", "name": "name"}]
    data['bestattack'] = {"link": "/link", "name": "name"}
    data['bestdefense'] = {"link": "/link", "name": "name"}
    data['mostcleansheets'] = {"link": "/link", "name": "name"}
    return render_template('best_of_division.html', data=data, admin=0)


@app.route('/team/<team_id>')
@app.route('/team')
def team(team_id=0):
    data = dict()
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


@app.route('/viewClub/<club_id>')
@app.route('/viewClub')
def view_club(club_id=0):
    data = dict()
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


@app.route('/editFixture/<match_id>')
@app.route('/editFixture')
def edit_fixture(match_id=0):
    data = dict()
    data['teams'] = "team 1 (h) - team 2 (a)"
    data['home_team'] = "team 1"
    data['away_team'] = "team 7"
    data['home_score'] = 0
    data['away_score'] = 2
    return render_template('edit_fixture.html', data=data, admin=0)


@app.route('/editClub/<club_id>')
@app.route('/editClub')
def edit_club(club_id=0):
    data = dict()
    data['name'] = "fc twente"
    data['stam_number'] = 32
    data['address'] = 'chickenstreet'
    data['zip_code'] = 33892
    data['city'] = 'Antwerpen'
    data['phone_number'] = 783498745923
    data['website'] = 'http://yeet.com'
    return render_template('edit_club.html', data=data, admin=1)


@app.route('/editTeam/<team_id>')
@app.route('/editTeam')
def edit_team(team_id=0):
    data = dict()
    data['suffix'] = "A"
    data['home_color'] = "red"
    data['away_color'] = "green"
    return render_template('edit_team.html', data=data, admin=0)


@app.route('/addTeam/<club_id>')
@app.route('/addTeam')
def add_team(club_id=0):
    data = dict()
    data['club_id'] = club_id
    return render_template('add_team.html', data=data, admin=0)


@app.route('/viewMatch/<match_id>')
@app.route('/viewMatch')
def view_match(match_id=0):
    data = dict()
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


@app.route('/admin/viewMatches')
def admin_view_matches():
    data = dict()
    data['matches'] = [
        {'ID': 1, 'teams': 'team 1 (h) - team 2 (a)', 'date': '22/12'}]
    return render_template('admin/view_matches.html', data=data, admin=1)


@app.route('/admin/viewClubs')
def admin_view_clubs():
    data = dict()
    data['clubs'] = [{'name': 'John', 'ID': 0}]
    return render_template('admin/view_clubs.html', data=data, admin=1)


@app.route('/admin/viewReferees')
def admin_view_referees():
    data = dict()
    data['referees'] = [{'name': 'John Doe', 'ID': 0}]
    return render_template('admin/view_referees.html', data=data, admin=1)


@app.route('/admin/viewUsers')
def admin_view_users():
    data = dict()
    data['users'] = [{'username': 'John Doe', 'email': 'yeet@yeet', 'ID': 0,
                      'tags': [{'class': 'badge bg-custom-red', 'text': 'Club'}]}]
    return render_template('admin/view_users.html', data=data, admin=1)


@app.route('/admin/addFixture')
def admin_add_match():
    data = dict()
    data['teams'] = [{'name': 'test', 'ID': 0}]
    data['status'] = ['status']
    data['seasons'] = ['season 1', 'season 2']
    data['divsions'] = ['division 1']
    data['referees'] = ['John Doe']
    return render_template('admin/add_match.html', data=data, admin=1)


@app.route('/admin/addClub')
def admin_add_club():
    return render_template('admin/add_club.html', admin=1)


@app.route('/admin/viewTeams/<club_id>')
@app.route('/admin/viewTeams')
def admin_view_teams(club_id=0):
    data = dict()
    data['teams'] = [{'name': 'A', 'ID': 0}]
    data['club'] = {'name': 'club 1', 'ID': club_id}
    return render_template('admin/view_teams.html', data=data, admin=1)


@app.route('/admin/assignReferee/<referee_id>')
@app.route('/admin/assignReferee')
def admin_assign_referee(referee_id=0):
    data = dict()
    data['matches'] = [{'ID': 0, 'teams': 'Team 1 (h) - Team 2 (a)'}]
    return render_template('admin/assign_referee.html', data=data, admin=1)


@app.route('/admin/editUser/<user_id>')
@app.route('/admin/editUser')
def admin_edit_user(user_id=0):
    data = dict()
    data['ID'] = 'ID'
    data['username'] = 'John Doe'
    data['password'] = 'password'
    data['email'] = 'email'
    return render_template('admin/edit_user.html', data=data, admin=1)


@app.route('/admin/addUser')
def admin_add_user():
    return render_template('admin/add_user.html', admin=1)


if __name__ == '__main__':
    app.run()
