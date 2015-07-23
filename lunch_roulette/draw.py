'''
Created on Jul 23, 2015

@author: udy
'''

import random
import elasticsearch_utils
from lunch_roulette.elasticsearch_utils import get_decided_games
from lunch_roulette import worker


def send_mail():
    pass

def make_draw():
    games = elasticsearch_utils.get_active_about_to_end_games()
    for game in games:
        participents = game.get("participents_ids")
        if len(participents) < 2:
            print "no participents"
        participents = random.shuffle(participents)[0]
        winner = participents[0]
        looser = participents[1]
        send_mail()
        game['status'] = "Decided"
        game['looser'] = [looser]
        game['winner'] = winner
        
        elasticsearch_utils.update_game(game)
    return games
        

mail = "idit@taykey.com"
password = "hachathon2015"        
def make_reservation():
    decided_games = get_decided_games()
    for decided_game in decided_games:
        decided_game['status'] = "Ended"
        elasticsearch_utils.update_game(decided_game)
        
        worker.order_meal(mail, password, str(decided_game['food']['rest_id']), str(decided_game['food']['dish_id']), decided_game["looser"])
        
        
