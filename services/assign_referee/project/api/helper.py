from project.api.config import *
import datetime


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


def get_all_referees() -> list:
    referees = \
        requests.get(f'http://database:5000/db/all_referees').json()['data'][
            'referees']
    return referees


def get_ref_matches(matches: list, ref_id: int) -> list:
    ref_matches = list()
    for match in matches:
        if match['ref_ID'] is None:
            continue
        elif int(match['ref_ID']) == ref_id:
            ref_matches.append(match)
    return ref_matches


def get_all_available_referees(match_id: int) -> list:
    referees = get_all_referees()
    match = get_match(match_id)
    matches = get_all_matches()
    return [referee for referee in referees if
            is_available(match, int(referee['ID']), matches)]
