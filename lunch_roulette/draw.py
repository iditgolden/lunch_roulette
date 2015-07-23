'''
Created on Jul 23, 2015

@author: udy
'''
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import random
import smtplib
import elasticsearch_utils
from lunch_roulette.elasticsearch_utils import get_decided_games
from lunch_roulette import worker

email_host = "email-smtp.us-east-1.amazonaws.com"
email_user = ""
email_password = ""


def send_mail(to, from_mail, subject, body):
    if not to:
        print "mailing list is empty"
        return

    to = ",".join(to) if type(to) == list else to
    msg = MIMEMultipart()
    msg['From'] = from_mail
    msg['To'] = to
    msg['subject'] = subject
    msg.attach(MIMEText(body.encode("utf-8"), 'plain'))
    s = None
    try:
        s = smtplib.SMTP(email_host)
        s.starttls()
        s.login(email_user, email_password)
        s.sendmail(from_mail, to, msg.as_string())
        print "Mail was sent to: %s." % to
    finally:
        if s:
            s.close()


def make_draw():
    games = elasticsearch_utils.get_active_about_to_end_games()
    for game in games:
        participents = game.get("participents_ids")
        if len(participents) < 2:
            print "no participents"
        random.shuffle(participents)
        winner = participents[0]
        looser = participents[1]
        winner_user = elasticsearch_utils.get_user_from_es(winner)
        looser_user = elasticsearch_utils.get_user_from_es(looser)
        # send to winner
        send_mail(winner_user["email"], looser_user["email"], subject = "KULULU %s, You won a lunch in Lunch Roulette !!!" % winner_user["user_name"],
                  body="Congrats!\nYou won the following lunch: %s (worth %s shekels)\nfrom: %s\nLunch will be ordered for you tomorrow (%s IS PAYING !! WOHO)\nYours truly,\nLunch Roulette" % (game["food"]["name"], game["food"]["price"],game["food"]["rest_name"], looser_user["user_name"]))
        # send to looser
        send_mail(looser_user["email"], winner_user["email"], subject = "BOOHOO %s, You lost %s shekels in Lunch Roulette " % (looser_user["user_name"],  game["food"]["price"]),
                  body="We're sorry to inform you that you owe your co-worker %s lunch tomorrow!\nNever give up hope, maybe you will eat for free tomorrow :)\nYours truly,\nLunch Roulette" % winner_user["user_name"])
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
        
        
