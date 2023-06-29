import sqlite3
import pika
from flask import jsonify, url_for, request

DB_PATH = './stat.db'
DB_PATH_PROFILE = './profiles.db' 
NOTSTARTED = 'Not Started'

cnt = 0

def update_stat(profile_id, request):
    try:
        game_count = None
        if request.json and 'game_count' in request.json:
            game_count = request.get_json()['game_count']

        win_count = None
        if request.json and 'win_count' in request.json:
            win_count = request.get_json()['win_count']

        loss_count = None
        if request.json and 'loss_count' in request.json:
            loss_count = request.get_json()['loss_count']

        gametime = None
        if request.json and 'gametime' in request.json:
            gametime = request.get_json()['gametime']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('insert into stat(profile_id, gamecnt, wincnt, losscnt, time) values(?, ?,?, ?, ?) on conflict(profile_id) do nothing', (profile_id, game_count, win_count, loss_count, gametime))
        if (game_count):
            c.execute('update stat set gamecnt=? where profile_id=?', (game_count, profile_id))
        if (win_count):
            c.execute('update stat set wincnt=? where profile_id=?', (win_count, profile_id))
        if (loss_count):
            c.execute('update stat set losscnt=? where profile_id=?', (loss_count, profile_id))
        if (gametime): 
            c.execute('update stat set time=? where profile_id=?', (gametime, profile_id))
        conn.commit()
        return jsonify( { 'result': True } )
    except Exception as e:
        print('Error: ', e, flush=True)
        return None

def add_to_queue(messg):
    connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.confirm_delivery()
    channel.queue_declare(queue='statistic_requests', durable=True)
    while (True):
        try:
            channel.basic_publish(
            exchange='',
            routing_key='statistic_requests',
            body=messg,
            properties=pika.BasicProperties(
            delivery_mode=2,    
            ),
            mandatory=True)
            break
        except Exception as inst:
            #Confirmation
            print(type(inst), flush=True)
            print(inst, flush=True)
            print('Failed', flush=True)
            time.sleep(1)
            pass

def get_stat_async(profile_id):

    data = ""
    try:
        conn = sqlite3.connect(DB_PATH_PROFILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("select * from profiles where profile_id=?;" , [profile_id])
        r = c.fetchone()
        if r is not None:
            for field in r.keys():
                data += field
                data += ':'
                data += r[field]
                data += '#'
    except Exception as e:
        print('Error: ', e, flush=True)
        return None
   
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("select * from stat where profile_id=?;" , [profile_id])
        r = c.fetchone()

        if r is not None:
            for field in r.keys():
                data += field
                data += ':'
                data += r[field]
                data += '#'
    except Exception as e:
        print('Error: ', e, flush=True)
        return None

    data += str(profile_id)
    add_to_queue(data)

    return jsonify( { 'uri': '/pdf/' + str(profile_id) + ".pdf" } )