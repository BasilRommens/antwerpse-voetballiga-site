from project.api.config import *


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


def is_team_in_here(league_table: dict, team_id: int):
    for team in league_table['teams']:
        if team['team_id'] == team_id:
            return True
    return False


def create_default_team():
    return {
        'team_id': None,
        'stam_number': None,
        'name': None,
        'clean_sheet_counter': 0
    }


def add_teams(league_table: dict, matches: list):
    league_table['teams'] = list()
    for match in matches:
        for team_id_name in ["team_home_ID", "team_away_ID"]:
            team = \
                requests.get(
                    f'http://database:5000/db/teams/{match[team_id_name]}').json()[
                    'data']
            team_id = team['id']
            stam_number = team['stamNumber']
            if not is_team_in_here(league_table, team_id):
                team_suffix = team['suffix']
                club_name = requests.get(
                    f'http://database:5000/db/clubs/{stam_number}').json()[
                    'data']['name']
                team = create_default_team()
                team['team_id'] = team_id
                team['stam_number'] = stam_number
                team['name'] = f'{club_name} {team_suffix}'
                league_table['teams'].append(team)
    return league_table


def clean_up_goals(teams: list) -> dict:
    for team in teams:
        for goal_type_letter in ['clean_sheet_counter']:
            if team[goal_type_letter] is None:
                team[goal_type_letter] = 0
    return teams


def add_clean_sheet(teams: list, team_id: int):
    for team in teams:
        if int(team['team_id']) == team_id:
            team['clean_sheet_counter'] += 1
    return teams


def is_null_goals(match: dict):
    return match['goals_home'] is None or match['goals_away'] is None


def count_clean_sheets(teams: list, matches: list):
    for match in matches:
        if is_null_goals(match):
            continue
        goals_home = match['goals_home']
        goals_against = match['goals_away']
        home_team_id = match['team_home_ID']
        if goals_against == 0:
            add_clean_sheet(teams, home_team_id)
        away_team_id = match['team_away_ID']
        if goals_home == 0:
            teams = add_clean_sheet(teams, away_team_id)
    league_table = clean_up_goals(teams)
    return league_table


def get_most_clean_sheets_team(season: int, division: int):
    matches = get_matches(season, division)
    teams = add_teams({'teams': list()}, matches)['teams']
    clean_sheets = count_clean_sheets(teams, matches)
    return max(clean_sheets, key=lambda x: x['clean_sheet_counter'])


def clean_team_data(data):
    del data['F']
    del data['A']
    del data['W']
    del data['L']
    del data['D']
    del data['GP']
    del data['Pts']
    del data['ranking']
    return data


def generate_best_of_division(season: int, division: int) -> dict:
    best_of_division = {'best_of_division': dict()}
    league_table = requests.get(
        f'http://league_table:5000/srv/league_table?season={season}&division={division}').json()
    best_attack_team = max(league_table['teams'], key=lambda x: int(x['F']))
    best_defense_team = max(league_table['teams'], key=lambda x: int(x['A']))
    most_clean_sheets_team = get_most_clean_sheets_team(season, division)
    best_attack_team = clean_team_data(best_attack_team)
    best_defense_team = clean_team_data(best_defense_team)
    best_of_division['best_of_division']['best_attack'] = best_attack_team
    best_of_division['best_of_division']['best_defense'] = best_defense_team
    best_of_division['best_of_division'][
        'most_clean_sheets'] = most_clean_sheets_team
    return best_of_division
