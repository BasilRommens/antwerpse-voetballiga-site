import requests
from flask_jwt_extended import get_jwt_identity


def get_club_id(user_id: int) -> int:
    team_id = int(requests.get(f'http://users:5000/srv/user/{user_id}').json()[
                      'teamID'])
    return int(requests.get(f'http://database:5000/db/teams/{team_id}').json()[
                   'data']['stamNumber'])


def get_team_id(user_id: int) -> int:
    resp = requests.get(f'http://users:5000/srv/user/{user_id}')
    if resp.status_code == 404:
        return -1
    return resp.json()['teamID']


def get_admin_data(user_id: int) -> dict:
    admin_data = requests.get(
        f'http://admin:5000/srv/admin/get_admin/{user_id}').json()
    return admin_data


def setup_nav(data_dict: dict, user_id: int) -> dict:
    data_dict['nav'] = dict()
    if user_id is None:
        for nav_element in ['logged', 'user_club', 'admin', 'super_admin']:
            data_dict['nav'][nav_element] = 0
        return data_dict
    data_dict['nav']['logged'] = True
    data_dict['nav']['user_club'] = get_club_id(user_id)
    data_dict['nav']['user_team'] = get_team_id(user_id)
    admin_data = get_admin_data(user_id)
    if admin_data['status'] == 'fail':
        data_dict['nav']['admin'] = 0
        data_dict['nav']['super_admin'] = False
        return data_dict
    data_dict['nav']['admin'] = admin_data['data']['adminID']
    data_dict['nav']['super_admin'] = admin_data['data']['isSuper']
    return data_dict


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


def get_team_matches(team_id: int) -> list:
    team_matches = \
        requests.get(
            f'http://database:5000/db/all_team_matches/{team_id}').json()[
            'data']['matches']
    return team_matches


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


def get_club_id_from_team_id(team_id: int) -> int:
    team_info = requests.get(
        f'http://database:5000/db/teams/{team_id}').json()['data']
    return int(team_info['stamNumber'])


def get_match_weeks(matches):
    match_weeks = set()

    for match in matches:
        match_weeks.add(int(match['week']))
    return list(match_weeks)


def remove_redundant_array(json_dict: dict):
    for element in json_dict.keys():
        json_dict[element] = json_dict[element][0]
    return json_dict