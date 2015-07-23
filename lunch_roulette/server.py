# coding=utf-8
import sys
import os
import elasticsearch
from lunch_roulette.elasticsearch_utils import update_game
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import worker
import traceback
import time,json

from flask import Flask
from flask import request
from flask import render_template_string
from flask import jsonify
from flask import Response
from flask import stream_with_context
from flask import make_response
import draw

import requests
import functools

app = Flask(__name__)

from elasticsearch import Elasticsearch
from elasticsearch_utils import get_game_from_es, get_food_from_es

es = Elasticsearch("10.20.5.53:9200")
@app.route('/')
def help():
    return "lunch roulette"

@app.route('/game/add',methods=['GET', 'POST'])
@app.route('/game/add/',methods=['GET', 'POST'])
def add_game():
    data = request.data
    if request.form:
        data = request.form.keys()[0]
    game = es.index(index="games", doc_type="game", body=data)
    return jsonify(**game), 200, None


@app.route('/game/join',methods=['GET', 'POST'])
def join_game():
    user_id = request.args.get("user_id")
    game_id = request.args.get("game_id")
    if not user_id or not game_id:
        raise Exception("must supply 'user_id' and 'game_id'")
    print user_id, game_id
    game = get_game_from_es(game_id)
    participents = game.get('participents_ids',[])
    participents.append(user_id)
    game['participents_ids'] = sorted(list(set(participents)))
    update_game(game)
    return jsonify(**game), 200, None

    
@app.route('/game',methods=['GET'])
@app.route('/game/',methods=['GET'])
@app.route('/game/<path:_id>',methods=['GET'])
@app.route('/game/<path:_id>/',methods=['GET'])
def get_game(_id=""):
    if _id:
        game = get_game_from_es(_id)
        return jsonify(**game), 200, None
    
    games = get_game_from_es()
    return jsonify(**{"data":games}), 200, None



   

@app.route('/food/add/',methods=['GET', 'POST'])
def add_food():
    data = request.data
    if request.form:
        data = request.form.keys()[0]
    food = es.index(index="foods", doc_type="food", body=data)
    return jsonify(**food), 200, None

@app.route('/food/update',methods=['GET', 'POST'])
@app.route('/food/update/',methods=['GET', 'POST'])
@app.route('/food/update/<path:_id>',methods=['GET', 'POST'])
@app.route('/food/update/<path:_id>/',methods=['GET', 'POST'])
def update_food(_id=""):
    data = request.data
    if request.form:
        data = request.form.keys()[0]
    if not _id:
        _id = data['id']
    if not _id:
        raise Exception("failed to get the id. must supply id as path or in body")
    
    food = get_food_from_es(_id)
    food.update(json.loads(data))
    food = es.index(index="foods", doc_type="food", body=food, id=_id)
    return jsonify(**food), 200, None


@app.route('/food/',methods=['GET'])
def get_food():
    foods = get_food_from_es()
    return jsonify(**{"data":foods}), 200, None


@app.route('/user/add/',methods=['GET', 'POST'])
def add_user():
    data = request.data
    if request.form:
        data = request.form.keys()[0]
        data = json.loads(data)
    email = data.get("email")
    password = data.get("10bis_pass")
    if not password or not email:
        raise Exception("must supply 'password' and 'email'")
    
    master_user = "idit@taykey.com"
    user_id_10bis = worker.give_master_permissions(email, password, master_user)
    data["user_id_10bis"] = user_id_10bis
    user = es.index(index="users", doc_type="user", body=data)
    return jsonify(**user), 200, None
    
    
@app.route('/user/',methods=['GET', 'POST'])
@app.route('/user/<path:_id>',methods=['GET'])
def get_user(_id=""):
    if _id:
        user = es.get(index="users", doc_type="user", id=_id)
        return jsonify(**user["_source"]), 200, None

    new_users = []
    users = es.search(index="users", body={"query":{"match_all":{}}})["hits"]["hits"]  
    for user in users:
        user["_source"]["id"] = user["_id"]
        new_users.append(user["_source"])
    
    return jsonify(**{"data":new_users}), 200, None
    


@app.route('/login' ,methods=['GET', 'POST'])
@app.route('/login/',methods=['GET','POST'])
def login(_id=""):
    email = request.args.get("email")
    password = request.args.get("password")
    
    if not password or not email:
        raise Exception("must supply 'password' and 'email'")
    print password, email
    
    users = es.search(index="users", body={"query":{"term":{"email":email}}})["hits"]["hits"]
    if not users:
        raise Exception("wrong email or password (no user)")
    user = users[0]
    if user.get("password") != password:
        raise Exception("wrong email or password (wrong pass)")
    
    return jsonify(**user), 200, None
    

@app.route('/make_draw',methods=['GET', 'POST'])
@app.route('/make_draw/',methods=['GET', 'POST'])
def make_draw(_id=""):
    games = draw.make_draw()
    return jsonify(**{"games":games}), 200, None

@app.route('/make_reservation',methods=['GET', 'POST'])
@app.route('/make_reservation/',methods=['GET', 'POST'])
def make_reservation(_id=""):
    draw.make_reservation()
    return jsonify(**{}), 200, None    
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)