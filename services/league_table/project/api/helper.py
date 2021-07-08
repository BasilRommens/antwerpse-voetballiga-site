from project.api.config import *


def is_valid_match(match, season: int, division: int):
    return match['season_ID'] == season and match['division_ID'] == division


def get_matches(season: int, division: int) -> list:
    all_matches = \
        requests.get(
            f'http://database:5000/db/all_matches_div_season?division={division}&season={season}').json()[
            'data'][
            'matches']
    return all_matches


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
        'F': None,
        'A': None,
        'GP': None,
        'L': None,
        'W': None,
        'D': None,
        'Pts': None,
        'ranking': None
    }


def get_club(stam_number: int) -> dict:
    club = requests.get(
        f'http://database:5000/db/club/{stam_number}').json()[
        'data']
    return club


def add_teams(league_table: dict, matches: list):
    league_table['teams'] = list()
    for match in matches:
        for team_id_name in ["team_home_ID", "team_away_ID"]:
            team = \
                requests.get(
                    f'http://database:5000/db/team/{match[team_id_name]}').json()[
                    'data']
            team_id = team['id']
            stam_number = team['stamNumber']
            if not is_team_in_here(league_table, team_id):
                team_suffix = team['suffix']
                club_name = get_club(stam_number)['name']
                team = create_default_team()
                team['team_id'] = team_id
                team['stam_number'] = stam_number
                team['name'] = f'{club_name} {team_suffix}'
                league_table['teams'].append(team)
    return league_table


def has_home_won(match: dict):
    return match['goals_home'] > match['goals_away']


def is_draw(match: dict):
    return match['goals_home'] == match['goals_away']


def increase(letter: str, league_table: dict, team_id: int, amount: int = 1):
    for team in league_table['teams']:
        if team['team_id'] == team_id:
            if team[letter] is None:
                team[letter] = amount
                continue
            else:
                team[letter] += amount
    return league_table


def set_ranking(league_table: dict, team_id: int, ranking: int):
    for team in league_table['teams']:
        if team['team_id'] == team_id:
            team['ranking'] = ranking
    return league_table


def increase_draw(league_table: dict, team_id: int):
    league_table = increase('D', league_table, team_id)
    return league_table


def increase_win(league_table: dict, team_id: int):
    league_table = increase('W', league_table, team_id)
    return league_table


def increase_loss(league_table: dict, team_id: int):
    league_table = increase('L', league_table, team_id)
    return league_table


def increase_matches_played(league_table: dict, team_id: int):
    league_table = increase('GP', league_table, team_id)
    return league_table


def increase_points_draw(league_table: dict, team_id: int):
    league_table = increase('Pts', league_table, team_id, 1)
    return league_table


def increase_points_win(league_table: dict, team_id: int):
    league_table = increase('Pts', league_table, team_id, 3)
    return league_table


def add_goals_for(league_table: dict, team_id: int, amount: int):
    league_table = increase('F', league_table, team_id, amount)
    return league_table


def add_goals_against(league_table: dict, team_id: int, amount: int):
    league_table = increase('A', league_table, team_id, amount)
    return league_table


def is_null_goals(match: dict):
    return match['goals_home'] is None or match['goals_away'] is None


def add_matches_played(league_table: dict, matches: list):
    for match in matches:
        if is_null_goals(match):
            continue
        # update the games played score
        for call_ids in ["team_home_ID", "team_away_ID"]:
            team_id = match[call_ids]
            league_table = increase_matches_played(league_table, team_id)
        # update the win/loss/draw scores
        if is_draw(match):
            for call_ids in ["team_home_ID", "team_away_ID"]:
                team_id = match[call_ids]
                league_table = increase_draw(league_table, team_id)
        elif has_home_won(match):
            home_team_id = match['team_home_ID']
            league_table = increase_win(league_table, home_team_id)
            away_team_id = match['team_away_ID']
            league_table = increase_loss(league_table, away_team_id)
        else:
            home_team_id = match['team_home_ID']
            league_table = increase_loss(league_table, home_team_id)
            away_team_id = match['team_away_ID']
            league_table = increase_win(league_table, away_team_id)
    return league_table


def add_teams_points(league_table: dict, matches: list):
    for match in matches:
        if is_null_goals(match):
            continue
        if is_draw(match):
            for call_ids in ["team_home_ID", "team_away_ID"]:
                team_id = match[call_ids]
                league_table = increase_points_draw(league_table, team_id)
        elif has_home_won(match):
            home_team_id = match['team_home_ID']
            league_table = increase_points_win(league_table, home_team_id)
        else:
            away_team_id = match['team_away_ID']
            league_table = increase_points_win(league_table, away_team_id)
    league_table = clean_up_points(league_table)
    return league_table


def clean_up_points(league_table: dict) -> dict:
    for team in league_table['teams']:
        for match_outcome_letter in ['L', 'D', 'W', 'Pts']:
            if team[match_outcome_letter] is None:
                team[match_outcome_letter] = 0
    return league_table


def clean_up_goals(league_table: dict) -> dict:
    for team in league_table['teams']:
        for goal_type_letter in ['F', 'A']:
            if team[goal_type_letter] is None:
                team[goal_type_letter] = 0
    return league_table


def add_matches_goals(league_table: dict, matches: list):
    for match in matches:
        if is_null_goals(match):
            continue
        goals_home = match['goals_home']
        goals_against = match['goals_away']
        home_team_id = match['team_home_ID']
        league_table = add_goals_for(league_table, home_team_id, goals_home)
        league_table = add_goals_against(league_table, home_team_id,
                                         goals_against)
        away_team_id = match['team_away_ID']
        league_table = add_goals_for(league_table, away_team_id, goals_against)
        league_table = add_goals_against(league_table, away_team_id, goals_home)
    league_table = clean_up_goals(league_table)
    return league_table


def clean_up_ranking(league_table: dict):
    for team in league_table['teams']:
        if team['ranking'] is None:
            team['ranking'] = 0
    return league_table


def add_table_ranking(league_table: dict):
    league_table['teams'] = sorted(league_table['teams'],
                                   key=lambda x: x['Pts'], reverse=True)
    for idx in range(len(league_table['teams'])):
        league_table['teams'][idx]['ranking'] = idx + 1
    return league_table


def generate_league_table(season: int, division: int) -> dict:
    matches = get_matches(season, division)
    league_table = dict()
    league_table = add_teams(league_table, matches)
    league_table = add_matches_played(league_table, matches)
    league_table = add_teams_points(league_table, matches)
    league_table = add_matches_goals(league_table, matches)
    # This function must stand at the end, because otherwise the final scores
    # would be calculated wrong
    league_table = add_table_ranking(league_table)
    return league_table
