'''
Created on Jul 23, 2015

@author: udy
'''

from elasticsearch import Elasticsearch

es = Elasticsearch("10.20.5.53:9200")
from datetime import datetime, timedelta

DATE_FORAMT = "%Y-%m-%dT%H:%M:%S"

def get_active_about_to_end_games():
    games = es.search(index="games",body={"query":{"match_all":{}}})["hits"]["hits"]
    games_to_make_draw = []
    for game in games:
        date = game["_source"]["date"]
        date = datetime.strptime(date, DATE_FORAMT)
        if game.get('status') in  ["Decided", "Ended"]:
            continue
        if date - timedelta(days=1) < datetime.now():
            games_to_make_draw.append(game)
    return games_to_make_draw 



def get_decided_games():
    games = es.search(index="games",body={"query":{"match_all":{}}})["hits"]["hits"]
    decided_games = []
    for game in games:
        if game['status'] == "Decided":
            decided_games.append(game)
    return decided_games 

def update_game(game):
    es.index(index="games", doc_type="game", id=game['id'], body=game)
    return game


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

 
def get_food_from_es(_id=None):
    if _id:
        game = es.get(index="foods", doc_type="food", id=_id)
        game["_source"]["id"] = game["_id"]
        return game["_source"]
    new_games = []
    games = es.search(index="foods",body={"query":{"match_all":{}}})["hits"]["hits"]
    for game in games:
        game["_source"]["id"] = game["_id"]
        new_games.append(game["_source"])
    return new_games   