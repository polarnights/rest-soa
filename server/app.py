import helper_profile
import helper_stat
from flask import send_from_directory
from flask import Flask, abort, request

app = Flask(__name__, static_url_path='/pdfs')

@app.route('/profiles/<int:profile_id>/', methods=['GET'])
def get_profile(profile_id):
    response = helper_profile.get_profile(profile_id)

    if response is None:
        abort(404)
    
    return response

@app.route('/profiles', methods=['GET'])
def get_all_profiles():
    return helper_profile.get_all_profiles()


@app.route('/profiles', methods=['POST'])
def add_profile():
    
    if not request.json or not 'nickname' in request.json:
        abort(400)
    
    nickname = request.get_json()['nickname']

    if not request.json or not 'profile_picture' in request.json:
        abort(400)
    
    profile_picture = request.get_json()['profile_picture']

    if not request.json or not 'gender' in request.json:
        abort(400)
    
    gender = request.get_json()['gender']

    if not request.json or not 'email' in request.json:
        abort(400)
    
    email = request.get_json()['email']
    response = helper_profile.add_user(nickname, profile_picture, gender, email)

    if response is None:
        abort(400)

    return response


@app.route('/profiles/<int:profile_id>/', methods=['PUT'])
def update_prof(profile_id):

    nickname = None
    if 'nickname' in request.json:
        nickname = request.get_json()['nickname']
    
    profile_picture = None
    if 'profile_picture' in request.json:
        profile_picture = request.get_json()['profile_picture']

    gender = None
    if 'gender' in request.json:
        gender = request.get_json()['gender']

    email = None
    if 'email' in request.json:
        email = request.get_json()['email']

    response = helper_profile.get_profile(profile_id)

    if response is None:
        response = helper_profile.add_user_key(profile_id, nickname, profile_picture, gender, email)
        if response is None:
            abort(400)
        return helper_profile.get_profile(profile_id)

    response = helper_profile.update_profile(profile_id, nickname, profile_picture, gender, email)

    if response is None:
        abort(400)

    return response



@app.route('/profiles/<int:profile_id>/', methods=['DELETE'])
def delete_task(profile_id):

    response = helper_profile.get_profile(profile_id)

    if response is None:
        abort(404)

    response = helper_profile.remove_profile(profile_id)

    return response

@app.route('/stat/<int:profile_id>/', methods=['GET'])
def get_statistic_async(profile_id):

    response = helper_stat.get_stat_async(profile_id)

    if response is None:
        abort(404)

    return response

@app.route('/stat/<int:profile_id>/', methods=['PUT'])
def put_new_stat(profile_id):

    response = helper_stat.update_stat(profile_id, request)

    if response is None:
        abort(404)

    return response

@app.route('/pdf/<path:path>')
def send_report(path):
    return send_from_directory('/pdfs', path)