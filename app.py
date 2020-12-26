from flask import Flask, render_template, request
import subprocess, requests, weather

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
    return render_template('league_table.html', data=data)


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
    return render_template('fixtures.html', data=data)


@app.route('/bestOfDivision/<division_id>')
@app.route('/bestOfDivision')
def best_of_division(division_id=0):
    data = dict()
    data['division'] = division_id
    data['divisions'] = [{"link": "/link", "name": "name"}]
    data['bestattack'] = {"link": "/link", "name": "name"}
    data['bestdefense'] = {"link": "/link", "name": "name"}
    data['mostcleansheets'] = {"link": "/link", "name": "name"}
    return render_template('best_of_division.html', data=data)


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
    return render_template('team.html', data=data)


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
    return render_template('view_club.html', data=data)


@app.route('/editFixture')
def edit_fixture():
    return render_template('edit_fixture.html')


@app.route('/editClub')
def edit_club():
    return render_template('edit_club.html')


@app.route('/editTeam')
def edit_team():
    return render_template('edit_team.html')


@app.route('/addTeam')
def add_team():
    return render_template('add_team.html')


@app.route('/viewMatch')
def view_match():
    data = dict()
    day = 0
    data['weather'] = weather.get_weather(day)
    return render_template('view_match.html', data=data)


@app.route('/admin/viewMatches')
def admin_view_matches():
    return render_template('admin/view_matches.html')


@app.route('/admin/viewClubs')
def admin_view_clubs():
    return render_template('admin/view_clubs.html')


@app.route('/admin/viewReferees')
def admin_view_referees():
    return render_template('admin/view_referees.html')


@app.route('/admin/viewUsers')
def admin_view_users():
    return render_template('admin/view_users.html')


@app.route('/admin/editMatch')
def admin_edit_match():
    return render_template('admin/edit_match.html')


@app.route('/admin/addMatch')
def admin_add_match():
    return render_template('admin/add_match.html')


@app.route('/admin/editClub')
def admin_edit_club():
    return render_template('admin/edit_club.html')


@app.route('/admin/addClub')
def admin_add_club():
    return render_template('admin/add_club.html')


@app.route('/admin/viewTeams')
def admin_view_teams():
    return render_template('admin/view_teams.html')


@app.route('/admin/editTeam')
def admin_edit_team():
    return render_template('admin/edit_team.html')


@app.route('/admin/addTeam')
def admin_add_team():
    return render_template('admin/add_team.html')


@app.route('/admin/assignReferee')
def admin_assign_referee():
    return render_template('admin/assign_referee.html')


@app.route('/admin/editUser')
def admin_edit_user():
    return render_template('admin/edit_user.html')


@app.route('/admin/addUser')
def admin_add_user():
    return render_template('admin/add_user.html')


if __name__ == '__main__':
    app.run()
