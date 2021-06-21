from project.api.config import *

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
    try:
        db.session.add(Match(goalsHome=goalsHome, goalsAway=goalsAway, matchStatus=matchStatus, mDate=mDate, mTime=mTime,
                             teamHomeID=teamHomeID, teamAwayID=teamAwayID, divisionID=divisionID, seasonID=seasonID, refID=refID))

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


@match_blueprint.route('/db/update_match', methods=['UPDATE'])
def update_match():
    post_data = request.get_json()
    response_object = {'status': 'fail', 'message': 'Invalid payload.'}
    if not post_data:
        return jsonify(response_object), 400
    match_id = post_data.get('ID')
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
    try:
        # Check for match existence
        match = Match.query.filter_by(ID=match_id).first()
        if not match:
            response_object['message'] = 'Sorry. Can\'t update match'
            return jsonify(response_object), 400
        else:
            match.update({Match.goalsHome: goalsHome, Match.goalsAway: goalsAway, Match.matchStatus: matchStatus, Match.mDate: mDate, Match.mTime: mTime,
                          Match.teamHomeID: teamHomeID, Match.teamAwayID: teamAwayID, Match.divisionID: divisionID, Match.seasonID: seasonID, Match.refID: refID})
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
                'data': {
                    'ID': match.ID,
                    'goalsHome': match.goalsHome,
                    'goalsAway': match.goalsAway,
                    'matchStatus': match.matchStatus,
                    'mDate': str(match.mDate),
                    'mTime': str(match.mTime),
                    'teamHomeID': match.teamHomeID,
                    'teamAwayID': match.teamAwayID,
                    'divisionID': match.divisionID,
                    'seasonID': match.seasonID,
                    'refID': match.refID
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


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
