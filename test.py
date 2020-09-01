from pymongo import MongoClient
import mysql.connector
from lxml import html
import numpy as np
import traceback
from re import *
import operator
import requests
import MySQLdb
import twython
import twython
import logging
import codecs
import json
import time
import os
import re    
date = time.strftime("%Y%m%d")
date = "20200814"
user_dict = {}
dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')
cursor = dbm.cursor()

command = "SELECT DISTINCT user_id,lang,COUNT(tweet_id) FROM Elite_Weekly.tweet_%s GROUP BY user_id,lang;" % date
print (command)
cursor.execute(command)
results = cursor.fetchall()
for i in range(len(results)):
    results[i] = re.sub(r'\(u\'([0-9]*)\', u\'([a-z]*)\', ([0-9]*)\)', r'\g<1> \g<2> \g<3>', str(results[i]))
    #print(results[i]) #parse out the pieces needed, for instance results[i][2] has 508) with a trailing parenthesis
    
    results[i] = results[i].split()
    #print(results[i])
    #print(results[i][0])

    wow = results[i][0]
    templen = len(wow)-2
    wow = wow[2:templen]
    results[i][0] = wowdd
    
    languages = results[i][1]
    templen2 = len(languages)-2
    languages = languages[1:templen2]
    results[i][1] = languages

    counter = results[i][2]
    templen3 = len(counter)-1
    counter = counter[0:templen3]
    results[i][2] = counter

    print(results[i][0])
    print(results[i][1])
    print(results[i][2])
    results[i][2] = int(results[i][2])
    print(results[i][2])
    if(results[i][0] not in user_dict.keys()):
        user_dict[results[i][0]] = [results[i][1], results[i][2]]
        print(user_dict[results[i][0]])
    elif(user_dict[results[i][0]][1] < results[i][2]):
        user_dict[results[i][0]] = [results[i][1], results[i][2]]
        print(user_dict[results[i][0]])


command = "SELECT DISTINCT user_id,COUNT(tweet_id) FROM Elite_Weekly.tweet_%s GROUP BY user_id;" %date
print (command)
cursor.execute(command)
user_tweet_counts = cursor.fetchall()
for i in range(len(user_tweet_counts)):
    user_tweet_counts[i] = re.sub(r'\(u\'([0-9]*)\', ([0-9]*)\)', r'\g<1> \g<2>', str(user_tweet_counts[i]))
    user_tweet_counts[i] = user_tweet_counts[i].split()

    first_param = user_tweet_counts[i][0]
    length = len(first_param)-2
    first_param = first_param[2:length]
    user_tweet_counts[i][0] = first_param

    #print(user_tweet_counts[i][0])

    second_param = user_tweet_counts[i][1]
    length = len(second_param)-1
    second_param = second_param[0:length]
    user_tweet_counts[i][1] = second_param

    user_tweet_counts[i][1] = int(user_tweet_counts[i][1])
    user_dict[user_tweet_counts[i][0]][1] = float(user_dict[user_tweet_counts[i][0]][1])/float(user_tweet_counts[i][1])

language_file = 'top12k_languages_' + date
l_f = open(language_file, 'w')
for user in user_dict.keys():
    for i in range(len(user_dict[user])):
        user_dict[user][i] = str(user_dict[user][i])
    l_f.write(str(user) + ',' + ','.join(user_dict[user]) + '\n')
l_f.close()
print("done")