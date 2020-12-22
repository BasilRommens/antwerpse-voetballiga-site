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


@app.route('/edit_team')
def edit_team():
    return render_template('edit_team.html')


if __name__ == '__main__':
    app.run()
