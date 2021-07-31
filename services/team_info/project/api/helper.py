from project.api.config import *
from datetime import date


def get_default_team() -> dict:
    return {
        'team_name': '',
        'last_three': [],
        'future_encounters': []
    }


def get_default_match() -> dict:
    return {
        'teams': '',
        'score': '',
        'date': '',
        'ID': '',
    }


def is_null_goals(match: dict) -> bool:
    try:
        return match['goals_home'] is None or match['goals_away'] is None
    except KeyError:
        return match['goalsHome'] is None or match['goalsAway'] is None


def convert_to_date(date_str: str):
    current_day_string = date_str.split('-')
    ret_date = date(int(current_day_string[0]),
                    int(current_day_string[1]),
                    int(current_day_string[2]))
    return ret_date


def sort_matches_date(vs_matches: list):
    return sorted(vs_matches, key=lambda x: convert_to_date(x['date']))


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


def filter_match_data(matches: list) -> list:
    match_list = list()
    for match in matches:
        match_dict = get_default_match()

        home_team_name = get_team_name(match['team_home_id'])
        away_team_name = get_team_name(match['team_home_id'])
        vs_name = f'{home_team_name} (H) - {away_team_name} (A)'

        match_dict['teams'] = vs_name
        match_dict['ID'] = match['ID']
        match_dict['date'] = match['date']
        if not is_null_goals(match):
            match_dict[
                'score'] = f'{match["goals_home"]} - {match["goals_away"]}'
        match_list.append(match_dict)
    return match_list


def get_future_matches(matches: list) -> list:
    future_match = list()
    for match in matches:
        if not is_history_match(match):
            future_match.append(match)
    return future_match


def get_future_scores(team_info: dict, team_id: int) -> dict:
    team_matches = requests.get(
        f'http://database:5000/db/all_team_matches/{team_id}').json()[
        'data']['matches']
    team_matches = sort_matches_date(team_matches)
    future_matches = get_future_matches(team_matches)
    team_info['future_encounters'] = filter_match_data(future_matches)
    return team_info


def is_history_match(match: dict) -> bool:
    match_day = convert_to_date(match['date'])
    current_day = date.today()
    return current_day > match_day


def get_historical_matches(matches: list) -> list:
    history_matches = list()
    for match in matches:
        if is_history_match(match):
            history_matches.append(match)
    return history_matches


def get_historical_scores(team_info: dict, team_id: int) -> dict:
    team_matches = requests.get(
        f'http://database:5000/db/all_team_matches/{team_id}').json()[
        'data']['matches']
    team_matches = sort_matches_date(team_matches)
    historical_matches = get_historical_matches(team_matches)
    team_info['last_three'] = filter_match_data(historical_matches[:3])
    return team_info


def get_team_name_for_info(team_info: dict, team_id: int) -> dict:
    team_info['team_name'] = get_team_name(team_id)
    return team_info


def set_vs_team_name_match(match: dict):
    home_team_id = int(match['team_home_id'])
    home_team_name = get_team_name(home_team_id)
    away_team_id = int(match['team_away_id'])
    away_team_name = get_team_name(away_team_id)
    match['teams'] = f'{home_team_name} (H) - {away_team_name} (A)'
    return match


def create_default_team():
    return {
        'team_id': None,
        'stam_number': None,
        'name': None
    }


def is_team_in_here(teams: list, team_id: int):
    for team in teams:
        if team['team_id'] == team_id:
            return True
    return False


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


def get_match_weeks(matches):
    match_weeks = set()

    print(matches)
    for match in matches:
        match_weeks.add(int(match['week']))
    return list(match_weeks)


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


def get_matches(season: int, division: int) -> list:
    all_matches = \
        requests.get(f'http://database:5000/db/all_matches').json()['data'][
            'matches']
    ret_matches = list()
    for match in all_matches:
        if is_valid_match(match, season, division):
            ret_matches.append(match)
    return ret_matches


def is_valid_match(match, season: int, division: int):
    return match['season_ID'] == season and match['division_ID'] == division


def get_team_info(team_id: int) -> dict:
    team_info = get_default_team()
    team_info = get_historical_scores(team_info, team_id)
    team_info = get_future_scores(team_info, team_id)
    team_info = get_team_name_for_info(team_info, team_id)
    return team_info


def give_team_names(matches: list):
    for match in matches:
        match = set_vs_team_name_match(match)
    return matches


def get_private_fixtures(team_id: int) -> dict:
    data = dict()
    data['team_name'] = get_team_name(team_id)
    all_matches = requests.get(
        f'http://database:5000/db/all_team_home_matches/{team_id}').json()[
        'data']['matches']
    all_matches = give_team_names(all_matches)
    data['matches'] = sort_matches_date(get_historical_matches(all_matches))[
                      ::-1]
    return data


def get_public_fixtures(team: int, week: int, season: int,
                        division: int) -> dict:
    data = dict()
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
    return data
