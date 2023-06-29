import sqlite3
from flask import jsonify, url_for

DB_PATH = './profiles.db' 
NOTSTARTED = 'Not Started'

def make_public_profile(row):
    res = {}
    for field in row.keys():
        if field == 'profile_id':
            res['uri'] = url_for('get_profile', profile_id = row['profile_id'], _external = True)
        else:
            res[field] = row[field]

    return res

def get_all_profiles():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('select * from profiles')
        rows = c.fetchall()
        result = jsonify( { 'profiles': list(map(make_public_profile, rows)) } )
        return result
    except Exception as e:
        print('Error: ', e)
        return None

def get_profile(profile_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("select * from profiles where profile_id=?;" , [profile_id])
        r = c.fetchone()
        return jsonify(make_public_profile(r))
    except Exception as e:
        print('Error: ', e)
    return None


def add_user(nickname, profile_picture, gender, email):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('insert into profiles(nickname, pp, gender, email) values(?,?, ?, ?)', (nickname, profile_picture, gender, email))
        conn.commit()
        result = get_profile(c.lastrowid)
        return result
    except Exception as e:
        print('Error: ', e)
        return None

def add_user_key(profile_id, nickname, profile_picture, gender, email):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('insert into profiles(profile_id, nickname, pp, gender, email) values(?, ?,?, ?, ?)', (profile_id, nickname, profile_picture, gender, email))
        conn.commit()
        result = profile_id
        return result
    except Exception as e:
        print('Error: ', e)
        return None

def update_profile(profile_id, nickname, profile_picture, gender, email):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if (nickname):
            c.execute('update profiles set nickname=? where profile_id=?', (nickname, profile_id))
        if (profile_picture):
            c.execute('update profiles set pp=? where profile_id=?', (profile_picture, profile_id))
        if (gender):
            c.execute('update profiles set gender=? where profile_id=?', (gender, profile_id))
        if (email):
            c.execute('update profiles set email=? where profile_id=?', (email, profile_id))
        conn.commit()
        result = get_profile(profile_id)
        return result
    except Exception as e:
        print('Error: ', e)
        return None

def remove_profile(profile_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM profiles WHERE profile_id=?', [profile_id])
        conn.commit()
        return jsonify( { 'result': True } )
    except Exception as e:
        print('Error: ', e)
        return None