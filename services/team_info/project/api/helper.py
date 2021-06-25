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
        f'http://database:5000/db/teams/{team_id}').json()['data']
    team_suffix = team['suffix']
    stam_number = int(team['stamNumber'])
    club_name = requests.get(
        f'http://database:5000/db/clubs/{stam_number}').json()[
        'data']['name']
    team_name = f'{club_name} {team_suffix}'
    return team_name


def filter_match_data(matches: list) -> list:
    match_list = list()
    for match in matches:
        match_dict = get_default_match()

        home_team_name = get_team_name(match['team_home_ID'])
        away_team_name = get_team_name(match['team_home_ID'])
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
    print(team_matches)
    team_info['last_three'] = filter_match_data(historical_matches[:3])
    return team_info


def get_team_name_for_info(team_info: dict, team_id: int) -> dict:
    team_info['team_name'] = get_team_name(team_id)
    return team_info


def get_team_info(team_id: int) -> dict:
    team_info = get_default_team()
    team_info = get_historical_scores(team_info, team_id)
    team_info = get_future_scores(team_info, team_id)
    team_info = get_team_name_for_info(team_info, team_id)
    return team_info
