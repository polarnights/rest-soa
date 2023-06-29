
@app.route('/stat/<int:profile_id>/', methods=['PUT'])
def post_statistic_update(profile_id):

	game_count = None
	if 'game_count' in request.json:
		game_count = request.get_json()['game_count']

	win_count = None
	if 'win_count' in request.json:
		win_count = request.get_json()['win_count']

	loss_count = None
	if 'loss_count' in request.json:
		loss_count = request.get_json()['loss_count']

	gametime = None
	if 'gametime' in request.json:
		gametime = request.get_json()['gametime']

	response = helper_profile.get_profile(profile_id)
	#response = helper_stat.update_stat(profile_id, game_count, win_count, loss_count, gametime)

	#if response is None:
	#	abort(400)

	return response