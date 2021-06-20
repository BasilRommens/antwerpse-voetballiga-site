def is_valid_match(match, season: int, division: int):
    return match['seasonID'] == season and match['divisionID'] == division


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


def add_teams(league_table: dict, matches: list):
    for match in matches:
        for team_id_name in ["teamHomeID", "teamAwayID"]:
            team = \
                requests.get(
                    f'http://database:5000/db/teams/{match[team_id_name]}').json()[
                    'data']
            team_id = team['id']
            stam_number = team['stamNumber']
            if not is_team_in_here(league_table, team_id):
                league_table['teams'].append(
                    {'team_id': team_id, 'stam_number': stam_number})


def add_matches_total(league_table: dict, matches: list):
    return


def add_matches_result(league_table: dict, matches: list):
    return


def add_matches_goals(league_table: dict, matches: list):
    return


def add_table_standing(league_table: dict, matches: list):
    return


def generate_league_table(season: int, division: int) -> dict:
    matches = get_matches(season, division)
    league_table = dict()
    add_teams(league_table, matches)
    add_matches_total(league_table, matches)
    add_matches_result(league_table, matches)
    add_matches_goals(league_table, matches)
    add_table_standing(league_table, matches)
    return jsonify(league_table)
