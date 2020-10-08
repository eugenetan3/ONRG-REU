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


#Notes from brian
#Use unofficial api to retrieve readable html: https://www.socialbakers.com/statistics/twitter/profiles/entertainment/online-show/page-2?do=platformList-renderAjax&json=
#requests.get(url) with given url will return json with parameters error and content, we want content but also to check error
#when we take in the json to get just the html string portion we can do html_page = page[content].strip()
#with the parsed json, we now have a html string with removed whitespaces
#with the html_page which is the page content we can now do tree = html.fromstring(html_page)


#!!!!Requests.cookies: https://requests.readthedocs.io/en/master/user/quickstart/#cookies
#Send our own cookies (send knownUser cookie ; other one is not required???) to the socialbakers server
#cookies =  {
#  "knownUser": "%7B%22leadFormSent%22%3Atrue%7D"
#}
#cookies = dict(knownUser="%7B%22leadFormSent%22%3Atrue%7D")
#
#page = requests.get(url, cookies=cookies)

def text(html_content):
    return html_content.text_content().replace(u'\xa0', '').replace('\t', '').replace('\n', '').encode("utf8")

def crawl_social():
    url = 'https://www.socialbakers.com/statistics/twitter/profiles/entertainment/online-show/page-1-5'
    with open('sb_crawl', 'w') as fp:
        #try:
            print('getting html content for url: %s' % url)
            cookies = dict(knownUser="%7B%22leadFormSent%22%3Atrue%7D")
            page = requests.get(url, cookies=cookies)
            
            #print(page.content)
            print(page.cookies)
            #tree = html.fromstring(page.text)
            tree = html.fromstring(page.content)
            table = tree.xpath('//table[@class="brand-table-list"]')[0]
            print(len(table))
            data = [[text(td) for td in tr.xpath('td')] for tr in table.xpath('//tr')] #this line has issues
            ids = table.xpath('//a[@class="acc-placeholder-img"]')
            #print(data) 
            name_id = {}

            for uid in ids:
                name_id[uid.attrib['href'].split('/')[-1].split('-')[1]] = uid.attrib['href'].split('/')[-1].split('-')[0]
            for row in data:
                #print(row)
                followings = None
                followers = None
                name = None
                uid = None
                user_country = None

                if len(row) == 4: 

    
                    '''obtaining name and id'''
                    name = row[1].split()[-1][2:-1]

                    name = name.decode("utf-8")

                    uid = name_id[name.lower()]

                    '''Obtaining user country'''
                    status_code = 0
                    while status_code != 200:
                        new_url = 'http://www.socialbakers.com/statistics/twitter/profiles/detail/' + uid + '-' + name
                        while True:
                            try:
                                print("hnere")
                                new_page = requests.get(new_url)
                                break
                            except Exception:
                                logging.info('sleeping for 5 seconds...')
                                time.sleep(5)
                                continue
                            #print("hnere")
                        status_code = new_page.status_code
                        if status_code != 200:
                            logging.error(status_code)
                            delay = np.random.rand() * 5
                            time.sleep(delay)
                    new_tree = html.fromstring(new_page.text)
                    tag_list = new_tree.xpath('//div[@class="account-tag-list"]')
                    tags = tag_list[0].text_content().split()
                    for tag in tags:
                        if 'GLOBAL' in tags:
                            user_country = 'GLOBAL'
                        elif len(tag) == 2:
                            user_country = tag
                        '''obtaining number of followers and friends'''
                    try:
                        followings = int(row[2][10:])
                    except ValueError:
                        try:
                            followings = int(row[2][20:])
                        except Exception:
                            print('error occured for: %s' % row)
                    try:
                        followers = int(row[3][9:])
                    except ValueError:
                        try:
                            followers = int(row[3][18:])
                        except Exception:
                            print('error occured for: %s' % row)
    
                    '''writing to file'''
                print('followings:')    #ADDED BY: ROBERT MACY (testing)
                print(followings)   #ADDED BY: ROBERT MACY (testing)
                print('followers:')    #ADDED BY: ROBERT MACY (testing)
                print(followers)    #ADDED BY: ROBERT MACY (testing)
                print('name:')    #ADDED BY: ROBERT MACY (testing)
                print(name)    #ADDED BY: ROBERT MACY (testing)
                print('user_country:')    #ADDED BY: ROBERT MACY (testing)
                print(user_country)    #ADDED BY: ROBERT MACY (testing)
                if (followings is not None) and (followers is not None) and (name is not None) and (user_country is not None):
                    fp.write(uid + '\t' + str(name) + '\t' + str(followings) + '\t' + str(followers) + '\t' + str(user_country) + '\n')
    
                    '''delay in order not to get blacklisted'''
                delay = np.random.rand()
        #except Exception:    # ADDED BY: ROBERT MACY
        #    print('error occured for a url, sleeping for 10 seconds...') # ADDED BY: ROBERT MACY
        #    delay = np.random.rand() * 10 # ADDED BY: ROBERT MACY

if __name__ == '__main__':
    crawl_social()