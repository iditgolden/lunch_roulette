# coding=utf-8
import sys
import os
import elasticsearch
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import traceback
import time

from flask import Flask
from flask import request
from flask import render_template_string
from flask import jsonify
from flask import Response
from flask import stream_with_context
from flask import make_response

import requests
import functools

app = Flask(__name__)

from elasticsearch import Elasticsearch


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
    es.index(index="games", doc_type="game", id=game['id'], body=game)
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


def get_game_from_es(_id=None):
    if _id:
        game = es.get(index="games", doc_type="game", id=_id)
        game["_source"]["id"] = game["_id"]
        game["_source"]["food"] = es.get(index="foods",doc_type="food", id=game["_source"]['food_id'])['_source']
        return game["_source"]
    new_games = []
    games = es.search(index="games",body={"query":{"match_all":{}}})["hits"]["hits"]
    for game in games:
        game["_source"]["id"] = game["_id"]
        game["_source"]["food"] = es.get(index="foods",doc_type="food", id=game["_source"]['food_id'])['_source']
        new_games.append(game["_source"])
    return new_games   

    

@app.route('/food/add/',methods=['GET', 'POST'])
def add_food():
    data = request.data
    if request.form:
        data = request.form.keys()[0]
    food = es.index(index="foods", doc_type="food", body=data)
    return jsonify(**food), 200, None



@app.route('/food/',methods=['GET'])
def get_food():
    new_foods = []
    foods = es.search(index="foods", body={"query":{"match_all":{}}})["hits"]["hits"]  
    for food in foods:
        food["_source"]["id"] = food["_id"]
        new_foods.append(food["_source"])
    
    return jsonify(**{"data":new_foods}), 200, None


@app.route('/user/add/',methods=['GET', 'POST'])
def add_user():
    data = request.data
    if request.form:
        data = request.form.keys()[0]
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
    

    
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)