from project.api.config import *
from datetime import date


def get_default_fixture() -> dict:
    return {
        'date': '',
        'time': '',
        'day': '',
        'ref_name': '',
        'home_team_name': '',
        'away_team_name': '',
        'weather': '',
        'head_to_head': {
            'GP': 0,
            'W': 0
        },
        'history_scores': [],
        'current_form_H': '',
        'current_form_A': ''
    }


def convert_to_date(date_str: str):
    current_day_string = date_str.split('-')
    ret_date = date(int(current_day_string[0]),
                    int(current_day_string[1]),
                    int(current_day_string[2]))
    return ret_date


def is_null_goals(match: dict) -> bool:
    return match['goals_home'] is None or match['goals_away'] is None


def count_vs_matches(vs_matches: list) -> int:
    counter = 0
    for match in vs_matches:
        if is_null_goals(match):
            continue
        counter += 1
    return counter


def is_home(match: dict, team_id: int):
    return match['team_home_ID'] == team_id


def is_draw(match: dict):
    return int(match['goals_home']) == int(match['goals_away'])


def home_wins_match(match: dict, team_id: int) -> bool:
    if is_draw(match):
        return False

    home_wins = int(match['goals_home']) > int(match['goals_away'])
    if is_home(match, team_id):
        return home_wins
    return not home_wins


def count_winning_matches(vs_matches, team_id) -> int:
    counter = 0
    for match in vs_matches:
        if not is_null_goals(match) and home_wins_match(match, team_id):
            counter += 1
    return counter


def count_draw_matches(vs_matches) -> int:
    counter = 0
    for match in vs_matches:
        if not is_null_goals(match) and is_draw(match):
            counter += 1
    return counter


def get_current_form_string(team_id: int):
    team_matches = requests.get(
        f'http://database:5000/db/all_team_matches/{team_id}').json()[
        'data']['matches']
    team_matches = sort_matches_date(team_matches)
    team_matches_string = ''
    for match in team_matches[:5]:
        team_matches_string += get_str_match(match, team_id)
    return team_matches_string


def get_current_form(all_fixture_info: dict, fixture_info: dict) -> dict:
    team_1_id = int(all_fixture_info['teamHomeID'])
    fixture_info['current_form_H'] = get_current_form_string(team_1_id)
    team_2_id = int(all_fixture_info['teamAwayID'])
    fixture_info['current_form_A'] = get_current_form_string(team_2_id)
    return fixture_info


def get_str_match(match: dict, team_id: int):
    if is_draw(match):
        return 'D'
    if is_home(match, team_id) and home_wins_match(match, team_id):
        return 'W'
    return 'L'


def get_head_to_head(all_fixture_info: dict, fixture_info: dict) -> dict:
    team_1_id = int(all_fixture_info['teamHomeID'])
    team_2_id = int(all_fixture_info['teamAwayID'])
    vs_matches = requests.get(
        f'http://database:5000/db/all_vs_matches?team1={team_1_id}&team2={team_2_id}').json()[
        'data']['matches']
    fixture_info['head_to_head']['GP'] = count_vs_matches(vs_matches)
    fixture_info['head_to_head']['W'] = count_winning_matches(vs_matches,
                                                              team_1_id)
    fixture_info['head_to_head']['D'] = count_draw_matches(vs_matches)
    return fixture_info


def sort_matches_date(vs_matches: list):
    return sorted(vs_matches, key=lambda x: convert_to_date(x['date']))


def get_historical_scores(all_fixture_info: dict, fixture_info: dict) -> dict:
    team_1_id = int(all_fixture_info['teamHomeID'])
    team_2_id = int(all_fixture_info['teamAwayID'])
    vs_matches = requests.get(
        f'http://database:5000/db/all_vs_matches?team1={team_1_id}&team2={team_2_id}').json()[
        'data']['matches']
    vs_matches = sort_matches_date(vs_matches)
    fixture_info['history_scores'] = [
        f'{match["goals_home"]}-{match["goals_away"]}' for match in
        vs_matches[:3]]
    return fixture_info


def get_weather(all_fixture_info: dict, fixture_info: dict) -> dict:
    current_day = convert_to_date(all_fixture_info['mDate'])
    match_day = date.today()
    day_delta = current_day - match_day
    if day_delta.days < 0 or day_delta.days > 7:
        return fixture_info
    weather_string = requests.get(
        f'http://weather:5000/srv/weather/get_weather?day={day_delta.days}').json()
    fixture_info['weather'] = weather_string
    return fixture_info


def get_team_names(all_fixture_info: dict, fixture_info: dict) -> dict:
    for call_id in [('teamHomeID', 'home_team_name'),
                    ('teamAwayID', 'away_team_name')]:
        team = \
            requests.get(
                f'http://database:5000/db/teams/{all_fixture_info[call_id[0]]}').json()[
                'data']
        team_suffix = team['suffix']
        stam_number = team['stamNumber']
        club_name = requests.get(
            f'http://database:5000/db/clubs/{stam_number}').json()[
            'data']['name']
        fixture_info[call_id[1]] = f'{club_name} {team_suffix}'
    return fixture_info


def get_referee(all_fixture_info: dict, fixture_info: dict) -> dict:
    ref_id = all_fixture_info['refID']
    if ref_id is None:
        return fixture_info
    ref_id = int(ref_id)
    ref_info = \
        requests.get(f'http://database:5000/db/referees/{ref_id}').json()[
            'data']
    fixture_info['ref_name'] = f'{ref_info["firstName"]} {ref_info["lastName"]}'
    return fixture_info


def get_week_day_name(current_date: str) -> str:
    return convert_to_date(current_date).strftime("%A")


def get_date(current_date: str) -> str:
    date_time_object = convert_to_date(current_date)
    return date_time_object.strftime('%d/%m')


def get_date_time(all_fixture_info: dict, fixture_info: dict) -> dict:
    fixture_info['time'] = all_fixture_info['mTime']
    date_str = all_fixture_info['mDate']
    fixture_info['day'] = get_week_day_name(date_str)
    fixture_info['date'] = get_date(date_str)
    print(get_date(date_str))
    return fixture_info


def get_fixture_info(fixture_id: int) -> dict:
    all_fixture_info = requests.get(
        f'http://database:5000/db/matches/{fixture_id}').json()['data']
    fixture_info = get_default_fixture()
    fixture_info = get_date_time(all_fixture_info, fixture_info)
    fixture_info = get_referee(all_fixture_info, fixture_info)
    fixture_info = get_team_names(all_fixture_info, fixture_info)
    fixture_info = get_weather(all_fixture_info, fixture_info)
    fixture_info = get_head_to_head(all_fixture_info, fixture_info)
    fixture_info = get_historical_scores(all_fixture_info, fixture_info)
    fixture_info = get_current_form(all_fixture_info, fixture_info)
    return fixture_info
