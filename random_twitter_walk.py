import twython
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

base_path='/home/robert/LMA/data/top_accounts_%s/' % current_date

def random_twitter_walk(random_walk_file, token_file, date, seed_id):
    all_tokens = []
    tokens = open(token_file) 
    for line in tokens:
        all_tokens.append(line.strip().split()[:])
    last_timeout = time.time()
    token_counter = 1
    print 'random walk started'
    user_counter = 0 #GOOD TO HERE
    random_walk_ids = []
    step = seed_id
    while(len(random_walk_ids) < 10000):
        print 'Profiles of %d users are walked so far' % user_counter
	user_counter += 1
	have_path = False
	back_steps = 0
	while(not have_path):
	    friend_ids = []
	    next_cursor = -1
            while next_cursor:
                try:
        	    consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
                    twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
        	    search = twitter.get_friends_ids(id=step, cursor=next_cursor)
        	    friend_ids.extend(search['ids'])
        	    next_cursor = search["next_cursor"]
        	except twython.TwythonRateLimitError, e:
        	    print "token number is %d" % (token_counter % len(all_tokens))
                    token_counter += 1
        	except Exception, e:
        	    print e
                    break
        	if token_counter % len(all_tokens) == 0:
        	    sleep_amount = 900
                    last_timeout = time.time()
                    print "Tokens are exhausted, sleeping for %f minutes" % (sleep_amount / 60.0)
        	    time.sleep(sleep_amount)
        	    token_counter += 1
	    if len(friend_ids):
	        print 'User has friends, taking next step from user %s ...' % step
	        rInt = random.randint(0,len(friend_ids)-1)
                step = friend_ids[rInt]
		print 'new step is %s' % step
		random_walk_ids.append(step)
                have_path = True
            else:
		print 'User %s has no friends, takings step back to last user...' % step
                back_steps += 1
		if (back_steps > len(random_walk_ids)):
	            step = seed_id
		    have_path = True
	        else:
                    step = random_walk_ids[-back_steps]

    walk_file = open(random_walk_file, "w")
    print 'Writing results of random walk to %s' % random_walk_file
    for user_id in random_walk_ids:
	followers_count = None
	screen_name = None
	lang = None
        try:
	    consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
            twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
	    search = twitter.show_user(id=user_id)
            try:
                followers_count = search['followers_count']
            except Exception, e:
	        print 'error occured for: %s' % user_id
	    try:
	        screen_name = search['screen_name']
	    except Exception, e:
	        print 'error occured for: %s' % user_id
	    try:
	        lang = search['lang']
	    except Exception, e:
	        print 'error occured for: %s' % lang
	    if ((user_id is not None) and (followers_count is not None) and (screen_name is not None) and (lang is not None)):
                walk_file.write('%s,%s,%s,%s\n' % (str(user_id), str(screen_name), str(followers_count), str(lang)))
        except twython.TwythonRateLimitError, e:
            print "token number is %d" % (token_counter % len(all_tokens))
	    token_counter += 1
        except Exception, e:
	    print e
	    time.sleep(5)
	if token_counter % len(all_tokens) == 0:
	    sleep_amount = 900
            last_timeout = time.time()
            print "Tokens are exhausted, sleeping for %f minutes" % (sleep_amount / 60.0)
	    time.sleep(sleep_amount)
	    token_counter += 1

	
    walk_file.close()
    tokens.close()
    print 'random walk successfully finished'

random_twitter_walk(base_path + "random_walk_users","tokens_LMA1",current_date,'21447363') # Using katyperry as default seed.
