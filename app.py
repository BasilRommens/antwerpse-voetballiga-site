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

if __name__ == '__main__':
    app.run()
