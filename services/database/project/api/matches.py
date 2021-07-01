from project.api.config import *
from sqlalchemy import and_

match_blueprint = Blueprint('matches', __name__)


@match_blueprint.route('/db/matches', methods=['POST'])
def add_match():
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    goalsHome = post_data.get('goalsHome')
    goalsAway = post_data.get('goalsAway')
    matchStatus = post_data.get('matchStatus')
    mDate = post_data.get('mDate')
    mTime = post_data.get('mTime')
    teamHomeID = post_data.get('teamHomeID')
    teamAwayID = post_data.get('teamAwayID')
    divisionID = post_data.get('divisionID')
    seasonID = post_data.get('seasonID')
    refID = post_data.get('refID')
    week = post_data.get('week')
    try:
        db.session.add(Match(goalsHome=goalsHome, goalsAway=goalsAway,
                             matchStatus=matchStatus, mDate=mDate, mTime=mTime,
                             teamHomeID=teamHomeID, teamAwayID=teamAwayID,
                             divisionID=divisionID, seasonID=seasonID,
                             refID=refID, week=week))

        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = f'Match was added!'
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@match_blueprint.route('/db/delete_match/<match_id>', methods=['DELETE'])
def delete_match(match_id):
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    try:
        # Check for match existence
        match = Match.query.filter_by(ID=match_id).first()
        if not match_match:
            response_object['message'] = 'Sorry. Can\'t delete match'
            return jsonify(response_object), 400
        else:
            match.delete()
            db.session.commit()
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@match_blueprint.route('/db/update_match_score/<match_id>', methods=['PUT'])
def update_match_score(match_id=0):
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    goalsHome = post_data.get('goalsHome')
    goalsAway = post_data.get('goalsAway')
    try:
        # Check for match existence
        match = Match.query.filter_by(ID=match_id).first()
        if not match:
            response_object['message'] = 'Sorry. Can\'t update match'
            return jsonify(response_object), 400
        else:
            match.goalsHome = goalsHome
            match.goalsAway = goalsAway
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Updated match {match_id}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@match_blueprint.route('/db/update_match/<match_id>', methods=['PUT'])
def update_match(match_id):
    post_data = json.loads(request.get_json())
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    goalsHome = post_data.get('goalsHome')
    goalsAway = post_data.get('goalsAway')
    matchStatus = post_data.get('status')
    mDate = post_data.get('date')
    mTime = post_data.get('time')
    week = post_data.get('week')
    teamHomeID = post_data.get('teamHomeID')
    teamAwayID = post_data.get('teamAwayID')
    divisionID = post_data.get('divisionID')
    seasonID = post_data.get('seasonID')
    refID = post_data.get('refID')
    try:
        # Check for match existence
        match = Match.query.filter_by(ID=match_id).first()
        if not match:
            response_object['message'] = 'Sorry. Can\'t update match'
            return jsonify(response_object), 400
        else:
            match.goalsHome = goalsHome
            match.goalsAway = goalsAway
            match.matchStatus = matchStatus
            match.mDate = mDate
            match.mTime = mTime
            match.week = week
            match.teamHomeID = teamHomeID
            match.teamAwayID = teamAwayID
            match.divisionID = divisionID
            match.seasonID = seasonID
            match.refID = refID
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = f'Updated match {match_id}'
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@match_blueprint.route('/db/matches/<match_id>', methods=['GET'])
def get_single_match(match_id):
    """Get single match details"""
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        match = Match.query.filter_by(ID=int(match_id)).first()
        if not match:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': match.to_json()
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@match_blueprint.route('/db/matches_team_week', methods=['GET'])
def get_matches_team_week():
    """Get all matches per week per team"""
    division = int(request.args.get('division'))
    season = int(request.args.get('season'))
    week = int(request.args.get('week'))
    team = int(request.args.get('team'))
    home_matches = [match.to_json() for match in
                    Match.query.filter(and_(Match.seasonID == season,
                                            Match.divisionID == division,
                                            Match.week == week,
                                            Match.teamHomeID == team))]
    away_matches = [match.to_json() for match in
                    Match.query.filter(and_(Match.seasonID == season,
                                            Match.divisionID == division,
                                            Match.week == week,
                                            Match.teamAwayID == team))]

    response_object = {
        'status': 'success',
        'data': {
            'matches': home_matches + away_matches
        }
    }
    return jsonify(response_object), 200


@match_blueprint.route('/db/all_matches_div_season', methods=['GET'])
def get_all_matches_div_season():
    """Get all matches per week"""
    division = int(request.args.get('division'))
    season = int(request.args.get('season'))
    response_object = {
        'status': 'success',
        'data': {
            'matches': [match.to_json() for match in
                        Match.query.filter(and_(Match.seasonID == season,
                                                Match.divisionID == division))]
        }
    }
    return jsonify(response_object), 200


@match_blueprint.route('/db/matches_week_all', methods=['GET'])
def get_matches_all_team_week():
    """Get all matches per week"""
    division = int(request.args.get('division'))
    season = int(request.args.get('season'))
    week = int(request.args.get('week'))
    response_object = {
        'status': 'success',
        'data': {
            'matches': [match.to_json() for match in
                        Match.query.filter(and_(Match.seasonID == season,
                                                Match.divisionID == division,
                                                Match.week == week))]
        }
    }
    return jsonify(response_object), 200


def get_home_matches(team_id):
    return [match.to_json() for match in
            Match.query.filter(and_(Match.teamHomeID == team_id))]


def get_away_matches(team_id):
    return [match.to_json() for match in
            Match.query.filter(and_(Match.teamAwayID == team_id))]


@match_blueprint.route('/db/all_team_home_matches/<team_id>', methods=['GET'])
def get_all_team_home_matches(team_id=0):
    team_id = int(team_id)
    if team_id < 1:
        response_object = {
            'status': 'failed',
            'message': 'No team with such an ID found'
        }
        return jsonify(response_object), 400

    response_object = {
        'status': 'success',
        'data': {
            'matches': get_home_matches(team_id)
        }
    }

    return jsonify(response_object), 200


@match_blueprint.route('/db/all_team_matches/<team_id>', methods=['GET'])
def get_all_team_matches(team_id=0):
    team_id = int(team_id)
    if team_id < 1:
        response_object = {
            'status': 'failed',
            'message': 'No team with such an ID found'
        }
        return jsonify(response_object), 400

    response_object = {
        'status': 'success',
        'data': {
            'matches': get_home_matches(team_id) + get_away_matches(team_id)
        }
    }

    return jsonify(response_object), 200


@match_blueprint.route('/db/all_vs_matches', methods=['GET'])
def get_all_vs_matches():
    team_1_id = int(request.args.get('team1'))
    team_2_id = int(request.args.get('team2'))

    home_1_matches = [match.to_json() for match in
                      Match.query.filter(and_(Match.teamHomeID == team_1_id,
                                              Match.teamAwayID == team_2_id))]
    away_1_matches = [match.to_json() for match in
                      Match.query.filter(and_(Match.teamAwayID == team_1_id,
                                              Match.teamHomeID == team_2_id))]

    response_object = {
        'status': 'success',
        'data': {
            'matches': home_1_matches + away_1_matches
        }
    }

    return jsonify(response_object), 200


@match_blueprint.route('/db/all_matches_in_range', methods=['GET'])
def get_all_matches_in_range():
    """Get all matches in a range"""
    min = int(request.args.get('min'))
    max = int(request.args.get('max'))
    response_object = {
        'status': 'success',
        'data': {
            'matches': [Match.query.get(match_id).to_json() for match_id in
                        range(min, max + 1)]
        }
    }
    return jsonify(response_object), 200


@match_blueprint.route('/db/all_matches', methods=['GET'])
def get_all_matches():
    """Get all matches"""
    response_object = {
        'status': 'success',
        'data': {
            'matches': [match.to_json() for match in Match.query.all()]
        }
    }
    return jsonify(response_object), 200
