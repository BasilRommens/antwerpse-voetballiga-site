from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/leagueTable')
def league_table():
    return render_template('league_table.html')


@app.route('/fixtures')
def fixtures():
    return render_template('fixtures.html')


@app.route('/bestOfDivision')
def best_of_division():
    return render_template('best_of_division.html')


@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/editTeam')
def edit_team():
    return render_template('edit_team.html')


@app.route('/editFixture')
def edit_fixture():
    return render_template('edit_fixture.html')


@app.route('/editClub')
def edit_club():
    return render_template('edit_club.html')


if __name__ == '__main__':
    app.run()