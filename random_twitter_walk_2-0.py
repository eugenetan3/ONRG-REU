import twython
from twython import Twython
from lxml import html
import numpy as np
import traceback
from re import *
import operator
import requests
import logging
import codecs
import json
import time
import os
import random

current_date = time.strftime("%Y%m%d")

base_path='/home/eugenet/WorkingDir/random_walk_data/random_walk_%s_' % current_date

def random_twitter_walk(random_walk_file, token_file, date, seed_id):
    all_tokens = []
    tokens = open(token_file)
    for line in tokens:
        all_tokens.append(line.strip().split()[:])

    for i in all_tokens:
        print(i)

    last_timeout = time.time()
    token_counter = 0


    user_count = 0
    random_walk_ids = []
    step = seed_id
    while (len(random_walk_ids) < 100):
        print ('Current number of profiles walked so far: %d' % user_count)
        user_count = user_count + 1
        have_path = False
        back_step = 0

        while (not have_path):
            friend_ids = []
            next_cursor = -1

            while (next_cursor):
                try:
                    consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
                    twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
                    search = twitter.get_friends_ids(id = step, cursor = next_cursor)
                    search2 = twitter.get_followers_ids(id = step, cursor = next_cursor)
                    #print(search2)
                    friend_ids.extend(search['ids'])
                    friend_ids.extend(search2['ids'])
                    print("How many people: " + len(friend_ids))
                    next_cursor = search2["next_cursor"]
                except twython.TwythonRateLimitError:
                    print ("Token number is %d" % (token_counter % len(all_tokens)))
                    token_counter = token_counter + 1

                except Exception:
                    #print (Exception)
                    break
                
                if token_counter % len(all_tokens) == 0:
                    sleep_amount = 5
                    last_timeout = time.time()
                    print("Tokens are exhausted, sleeping for %f minutes!" % (sleep_amount / 60.0))
                    time.sleep(sleep_amount)
                    token_counter = token_counter + 1
 
            if len(friend_ids):
                print("User has friends, taking next from step from user %s..." % step)
                rInt = random.randint(0, len(friend_ids)-1)
                step = friend_ids[rInt]
                print("New step is %s" % step)
                random_walk_ids.append(step)
                have_path = True
            else:
                print("User %s has no friends, taking step back to the last user..." % step)
                back_step = back_step + 1
                if (back_step > len(random_walk_ids)):
                    step = seed_id
                    have_path = True
                else:
                    step = random_walk_ids[-back_step]
    print(len(friend_ids))        
    walk_file = open(base_path + seed_id, "w")
    print('Writing results of random walk to %s' % random_walk_file)
    for user_id in random_walk_ids:
        followers_count = None
        screen_name = None
        lang = None
        
        try:
            consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
            twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
            search = twitter.show_user(id=user_id)
        except twython.TwythonRateLimitError:
            print("Token number is %d" % (token_counter % len(all_tokens)))
            token_counter = token_counter + 1
        try:
            followers_count = search['followers_count']
        except Exception:
            print("Error occurred for: %s" % user_id)
        
        try:
            screen_name = search['screen_name']
        except Exception:
            print("Error occurred for: %s" % user_id)
        
        try:
            lang = search['lang']
        except Exception:
            print("Error occurred for: %s" % lang)
 
        if ((user_id is not None) and (followers_count is not None) and (screen_name is not None)):
            walk_file.write('%s,%s,%s\n' % (str(user_id), str(screen_name), str(followers_count)))
        if token_counter & len(all_tokens) == 0:
            sleep_amount = 5
            last_timeout = time.time()
            print("All tokens are exhausted, sleeping for %f minutes" % (sleep_amount / 60.0))
            time.sleep(sleep_amount)
            token_counter = token_counter + 1
    walk_file.close()
    tokens.close()
    print("Random walk successfully finished")

if __name__ == '__main__':
    #random_twitter_walk("/home/eugenet/WorkingDir/data/top_accounts_20200719/random_walk_users", "token.txt", current_date, "1280557030562869248")
    #random_twitter_walk(base_path + "106387406", "token.txt", current_date, "106387406")
    random_twitter_walk(base_path + "358996059", "token.txt", current_date, "358996059")
    #  SEEDS ARE ELITES FOR RANDOM