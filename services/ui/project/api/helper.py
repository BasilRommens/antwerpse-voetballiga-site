import requests, json
import datetime
from flask_jwt_extended import get_jwt_identity
from flask import flash
from project.api.constants import *


def get_club_id(user_id: int) -> int:
    try:
        team_id = int(
            requests.get(f'http://login:5000/srv/user/{user_id}').json()[
                'teamID'])
    except Exception:
        return None
    return int(requests.get(f'http://database:5000/db/team/{team_id}').json()[
                   'data']['stamNumber'])


def get_team_id(user_id: int) -> int:
    resp = requests.get(f'http://login:5000/srv/user/{user_id}')
    if resp.status_code == 404:
        return -1
    return resp.json()['teamID']


def get_admin_data(user_id: int) -> dict:
    admin_data = requests.get(
        f'http://database:5000/db/admin/{user_id}').json()
    if admin_data['status'] == 'fail':
        return None
    return admin_data


def is_admin(user_id: int) -> bool:
    return get_admin_data(user_id) is not None


def is_super_admin(user_id: int) -> bool:
    if get_admin_data(user_id) is None:
        return False
    return get_admin_data(user_id)['data']['is_super']


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
    if not admin_data:
        data_dict['nav']['admin'] = 0
        data_dict['nav']['super_admin'] = False
        return data_dict
    if admin_data['status'] == 'fail':
        data_dict['nav']['admin'] = 0
        data_dict['nav']['super_admin'] = False
        return data_dict
    data_dict['nav']['admin'] = admin_data['data']['admin_id']
    data_dict['nav']['super_admin'] = admin_data['data']['is_super']
    return data_dict


def get_division_name(data: dict, division: int):
    data['division_name'] = \
        requests.get(f'http://database:5000/db/division/{division}').json()[
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


def get_team_name(team_id: int):
    team = requests.get(
        f'http://database:5000/db/team/{team_id}').json()['data']
    team_suffix = team['suffix']
    stam_number = int(team['stamNumber'])
    club_name = requests.get(
        f'http://database:5000/db/club/{stam_number}').json()[
        'data']['name']
    team_name = f'{club_name} {team_suffix}'
    return team_name


def set_match_team_names(match: dict):
    home_team_id = int(match['team_home_id'])
    home_team_name = get_team_name(home_team_id)
    away_team_id = int(match['team_away_id'])
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
        for team_id_name in ["team_home_id", "team_away_id"]:
            team = \
                requests.get(
                    f'http://database:5000/db/team/{match[team_id_name]}').json()[
                    'data']
            team_id = team['id']
            stam_number = team['stamNumber']
            if not is_team_in_here(teams, team_id):
                team_suffix = team['suffix']
                club_name = requests.get(
                    f'http://database:5000/db/club/{stam_number}').json()[
                    'data']['name']
                team = create_default_team()
                team['team_id'] = team_id
                team['stam_number'] = stam_number
                team['name'] = f'{club_name} {team_suffix}'
                teams.append(team)
    return teams


def get_club_id_from_team_id(team_id: int) -> int:
    team_info = requests.get(
        f'http://database:5000/db/team/{team_id}').json()['data']
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


def get_fixture(match_id: int) -> dict:
    match = \
        requests.get(f'http://database:5000/db/match/{match_id}').json()[
            'data']

    data = set_match_team_names(match)
    data['home_team'] = get_team_name(match['team_home_id'])
    data['away_team'] = get_team_name(match['team_away_id'])
    data['home_score'] = match['goals_home']
    data['away_score'] = match['goals_away']
    data['match_id'] = match_id
    return data


def get_all_referees() -> list:
    referees = \
        requests.get(f'http://database:5000/db/all_referees').json()['data'][
            'referees']
    return referees


def get_referee(ref_id: int) -> list:
    referee = \
        requests.get(f'http://database:5000/db/referee/{ref_id}').json()[
            'data']
    return referee


def get_admin_number(user_id: int) -> int:
    return 0 if not is_admin(user_id) else 1


def get_match_names(matches: list) -> list:
    for match in matches:
        match = set_match_team_names(match)
    return matches


def get_form_data(request: any) -> any:
    json_data = json.dumps(remove_redundant_array(dict(request.form.lists())))
    return json_data


def get_all_teams() -> list:
    teams = requests.get(f'http://database:5000/db/all_teams').json()['data'][
        'teams']
    for team in teams:
        team['team_name'] = get_team_name(team['ID'])
    return teams


def get_all_statuses() -> list:
    statuses = requests.get(f'http://database:5000/db/all_statuses').json()[
        'data']['statuses']
    return statuses


def get_status(status_id: int) -> dict:
    return requests.get(f'http://database:5000/db/status/{status_id}').json()[
        'data']


def get_division(division_id: int) -> dict:
    return \
        requests.get(f'http://database:5000/db/division/{division_id}').json()[
            'data']


def create_badge(badge_class: str, content: str):
    return {'class': badge_class, 'text': content}


def add_admin_badge(user: dict) -> dict:
    user['tags'].append(create_badge('badge bg-custom-black', 'Admin'))
    return user


def add_super_admin_badge(user: dict) -> dict:
    user['tags'].append(create_badge('badge bg-custom-blue', 'Super Admin'))
    return user


def add_club_badge(user: dict) -> dict:
    user['tags'].append(create_badge('badge bg-custom-red', 'Club'))
    return user


def has_club(user_id: int) -> bool:
    return get_club_id(user_id) is not None


def get_all_users() -> list:
    users = requests.get(f'http://database:5000/db/all_users').json()['data'][
        'users']
    print(users)
    for user in users:
        user['tags'] = list()
        if is_admin(user['ID']):
            if is_super_admin(user['ID']):
                user = add_super_admin_badge(user)
            else:
                user = add_admin_badge(user)
        if has_club(user['ID']):
            user = add_club_badge(user)

    return users


def get_single_user(user_id: int) -> dict:
    user = requests.get(f'http://database:5000/db/user/{user_id}').json()[
        'data']
    if is_super_admin(user_id):
        user['admin'] = 2
    elif is_admin(user_id):
        user['admin'] = 1
    else:
        user['admin'] = 0
    return user


def get_single_team(team_id: int) -> dict:
    team = requests.get(f'http://database:5000/db/team/{team_id}').json()[
        'data']
    return team


def get_all_clubs() -> list:
    clubs = requests.get(f'http://database:5000/db/all_clubs').json()['data'][
        'clubs']
    return clubs


def get_time(time: str) -> datetime.timedelta:
    time_split = time.split(':')
    return datetime.timedelta(hours=int(time_split[0]),
                              minutes=int(time_split[1]),
                              seconds=int(time_split[2]))


def has_overlap(match_1: dict, match_2: dict,
                match_duration_min: int = 90) -> bool:
    if match_1['date'] != match_2['date']:
        return False
    match_1_begin = get_time(match_1['time'])
    match_1_end = match_1_begin + datetime.timedelta(minutes=match_duration_min)
    match_2_begin = get_time(match_2['time'])
    match_2_end = match_2_begin + datetime.timedelta(minutes=match_duration_min)
    # No overlap since one ends earlier than the other
    # Otherwise we know there is overlap in the matches
    return not (match_1_end < match_2_begin or match_2_end < match_1_begin)


def is_own_match(match_1: dict, match_2: dict) -> bool:
    return match_1['ID'] == match_2['ID']


def is_available(match: dict, ref_id: int, all_matches: list) -> bool:
    referee_matches = get_ref_matches(all_matches, ref_id)

    print(referee_matches)
    for referee_match in referee_matches:
        if is_own_match(match, referee_match):
            continue
        if has_overlap(match, referee_match):
            return False
    return True


def get_all_matches() -> list:
    matches = \
        requests.get(f'http://database:5000/db/all_matches').json()['data'][
            'matches']
    return matches


def get_match(match_id: int) -> dict:
    match = requests.get(f'http://database:5000/db/match/{match_id}').json()[
        'data']
    return match


def get_ref_matches(matches: list, ref_id: int) -> list:
    ref_matches = list()
    for match in matches:
        if match['ref_ID'] is None:
            continue
        elif int(match['ref_ID']) == ref_id:
            ref_matches.append(match)
    return ref_matches


def response_flash(response):
    if not response:
        return
    status = response['status']
    message = response['message']
    if status == 'fail':
        flash((message, ALERT_ERROR))
    else:
        flash((message, ALERT_SUCCESS))


def is_failed_response(response) -> bool:
    return response == 'fail'
