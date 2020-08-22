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
import logging
import codecs
import json
import time
import os
import re    


categories = {'brands': {'accommodation': [],
                         'airlines': [],
                         'alcohol': ['beer', 'spirits', 'wine'],
                         'auto': [],
                         'beauty': ['hygiene'],
                         'beverages': ['coffee-tea', 'soft-drink', 'water'],
                         'conglomerate': [],
                         'ecommerce': ['e-shop', 'travel-booking'],
                         'electronics': ['appliance', 'audio', 'camera', 'computer', 'gaming-console', 'phone'],
                         'fmcg-corporate': [],
                         'fmcg-food': ['baby-food', 'confectionery', 'dairy'],
                         'fashion': ['accessories', 'clothing', 'jewelry'],
                         'finance': ['bank', 'insurance', 'payment'],
                         'gambling': [],
                         'healthcare': [],
                         'home-living': ['children', 'furniture', 'home-maintenance', 'toys-games', 'utensils'],
                         'household-goods': ['chemicals', 'pets', 'stationery'],
                         'industrial': [],
                         'retail': [],
                         'retail-food': [],
                         'services': ['agency', 'housing', 'mail-shipping', 'transportation', 'wellness'],
                         'software': ['game-developer'],
                         'sporting-goods': [],
                         'telecom': [],
                         'travel': []
                         },
              'celebrities': ['actor',
                              'artist',
                              'broadcast-star',
                              'disc-jockey',
                              'fashion-star',
                              'musician',
                              'singer',
                              'sport-star',
                              'writer'
                              ],
              'community': ['auto-interest',
                            'culture',
                            'erotic',
                            'film',
                            'fun',
                            'hobbies',
                            'life-style',
                            'music',
                            'personal',
                            'political',
                            'religion',
                            'sport-interest',
                            'wikipedia'
                            ],
              'entertainment': ['apps',
                                'books',
                                'broadcast-show',
                                'computer-game',
                                'event',
                                'fictional-character',
                                'film-industry',
                                'music-industry',
                                'online-show'
                                ],
              'media': ['blog',
                        'media-house',
                        'news',
                        'online-media',
                        'printed-media',
                        'radio-media',
                        'social-media',
                        'tv-channels',
                        'web-portal'
                        ],
              'place': ['airport',
                        'city',
                        'country',
                        'cultural-center',
                        'medical-center',
                        'night-life',
                        'restaurant-cafe'
                        ],
              'society': ['csr',
                          'conference',
                          'education',
                          'governmental',
                          'ngo',
                          'politics',
                          'professional-association'
                          ],
              'sport': ['sport-club',
                        'sport-event',
                        'sport-organization']
              }

base_url = 'http://www.socialbakers.com/statistics/twitter/profiles/'
first_page = ['1', '6', '11', '16', '21', '26', '31', '36', '41', '46', '51', '56', '61', '66', '71', '76', '81', '86',
             '91', '96']
last_page = ['5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '60', '65', '70', '75', '80', '85', '90',
             '95', '100']


def initialize():
    print "It is recommended that this program runs with GNU screen!"
    # try:
    #     raw_input("Press any key to continue...")
    # except SyntaxError:
    #     pass
    date = time.strftime("%Y%m%d")
    # date = '20170404'
    base_path = './data/top_accounts_%s/' % date
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    for super_cat in categories.keys():
        if not os.path.exists(base_path + super_cat):
            os.mkdir(base_path + super_cat)

    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')

    cursor = dbm.cursor()
    data_base_creation_query = "CREATE DATABASE IF NOT EXISTS Elite_Weekly;"
    cursor.execute(data_base_creation_query)
    cursor.close()
    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')
    return dbm, date, base_path


def file_diff(infile1, infile2, outfile, index1=-1, sep1='', index2=-1, sep2=''):
    """
    :param infile1: string that identifies first file path and name.
    :param infile2: string that identifies first file path and name.
    :param outfile: string that identifies the output file name and path.
    :param index1: integer that identifies the column number of first file that is considered for calculating the difference. If there is only one column index is -1.
    :param sep1: string that identifies the separator of columns. Could be tab, comma, etc. If there is only one column sep1 is empty.
    :param index2: integer that identifies the column number of first file that is considered for calculating the difference. If there is only one column index is -1.
    :param sep2: string that identifies the separator of columns. Could be tab, comma, etc. If there is only one column sep1 is empty.
    :return: a file that contains the difference of two specific columns of two files. Note that order of infiles matters! the content of outfile is file1 - file2
             and the columns in outfile is similar to infile1.
    """
    set1 = set()
    outf = open(outfile, 'w')
    with open(infile2) as top:
        for line in top:
            if sep2 != '':
                set1.add(str(line.strip().split(sep2)[index2]))
            else:
                set1.add(str(line.strip()))

    with open(infile1) as fp1:
        for line in fp1:
            if sep1 != '':
                uid = str(line.strip().split(sep1)[index1])
                if uid not in set1:
                    outf.write(line)
            else:
                uid = str(line.strip())
                if uid not in set1:
                    outf.write(line)
    outf.close()


def unix_sort(source_file, column_number, dest_file, asc=True, separator=''):
    """
    This function takes a file as an input and sorts it based on one of the columns using unix command sort. The
    output of this function is a sorted version of the input file. column number starts from 1.
    """
    if asc:
        command = 'sort -n -k' + str(
            column_number) + " -r  --field-separator='" + separator + "' " + source_file + ' > ' + dest_file
        print command
        os.system(command)
    else:
        command = 'sort -n -k' + str(
            column_number) + " --field-separator='" + separator + "' " + source_file + ' > ' + dest_file
        print command
        os.system(command)


def text(html_content):
    return html_content.text_content().replace(u'\xa0', '').replace('\t', '').replace('\n', '').encode("utf8")


def create_urls():
    """
    This function creates valid urls that are used to crawl socialbakers.com website.
    The  category information is provided in url_info.py file. The output of this function is a list of urls.
    """
    urls = []
    for category, subcategory in categories.items():
        for i, j in zip(first_page, last_page):
            urls.append(base_url + category + '/page-' + i + '-' + j)
        if isinstance(subcategory, dict):
            for sub, sub_list in subcategory.items():
                for i, j in zip(first_page, last_page):
                    urls.append(base_url + category + '/' + sub + '/page-' + i + '-' + j)
                if len(sub_list):
                    for subsub in sub_list:
                        for i, j in zip(first_page, last_page):
                            url = base_url + category + '/' + sub + '/' + subsub + '/page-' + i + '-' + j
                            urls.append(url)
                else:
                    for i, j in zip(first_page, last_page):
                        url = base_url + category + '/' + sub + '/page-' + i + '-' + j
                        urls.append(url)
        else:
            for sub in subcategory:
                for i, j in zip(first_page, last_page):
                    url = base_url + category + '/' + sub + '/page-' + i + '-' + j
                    urls.append(url)
    return urls


def crawl_social(urls, path):
    """
    This function takes a list of socialbaker urls and crawls them to finds users and some relevant information about
    them including: number of followers, number of friends, country, user id, and user name. The output of this function
    is a set of twenty files per category.
    """
    for url in urls:
        with open(path + url[56:].split('/')[0] + '/' + url[56:].replace('/', '_'), 'w') as fp:
            try:
                print 'getting html content for url: %s' % url
                page = requests.get(url)
                tree = html.fromstring(page.text)
                table = tree.xpath('//table[@class="brand-table-list"]')[0]
                data = [[text(td) for td in tr.xpath('td')] for tr in table.xpath('//tr')]
                ids = table.xpath('//a[@class="acc-placeholder-img"]')
                name_id = {}
                for uid in ids:
                    name_id[uid.attrib['href'].split('/')[-1].split('-')[1]] = uid.attrib['href'].split('/')[-1].split('-')[
                        0]
                for row in data:
                    followings = None
                    followers = None
                    name = None
                    uid = None
                    user_country = None
                    if len(row) == 4: # ADDED BY: ROBERT MACY (Social bakers' data reformated so this text object only has 4 parts now.)
                   # if len(row) == 5: # COMMENTED BY: ROBERT MACY (Replaced by above line).
    
                        '''obtaining name and id'''
                        name = row[1].split()[-1][2:-1]
                        print name
                        uid = name_id[name.lower()]
    
                        '''Obtaining user country'''
                        status_code = 0
                        while status_code != 200:
                            new_url = 'http://www.socialbakers.com/statistics/twitter/profiles/detail/' + uid + '-' + name
                            while True:
                                try:
                                    new_page = requests.get(new_url)
                                    break
                                except Exception, e:
                                    logging.error(e)
                                    logging.info('sleeping for 5 seconds...')
                                    time.sleep(5)
                                    continue
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
                            except Exception, e:
                                print 'error occured for: %s' % row
                        try:
                            followers = int(row[3][9:])
                        except ValueError:
                            try:
                                followers = int(row[3][18:])
                            except Exception, e:
                                print 'error occured for: %s' % row
    
                    '''writing to file'''
                    print 'followings:'    #ADDED BY: ROBERT MACY (testing)
                    print followings    #ADDED BY: ROBERT MACY (testing)
                    print 'followers:'    #ADDED BY: ROBERT MACY (testing)
                    print followers    #ADDED BY: ROBERT MACY (testing)
                    print 'name:'    #ADDED BY: ROBERT MACY (testing)
                    print name    #ADDED BY: ROBERT MACY (testing)
                    print 'user_country:'    #ADDED BY: ROBERT MACY (testing)
                    print user_country    #ADDED BY: ROBERT MACY (testing)
                    if (followings is not None) and (followers is not None) and (name is not None) and (
                        user_country is not None):
                        fp.write(uid + '\t' + str(name) + '\t' + str(followings) + '\t' + str(followers) + '\t' + str(
                            user_country) + '\n')
    
                    '''delay in order not to get blacklisted'''
                    delay = np.random.rand()
            except Exception, e:    # ADDED BY: ROBERT MACY
                print 'error occured for a url, sleeping for 10 seconds...' # ADDED BY: ROBERT MACY
                delay = np.random.rand() * 10 # ADDED BY: ROBERT MACY

def create_directories(path):
    """
    When social baker is crawled, for each page of each category one file is generated so we would have
    (20 times number of categories) files. These files are stored in base_path. this function crates one directory
    for each category.
    """
    files = os.listdir(path)
    for f in files:
        if os.path.isdir(path + '/' + f):
            pass
        else:
            if len(f.split('_')) == 3:
                folder_name = f.split('_')[-2]
                if not os.path.exists(path + '/' + folder_name):
                    os.mkdir(path + '/' + folder_name)
                if not os.path.exists(path + '/all'):
                    os.mkdir(path + '/all')
            if len(f.split('_')) == 4:
                parent_folder_name = f.split('_')[-3]
                folder_name = f.split('_')[-2]
                if not os.path.exists(path + '/all'):
                    os.mkdir(path + '/all')
                if not os.path.exists(path + '/' + parent_folder_name):
                    os.mkdir(path + '/' + parent_folder_name)
                if not os.path.exists(path + '/' + parent_folder_name + '/all'):
                    os.mkdir(path + '/' + parent_folder_name + '/all')
                if not os.path.exists(path + '/' + parent_folder_name + '/' + folder_name):
                    os.mkdir(path + '/' + parent_folder_name + '/' + folder_name)


def organize_files(path):
    """
    When social baker is crawled, for each page of each category one file is generated so we would have
    (20 times number of categories) files. This function moves relevant files to their corresponding directory.
    """
    files = os.listdir(path)
    for f in files:
        name_list = f.split('_')
        if os.path.isdir(path + '/' + f):
            pass
        else:
            if len(name_list) == 2:
                os.rename(path + '/' + f, path + '/all/' + f)
            if len(name_list) == 3:
                flag = False
                folder_check = os.listdir(path + '/' + name_list[-2] + '/')
                for fifo in folder_check:
                    if os.path.isdir(path + '/' + name_list[-2] + '/' + fifo):
                        flag = True
                if len(folder_check) and flag:
                    os.rename(path + '/' + f, path + '/' + name_list[-2] + '/all/' + f)
                else:
                    os.rename(path + '/' + f, path + '/' + name_list[-2] + '/' + f)
            if len(name_list) == 4:
                os.rename(path + '/' + f, path + '/' + name_list[-3] + '/' + name_list[-2] + '/' + f)


def join(path):
    """
    This function takes a path as input and goes into all directories and sub-directories recursively
    and concatenates the contents of the files inside all directories and sub-directories together and
    creates a joined file of all content in each directory (or sub-directory)
    """
    accounts = []
    files = os.listdir(path)
    for f in files:
        if os.path.isdir(path + '/' + f):
            join(path + '/' + f)
        else:
            with open(path + '/' + f) as fp:
                for line in fp:
                    accounts.append(line)

    if len(accounts):
        f_out = open(path + '/' + 'joined', 'w')
        for item in accounts:
            f_out.write(item)
        f_out.close()


def joined_join(path):
    """
    This function gets a path as an input and goes into all directories and sub directories recursively
    and joins all joined files that were created using join() function. It returns a set of all accounts.
    """
    global all_accounts
    files = os.listdir(path)
    for f in files:
        if os.path.isdir(path + '/' + f):
            joined_join(path + '/' + f)
        elif f == 'joined':
            joined_accounts = open(path + '/' + f)
            for line in joined_accounts:
                all_accounts.add(line)
            joined_accounts.close()
    return all_accounts


def find_social_tags_from_file(path, date, dbm):
    """
    This function creates a table called social_baker that has all information for all users
    """
    table_creation_query = "CREATE TABLE IF NOT EXISTS Elite_Weekly.social_baker (id BIGINT NOT NULL, name VARCHAR(45) NULL, country VARCHAR(45) NULL, social_tags VARCHAR(100) NULL, PRIMARY KEY (id)) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;"
    cursor = dbm.cursor()
    cursor.execute(table_creation_query)

    files = os.listdir(path)
    for f in files:
        if os.path.isdir(path + '/' + f):
            find_social_tags_from_file(path + '/' + f, date, dbm)
        if os.path.isfile(path + '/' + f) and f != 'all' and len(f.split('-')) > 2:
            tags = f.split('_')[:-1]
            tags = '|'.join(tags)
            with open(path + '/' + f) as fp:
                for line in fp:
                    new_line = line.strip().split('\t') + [tags]
                    insert_query = "INSERT IGNORE INTO Elite_Weekly.social_baker VALUES (%d, '%s', '%s', '%s');" % (
                    long(new_line[0]), new_line[1], new_line[4], new_line[5])
                    cursor.execute(insert_query)


def find_friends(id_file, token_file, date, dbm):
    cursor = dbm.cursor()
    create_table_query = "CREATE TABLE IF NOT EXISTS Elite_Weekly.fofr_%s (follower_id BIGINT NOT NULL default 0, friend_id BIGINT NOT NULL default 0) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;" % date
    cursor.execute(create_table_query)
    user_list = set()
    with open(id_file) as ids:
        for line in ids:
            user_list.add(line.strip())

    all_tokens = []
    tokens = open(token_file)
    for line in tokens:
        all_tokens.append(line.strip().split()[:])
    last_timeout = time.time()
    token_counter = 1
    print 'finding friends started'
    user_counter = 0
    for user in user_list:
        print "Friends of %d users are found so far" % user_counter
        user_counter += 1
        friends_ids = []
        next_cursor = -1
        while next_cursor:
            try:
                consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
                twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
                search = twitter.get_friends_ids(id=user, cursor=next_cursor)
                friends_ids.extend(search['ids'])
                next_cursor = search["next_cursor"]
            except twython.TwythonRateLimitError, e:
                print "token number is %d" % (token_counter % len(all_tokens))
                token_counter += 1
            except Exception, e:
                print e
                break

            if token_counter % len(all_tokens) == 0:
                # sleep_amount = 900 
                sleep_amount = 900
                # if sleep_amount < 0:
                    # sleep_amount = 0
                last_timeout = time.time()
                print "Tokens are exhausted, sleeping for %f minutes" % (sleep_amount / 60.0)
                time.sleep(sleep_amount)
                token_counter += 1

        if len(friends_ids):
            print 'Inserting into database for user %s ...' % user
            for fr_id in friends_ids:
                q = "INSERT INTO Elite_Weekly.fofr_%s (follower_id, friend_id) VALUES (%s, %s);" % (date, user, fr_id)
                cursor.execute(q.encode('utf-8'))
        dbm.commit()

    cursor.close()
    dbm.close()
    tokens.close()
    print 'finding friends successfully finished'


def followers_counter(id_file, token_file, out_file):
    outf = open(out_file, 'w')
    user_list = set()
    with open(id_file) as ids:
        for line in ids:
            user_list.add(line.strip())

    all_tokens = []
    tokens = open(token_file)
    for line in tokens:
        all_tokens.append(line.strip().split()[:])
    last_timeout = time.time()
    token_counter = 1
    print 'Counting followers staretd....'
    user_counter = 0
    for user in user_list:
        print "Number of followers of %d users are found so far" % user_counter
        user_counter += 1
        num_followers = 0
        while True:
            try:
                consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
                twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
                search = twitter.show_user(user_id=user)
                num_followers = search['followers_count']
                break
            except twython.TwythonRateLimitError, e:
                print "token number is %d" % (token_counter % len(all_tokens))
                token_counter += 1
            except Exception, e:
                print e
                break

            if token_counter % len(all_tokens) == 0:
                sleep_amount = 900 
                # last_timeout = time.time()
                print "Tokens are exhausted, sleeping for %f minutes" % (sleep_amount / 60.0)
                time.sleep(sleep_amount)
                token_counter += 1

        outf.write(str(user) + ',' + str(num_followers) + '\n')

    tokens.close()
    outf.close()
    print 'Counting followers finished.'


def friend_finder(id_file, token_file, date, dbm):
    cursor = dbm.cursor()
    user_list = set()
    with open(id_file) as ids:
        for line in ids:
            user_list.add(line.strip())

    all_tokens = []
    tokens = open(token_file)
    for line in tokens:
        all_tokens.append(line.strip().split()[:])
    last_timeout = time.time()
    token_counter = 1
    print 'Finding friends of most followed friends started...'
    user_counter = 0
    for user in user_list:
        print "Friends of %d users are found so far" % user_counter
        user_counter += 1
        friends_ids = []
        next_cursor = -1
        while next_cursor:
            try:
                consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
                twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
                search = twitter.twython.get_friends_ids(id=user, cursor=next_cursor)
                friends_ids.extend(search['ids'])
                next_cursor = search["next_cursor"]
            except twython.TwythonRateLimitError, e:
                print "token number is %d" % (token_counter % len(all_tokens))
                token_counter += 1
            except Exception, e:
                print e
                break

            if token_counter % len(all_tokens) == 0:
                sleep_amount = 900
                if sleep_amount < 0:
                    sleep_amount = 0
                last_timeout = time.time()
                print "Tokens are exhausted, sleeping for %f minutes" % (sleep_amount / 60.0)
                time.sleep(sleep_amount)
                token_counter += 1

        if len(friends_ids):
            print 'Inserting into database for user %s ...' % user
        for fr_id in friends_ids:
            q = "INSERT INTO Elite_Weekly.fofr_%s (follower_id, friend_id) VALUES (%s, %s);" % (date, user, fr_id)
            cursor.execute(q.encode('utf-8'))
        dbm.commit()

    cursor.close()
    dbm.close()
    tokens.close()
    print 'Finding griends of most followed friends finished.'


def name_finder(id_file, token_file, outfile):
    main_friends = []
    all_tokens = []
    with open(token_file) as tokens:
        for line in tokens:
            all_tokens.append(line.strip().split()[:])
    with open(id_file) as fp:
        for line in fp:
            main_friends.append(line.strip())
    id_name_dict = {}
    token_counter = 1
    user_counter = 0
    for uid in main_friends:
        print "Name of %d users are found so far" % user_counter
        user_counter += 1
        while True:
            try:
                consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
                twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
                output = twitter.lookup_user(user_id=uid)
                name = output[0]['screen_name']
                id_name_dict[name] = uid
                break
            except twython.TwythonRateLimitError, e:
                print "token number is %d" % (token_counter % len(all_tokens))
                token_counter += 1
            except Exception, e:
                print e
                break
            if token_counter % len(all_tokens) == 0:
                sleep_amount = 900
                if sleep_amount < 0:
                    sleep_amount = 0
                last_timeout = time.time()
                print "Tokens are exhausted, sleeping for %f minutes" % (sleep_amount / 60.0)
                time.sleep(sleep_amount)
                token_counter += 1

    with open(outfile, 'w') as fp:
        for k, v in id_name_dict.items():
            fp.write(k + ',' + v + '\n')


def social_country_finder(id_name_file, not_found_file, found_file):
    """
    :param id_name_file: This file should be in the format of id,name
    :return: two files: one file called most_followed_friends_social that contains id,name,country,tag1|tag2|tag3
             and another file called most_followed_friends_error that contains user id and name of those accounts that
             are not found on socialbakers.com
    """
    urls = []
    not_found = open(not_found_file, 'w')
    base_url = 'http://www.socialbakers.com/statistics/twitter/profiles/detail/'
    with open(id_name_file) as fp:
        for line in fp:
            k = line.strip().split(',')[0]
            v = line.strip().split(',')[1]
            new_url = base_url + v + '-' + k
            urls.append(new_url)

    with open(found_file, 'w') as fp:
        for url in urls:
            print url
            '''Obtaining user tags'''
            new_page = requests.get(url)
            user_country = None
            new_tags = 'None,None'
            try: 
                if new_page.status_code == 200:
                    new_tree = html.fromstring(new_page.text)
                    tag_list = new_tree.xpath('//div[@class="account-tag-list"]')
                    tags = tag_list[0].text_content().split()

                    for tag in tags:
                        if 'GLOBAL' in tags:
                            user_country = 'GLOBAL'
                        elif len(tag) == 2:
                            user_country = tag
                    tag_set = set()
                    for item in tags:
                        tag_set.add(item)
                    try:
                        tag_set.remove('edit')
                        tag_set.remove('tags')
                        tag_set.remove(user_country)
                    except Exception, e:
                        print e
                    new_tags = '|'.join(list(tag_set))

                else:
                    name = url[63:].split('-')[1]
                    uid = url[63:].split('-')[0]
                    not_found.write(name + ',' + uid + '\n')

                name = url[63:].split('-')[1]
                uid = url[63:].split('-')[0]
                '''writing to file'''
                if user_country is not None:
                    fp.write(uid + ',' + name + ',' + user_country + ',' + new_tags + '\n')
            except:
                pass
    not_found.close()

def find_elite_most_followed_friends(friends_file_path, topxk_sourced_file, token_file_path):
    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')
    all_tokens = []
    tokens = open(token_file_path)
    for line in tokens:
        all_tokens.append(line.strip().split()[:])
    friends = open(friends_file_path, 'r')
    topxk_sourced = open(topxk_sourced_file, 'r')       
    friends_lines = friends.readlines()
    topxk_sourced_lines = topxk_sourced.readlines()
    topxk_sourced_atoms = {}
    for i in range(len(topxk_sourced_lines)):
        line = re.sub(r'^([0-9]*),\[([0-9]*), (\'[^\']*\')\]$', r'\g<1> \g<2> \g<3>', topxk_sourced_lines[i])
        line = line.split()
        topxk_sourced_atoms[line[0]] = [line[1], line[2]]
        topxk_sourced_lines[i] = line
        
    last_timeout = time.time()
    token_counter = 1
    run = 0
    mff_count = 0
    swap_counter = 0
    most_followed_friend = ['',0]
    for i in range(len(friends_lines)):
        friends_lines[i] = re.sub(r',', r' ', friends_lines[i])
        friends_lines[i] = friends_lines[i].split()
    friends_lines.sort(key = lambda elem: int(elem[1]), reverse=True)
    for i in range(len(friends_lines)):
        line = friends_lines[i]
        mff_count += 1
        if(line[0] in topxk_sourced_atoms.keys()):
            print '%s already in %s, ignoring...' % (str(line[0]), topxk_sourced_file)
            continue
        else:
            try:
                consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
                twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)
                search = twitter.show_user(user_id=line[0])
                num_followers = search['followers_count']
                print 'num_followers fonud for user %s' % str(line[0])
                if(int(num_followers) > most_followed_friend[1]):
                    most_followed_friend = [line[0], int(num_followers)]
                i = 0
                print 'int(num_followers): %d, topxk_sourced_lines[i][1]: %d' % (int(num_followers), int(topxk_sourced_lines[i][1]))
                while(int(num_followers) > int(topxk_sourced_lines[i][1])):
                    i += 1
                if(i > 0):
                    run = 0
                    topxk_sourced_lines.insert(i,[line[0], num_followers, '\'mff\''])
                    print 'replacement for user %s' % (str(line[0]))
                    topxk_sourced_lines.pop(0)
                    swap_counter += 1
                else:
                    run += 1
            except twython.TwythonRateLimitError, e:
                print "token number is %d" % (token_counter % len(all_tokens))
                token_counter += 1
            except Exception, e:
                print e
            if token_counter %  len(all_tokens) == 0:
                sleep_amount = 900
                last_timeout = time.time()
                print "Tokens are exhausted, sleeping for %f minutes" % (sleep_amount / 60.0)
                time.sleep(sleep_amount)
                token_counter += 1
        print 'run length: ' + str(run)
        print 'token counter: ' + str(token_counter) 
        print 'number of tokens: ' + str(len(all_tokens))
        print 'token counter mod number of tokens: ' + str(token_counter % len(all_tokens))
        if(run >= 100):
            print 'Breaking out of elite most followed friends search, %d lines checked' % mff_count
            break
    return topxk_sourced_lines

def generate_topxk_sourced_ranking_report(topxk_sourced_file, out_file):
    topxk_sourced = open(topxk_sourced_file,'r')
    out = open(out_file, 'w')
    topxk_sourced_lines = topxk_sourced.readlines()
    topxk_sourced_dict = {}
    topxk_sourced_list = []
    for line in topxk_sourced_lines:
        mod_line = line.replace('[', '').replace(']', '').split(',')
        mod_line[2] = mod_line[2].strip()
        topxk_sourced_list.append([mod_line[1], mod_line[0], mod_line[2]])
        if(mod_line[2] not in topxk_sourced_dict.keys()):
            topxk_sourced_dict[mod_line[2]] = []
            topxk_sourced_dict[mod_line[2]].append([mod_line[1], mod_line[0]])

        else:
            topxk_sourced_dict[mod_line[2]].append([mod_line[1], mod_line[0]])
    topxk_sourced_list.sort(key = lambda elem: int(elem[0]))
    topxk_sourced_list.reverse()

    
    # print topxk_sourced_dict[ "'RDS'"], '\n\n\n'

    for group in topxk_sourced_dict.keys():
        topxk_sourced_dict[group].sort(key = lambda elem: int(elem[0]))
        topxk_sourced_dict[group].reverse()
        out.write('############### ' + group + ' ###############\n')
        out.write('Category:\t\tLeastFollowed\t\tMost Followed\n')
        out.write('Elite Rank:\t\t' + str(topxk_sourced_list.index([topxk_sourced_dict[group][-1][0], topxk_sourced_dict[group][-1][1], group]) + 1) + '\t\t\t' + str(topxk_sourced_list.index([topxk_sourced_dict[group][0][0], topxk_sourced_dict[group][0][1], group]) + 1) + '\n')
        out.write('User ID:\t\t' + topxk_sourced_dict[group][-1][1] + '\t\t' + topxk_sourced_dict[group][0][1] + '\n')
        out.write('Number of followers:\t' + topxk_sourced_dict[group][-1][0] + '\t\t\t' + topxk_sourced_dict[group][0][0] + '\n')
    topxk_sourced.close()
    out.close()
    return out_file

def topxk_ranks(topxk_sourced_file, out_file):
    topxk_sourced = open(topxk_sourced_file, 'r')
    out = open(out_file, 'w')
    topxk_sourced_lines = topxk_sourced.readlines()
    topxk_dict = {}
    topxk_list = []
    for line in topxk_sourced_lines:
        mod_line = line.replace('[', '').replace(']', '').split(',')
        mod_line[2] = mod_line[2].strip()
        topxk_list.append([mod_line[1], mod_line[0], mod_line[2]])
        if(mod_line[2] not in topxk_dict.keys()):
            topxk_dict[mod_line[2]] = []
            topxk_dict[mod_line[2]].append([mod_line[1], mod_line[0]])

        else:
            topxk_dict[mod_line[2]].append([mod_line[1], mod_line[0]])
    topxk_list.sort(key=lambda elem: int(elem[0]))
    topxk_list.reverse()
    for group in topxk_dict.keys():
        topxk_dict[group].sort(key=lambda elem: int(elem[0]))
        topxk_dict[group].reverse()
        out.write('############### ' + group + ' ################\n')
        out.write('Category:\t\tLeast Followed\t\tMost Followed\n')
        out.write('Top 10k rank:\t\t' + str(topxk_list.index([topxk_dict[group][-1][0],topxk_dict[group][-1][1],group]) + 1) + '\t\t\t' + str(topxk_list.index([topxk_dict[group][0][0],topxk_dict[group][0][1],group]) + 1) + '\n')
        out.write('User ID:\t\t' + topxk_dict[group][-1][1] + '\t\t' + topxk_dict[group][0][1] + '\n')
        out.write('Number of followers:\t' + topxk_dict[group][-1][0] + '\t\t\t' + topxk_dict[group][0][0] + '\n')


if __name__ == '__main__':
    print "Initializing..."
    dbm, date, base_path = initialize()
#
    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')

#    print "call find_friend function to collect friends of top12k and store them into fofr table"
    #find_friends(base_path + 'top12k', 'token.txt', date, dbm)

#
    urls = create_urls()
    print "Crawling social_bakers started"
    crawl_social(urls, base_path) #MODIFIED BY : ROBERT MACY (don't need this for run on 20160804 because I collected SocialBaker Data on 20160801)
    
    print "Crawling social baker is finished"
    print "Organizing files..."
    for k in categories.keys():
        tmp_path = base_path + k
        create_directories(tmp_path)
    for k in categories.keys():
        tmp_path = base_path + k
        organize_files(tmp_path)
    join(base_path)
    all_accounts = set()
    all_accounts = joined_join(base_path)
    print "%d accounts were crawled from social baker" % len(all_accounts)
    print "write all account and their information into the file final_join"
    with open(base_path + 'final_join', 'w') as fp:
        for item in all_accounts:
            fp.write(','.join(item.strip().split('\t')) + '\n')

    print 'sort the file, final_join, based on number of followers.'
    unix_sort(base_path + 'final_join', 4, base_path + 'final_join.sorted', asc=True, separator=',')
    
    all_dict = {} #START PLACING ALL FOUND USERS IN DICTIONARY
    social_baker_dict = {}
    with open(base_path + 'final_join.sorted') as fp:
        for line in fp:
            line = line + ',social_baker' #ADDED BY: ROBERT MACY           
            uid = str(line.strip().split(',')[0])
            followers_count = line.strip().split(',')[3]
            friends_count = line.strip().split(',')[2]
            try:
                country = line.strip().split(',')[4]
                source = line.strip().split(',')[5] #ADDED BY: ROBERT MACY
            except Exception, e:
                print line
                exit()
            social_baker_dict[uid] = [followers_count, friends_count, country, source] # ADDED BY : [SAED REZAEI] MODIFIED BY : [ROBERT MACY]
            all_dict[uid] = [int(followers_count), source] # ADDED BY : [SAED REZAEI] MODIFIED BY : [ROBERT MACY]
    social_baker_users = set(social_baker_dict.keys())

    print 'finding top12k from random walk'
    local_conn = MongoClient()
    db = local_conn.MRW
    profile = db.profile

    print 'writing all random walk users in a file. (MRW)'
    walker_dict = {}
    with open(base_path + 'random_walk_users', 'w') as fp:
        try:
            profile_info = profile.find()
            for item in profile_info:
                num_followers = item['profile']['followers_count']
                screen_name = item['profile']['screen_name']
                user_id = str(item['profile']['id'])
                lang = item['profile']['lang']
                source = 'MRW' # ADDED BY : [ROBERT MACY]
                walker_dict[user_id] = [screen_name, num_followers, lang] # ADDED BY : [SAED REZAEI] MODIFIED BY : [ROBERT MACY]
                fp.write(str(user_id) + ',' + screen_name + ',' + str(num_followers) + ',' + lang + '\n') # ADDED BY : [SAED REZAEI] MODIFIED BY : [ROBERT MACY]
                if user_id in all_dict:
                    if all_dict[user_id][0] > int(num_followers):
                        all_dict[user_id][0] = int(num_followers) # ADDED BY : [SAED REZAEI] MODIFIED BY : [ROBERT MACY]
                        continue
                    all_dict[user_id][1] = 'social_baker_and_MRW' # ADDED BY : [ROBERT MACY]
                else:
                    all_dict[user_id] = [int(num_followers), source]
        except Exception, e:
            print e
    mrw_users = set(walker_dict.keys())

    db2 = local_conn.RDS
    profile2 = db2.profile

    print 'writing all random walk users in a file. (RDS)'
    rds_dict = {}
    with open(base_path + 'random_walk_users_rds', 'w') as fp:
        try:
            profile_info = profile2.find()
            for item in profile_info:
                num_followers = item['profile']['followers_count']
                screen_name = item['profile']['screen_name']
                user_id = str(item['profile']['id'])
                lang = item['profile']['lang']
                source = 'RDS' # ADDED BY : [ROBERT MACY]
                rds_dict[user_id] = [screen_name, num_followers, lang] # ADDED BY : [SAED REZAEI] MODIFIED BY : [ROBERT MACY]
                fp.write(str(user_id) + ',' + screen_name + ',' + str(num_followers) + ',' + lang + '\n') # ADDED BY : [SAED REZAEI] MODIFIED BY : [ROBERT MACY]
                if user_id in all_dict:
                    all_dict[user_id][1] = all_dict[user_id][1] + '_and_RDS' # ADDED BY : [ROBERT MACY]
                    if all_dict[user_id][0] > int(num_followers):
                        continue
                    all_dict[user_id][0] = int(num_followers)
                else:
                    all_dict[user_id] = [int(num_followers), source]
        except Exception, e:
            print e
    rds_users = set(rds_dict.keys())

    print 'get the union of social baker top12k and random walk top12k (MRW and RDS) and select top 12k of the union'
    sorted_all = sorted(all_dict.items(), key=operator.itemgetter(1))
    top12k = sorted_all[-12000:] 
    
    print 'store top12k_sourced of all three sets into file top12k_sourced'
    with open(base_path + 'top12k_sourced', 'w') as outfile:
        for item in top12k:
            outfile.write(str(item[0]) + ',' +  str(item[1]) + '\n')
#            item[1] = item[1][0] # ADDED BY : ROBERT MACY (convert top12k back to original formatting)
    top12k_set = set()
    print "store top12k of all three sets into file top12k"
    with open(base_path + 'top12k', 'w') as outfile:
        for item in top12k:
            top12k_set.add(item[0])
            outfile.write(str(item[0]) + '\n')

    dbm = mysql.connector.connect(host='localhost',
                                  user='eugenet',
                                  passwd='Eugenetan123',
                                  db='Elite_Weekly')

    print 'find social tags of social baker top12k from file and store them into social_baker table'
    find_social_tags_from_file(base_path, date, dbm)

    print 'find those users who are in union AND in the rw_top12k but not in sb_top12k'
    significant_others = top12k_set - social_baker_users
    print 'number of significants from rw who are not in sb is %d' % len(significant_others)

    with open(base_path + 'other_significants', 'w') as fp:
        for uid in significant_others:
            if uid in walker_dict:
                fp.write(str(walker_dict[uid][0]) + ',' + uid + '\n')
            elif uid in rds_dict:
                fp.write(str(rds_dict[uid][0]) + ',' + uid + '\n')

#    if len(significant_others):
#        print "call social_country_finder function to find social tags for rw significants."
#        print "if the information is not available in socialbaker, the tag rw|lang is stored"
#        social_country_finder(base_path + 'other_significants', base_path + 'other_significants_error',
#                              base_path + 'other_significants_social')
#        with open(base_path + 'other_significants_social', 'a') as outfile:
#                outfile.write(str(rds_dict[uid][0]) + ',' + uid + '\n') # ADDED BY : [SAED] MODIFIED BY : [ROBERT MACY] (changed fp to outfile)
# THE SECTION ABOVE IS CAUSING AN ERROR

    if len(significant_others):
        print "call social_country_finder function to find social tags for rw significants."
        print "if the information is not available in socialbaker, the tag rw|lang is stored"
        social_country_finder(base_path + 'other_significants', base_path + 'other_significants_error',
                              base_path + 'other_significants_social')
        with open(base_path + 'other_significants_social', 'a') as outfile:
            with open(base_path + 'other_significants_error') as fp:
                for line in fp:
                    uid = line.strip().split(',')[1]
                    if uid in walker_dict:
                        lang = walker_dict[uid][2]
                        name = walker_dict[uid][0]
                    elif uid in rds_dict:
                        lang = rds_dict[uid][2]
                        name = rds_dict[uid][0]
                    tag = 'rw|' + lang
                    country = 'rw'
                    outfile.write(uid + ',' + name + ',' + country + ',' + tag + '\n')

 #       print "move the other_significants_social into mysql_output folder where sql server has access to."
 #       os.rename(base_path + 'other_significants_social', '/home/rmacy/mysql_output/other_significants_social_' + date)

#chunk of code that uploads social information of the other_significants into table
 #       dbm = mysql.connector.connect(host='localhost',
#                                      user='rmacy',
#                                      passwd='RWM3cyrus',
#                                      db='Elite_Weekly')
#
        #print "store social information of other_significants into social_baker table"
       # social_query = "LOAD DATA LOCAL INFILE '/home/rmacy/mysql_output/other_significants_social_%s' INTO TABLE Elite_Weekly.social_baker FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';" % (date)
        ##social_query causes mariaDB to throw error (mariadb used command zzzz)
        #cursor = dbm.cursor()
        #cursor.execute(social_query) #command usually fails can technically ignore lines 1019 to 1032 if not inserting into table.
        #os.rename('/home/rmacy/mysql_output/other_significants_social_' + date, base_path + 'other_significants_social')

    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')

    print "call find_friend function to collect friends of top12k and store them into fofr table"
    find_friends(base_path + 'top12k', 'token.txt', date, dbm)

    print 'create db.txt file based on date'
    with open(base_path + 'db_%s.txt' % date, 'w') as db:
        db.write('host : localhost\n')
        db.write('database : Elite_Weekly\n')
        db.write('username: rmacy\n')
        db.write('password :RWM3cyrus\n')
        db.write('port : 3306\n')
        db.write('tables : users tweets urls')

    print "call Morgan's code to collect profile of finalized important users."
    os.system(
        'java -cp "./TW_Crawler/gson-2.8.6.jar:./TW_Crawler/twitter4j-core-3.0.5.jar:./TW_Crawler/mysql-connector-java-5.1.16-bin.jar:./TW_Crawler/." Collect %sdb_%s.txt token.txt %stop12k u' % (
        base_path, date, base_path))


    print 'all friends of top12k twitter accounts and their profile are stored in the db, now we start to find their most followed friends'
    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')
    print ("query to find number of followers of friends and to store the output in friends file.")
    
    #problematic
    query = "SELECT friend_id, count(distinct follower_id) FROM Elite_Weekly.fofr_%s group by friend_id INTO OUTFILE '/tmp/friends1_%s' fields terminated by ',' lines terminated by '\n';" % (date,date)
    #seems to not like this command ^^
    cursor = dbm.cursor()
    cursor.execute(query)

    #bash: cd: systemd-private-40d02ea2cfad4a598fd2a04003d407d9-mariadb.service-Wn4jIf/: Permission denied
    #seems like I do not have permission to enter the mariadb tmp folder where data is being held. Might be why I cannot execute the command

    command = 'cp /tmp/systemd-private-*-mariadb.service-*/tmp/friends1_%s /home/rmacy/mysql_output/friends_%s' % (date, date) #file friends should exist in the rmacy directory now
    print command
    os.system(command)

    #using rmacy directory it should be added to base path now inside my own diretory
    print "call file_diff function to remove the top12k users from list of friends and to store the result in pure_friends file"
    file_diff('/home/rmacy/mysql_output/friends_%s' % date, base_path + 'top12k', base_path + 'pure_friends', index1=0, sep1=',')

    print "sort the pure_friends file based on number of followers"
    unix_sort(base_path + 'pure_friends', 2, base_path + 'pure_friends.sorted', separator=',')

    print "select the top 12000 of most followed friends"
    cnt = 0
    with open(base_path + 'pure_friends.sorted.top12k', 'w') as top: #new file
        with open(base_path + 'pure_friends.sorted') as sort:
            for line in sort:
                cnt += 1
                top.write(line.strip().split(',')[0] + '\n')
                if cnt == 12000: 
                    break

    print "call follower_counter function to count the followers of the top12k of most followed friends and to store them in most_followed_friends file"
    followers_counter(base_path + 'pure_friends.sorted.top12k', 'tokens_LMA1', base_path + 'most_followed_friends')

    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')
    print "query to find the min number of followers among all top12k twitter accounts"
    query2 = "SELECT min(followers_count) FROM Elite_Weekly.users;"
    cursor = dbm.cursor()
    cursor.execute(query2)
    min_num_followers = cursor.fetchone()[0]

    print "find those accounts from top 12000 most followed friends that have more followers than the least popular twitter account in top12k"
    with open(base_path + 'most_followed_friends.final', 'w') as fin:
        with open(base_path + 'most_followed_friends') as fp:
            for line in fp:
                if int(line.strip().split(',')[1]) > min_num_followers:
                    fin.write(line.strip().split(',')[0] + '\n')

    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')
    print "call friend_finder function to add the friends of finalized important users to the existing database"
    friend_finder(base_path + 'most_followed_friends.final', 'tokens_LMA1', date, dbm)

    print "call Morgan's code to collect profile of finalized important users."
    os.system(
        'java -cp "./TW_Crawler/out/production/TW_Crawler/gson-2.8.6.jar:./TW_Crawler/out/production/TW_Crawler/twitter4j-core-3.0.5.jar:./TW_Crawler/out/production/TW_Crawler/mysql-connector-java-5.1.16-bin.jar:./TW_Crawler/out/production/TW_Crawler/" Collect %sdb_%s.txt token.txt %smost_followed_friends.final u' % (
        base_path, date, base_path))

    print "call name_finder function to create URLs to see if the finalized important users could be found on socialbakers.com"
    name_finder(base_path + 'most_followed_friends.final', 'tokens_LMA1', base_path + 'most_followed_friends_with_name')

    print "call social_country_finder function to crawl socialbaker.com to obtain country and social tags for most followed friends."
    social_country_finder(base_path + 'most_followed_friends_with_name', base_path + 'most_followed_friends_error',
                          base_path + 'most_followed_friends_social')

    print "move the most_followed_friends_social into mysql_output folder where sql server has access to."
    os.rename(base_path + 'most_followed_friends_social',
              '/home/rmacy/mysql_output/most_followed_friends_social_' + date)

    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')

    print "store social information of important friends into social_baker table"
    social_query = "LOAD DATA LOCAL INFILE '/home/rmacy/mysql_output/most_followed_friends_social_%s' INTO TABLE Elite_Weekly.social_baker FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';" % (
    date)
    cursor = dbm.cursor()
    cursor.execute(social_query)
    os.rename('/home/rmacy/mysql_output/most_followed_friends_social_' + date,
              base_path + 'most_followed_friends_social')

    print "create a table that contains initial 12000 users."
    os.rename(base_path + 'top12k', '/home/rmacy/mysql_output/top12k_' + date)
    create_query = "CREATE TABLE IF NOT EXISTS Elite_Weekly.initial_12k_%s (uid BIGINT NOT NULL default 0) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;" % (date)
    cursor = dbm.cursor()
    cursor.execute(create_query)
    load_query = "LOAD DATA LOCAL INFILE '/home/eugenet/mysql_output/top12k_%s' INTO TABLE Elite_Weekly.initial_12k_%s LINES TERMINATED BY '\n';" % (date,date)
    os.rename('/home/rmacy/mysql_output/top12k_' + date, base_path + 'top12k')




    dbm = MySQLdb.connect(host='localhost',
                          user='rmacy',
                          passwd='RWM3cyrus',
                          db='Elite_Weekly')

    cursor = dbm.cursor()

    myre = compile(u'['
                   u'\U0001F300-\U0001F64F'
                   u'\U0001F680-\U0001F6FF'
                   u'\u2600-\u26FF\u2700-\u27BF]+',
                   UNICODE)

    print "Query to get union of users that are inserted into database"
    q = "SELECT distinct(id) FROM Elite_Weekly.users INTO OUTFILE '/tmp/top12k-%s' LINES TERMINATED BY '\n';" % (date)
    cursor.execute(q.encode('utf-8'))
    command = 'cp /tmp/systemd-private-*-mariadb.service-*/tmp/top12k-%s /home/rmacy/mysql_output/' % date
    os.system(command)


    id_file = '/home/rmacy/mysql_output/top12k-%s' % date
    token_file = 'tokens_LMA1'

    user_list = set()
    with open(id_file) as ids:
        for line in ids:
            user_list.add(line.strip())

    all_tokens = []
    tokens = open(token_file)
    for line in tokens:
        all_tokens.append(line.strip().split()[:])
    last_timeout = time.time()
    token_counter = 1

    create_query = "CREATE TABLE IF NOT EXISTS Elite_Weekly.tweet_hashtags_%s (tweet_id CHAR(30) NOT NULL, hashtag VARCHAR(255)) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;" % (date)
    cursor = dbm.cursor()
    cursor.execute(create_query)
    create_query = "CREATE TABLE IF NOT EXISTS Elite_Weekly.tweet_user_mentions_%s (tweet_id CHAR(30) NOT NULL, user_mention VARCHAR(255)) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;" % (date)
    cursor = dbm.cursor()
    cursor.execute(create_query)
    create_query = "CREATE TABLE IF NOT EXISTS Elite_Weekly.tweet_urls_%s (tweet_id CHAR(30) NOT NULL, url VARCHAR(255)) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;" % (date)
    cursor = dbm.cursor()
    cursor.execute(create_query)

    create_query = "CREATE TABLE IF NOT EXISTS Elite_Weekly.tweet_%s  ( tweet_id char(30) NOT NULL DEFAULT '', text varchar(255) DEFAULT NULL, time_created char(50) DEFAULT NULL, is_reply char(10) DEFAULT NULL, is_retweet char(10) DEFAULT NULL, original_tweet_id char(30) DEFAULT NULL, original_user_id char(20) DEFAULT NULL, original_screen_name char(50) DEFAULT NULL, retweet_count char(10) DEFAULT NULL, favorite_count char(10) DEFAULT NULL, user_id char(20) DEFAULT NULL, in_reply_to_sid char(30) DEFAULT NULL, in_reply_to_uid char(20) DEFAULT NULL, is_truncated char(10) DEFAULT NULL, is_possibly_sensitive char(10) DEFAULT NULL, geo_location char(30) DEFAULT NULL, lang char(10) DEFAULT NULL, source varchar(255) DEFAULT NULL, hashtag_count char(10) DEFAULT NULL, user_mention_count char(10) DEFAULT NULL, url_count char(10) DEFAULT NULL, time_collected char(40) DEFAULT NULL, PRIMARY KEY (tweet_id)) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;" % (date)
    cursor = dbm.cursor()
    cursor.execute(create_query)



    for user in user_list:
        max_id = 0
        tweet_list = []
        for i in range(20):
            while True:
                try:
                    consumer_key, consumer_secret, access_token, access_secret = all_tokens[token_counter % len(all_tokens)]
                    twitter = twython.Twython(consumer_key, consumer_secret, access_token, access_secret)

                    if max_id == 0:
                        search = twitter.get_user_timeline(id=user, count=200)
                    else:
                        search = twitter.get_user_timeline(id=user, count=200, include_retweets=True, max_id=max_id)

                    for t in search:
                        tweet_list.append(t)

                    old_max_id = max_id
                    max_id = tweet_list[-1]['id']-1
                    if old_max_id == max_id:
                        i = 21
                        break

                    break

                except twython.TwythonRateLimitError, e:
                    print "token number is %d" % (token_counter % len(all_tokens))
                    token_counter += 1
                except Exception, e:
                    print 'Error Occured, printed below'
                    print e
                    break

                if token_counter % len(all_tokens) == 0:
                    sleep_amount = 900
                    if sleep_amount < 0:
                        sleep_amount = 0
                    last_timeout = time.time()
                    print "Tokens are exhausted, sleeping for %f minutes" % (sleep_amount/60.0)
                    time.sleep(sleep_amount)
                    token_counter += 1

        print 'found %d tweets for user %s' % (len(tweet_list), user)
        print 'inserting tweets into database for user %s' % (user)
        for item in tweet_list:
            try:
                # json.dumps(item, outfile)
                tweet_id = item['id']
                text = myre.sub('', item['text']).replace('\n', ' ').replace('\t', ' ')
                time_created = item['created_at']
                user_id = item['user']['id']
                if 'retweeted_status' in item:
                    is_retweet = 1
                    original_tweet_id = item['retweeted_status']['id']
                    original_user_id = item['retweeted_status']['user']['id']
                    original_screen_name = item['retweeted_status']['user']['screen_name']
                else:
                    is_retweet = 0
                    original_tweet_id = 'Null'
                    original_user_id = 'Null'
                    original_screen_name = 'Null'
                retweet_count = item['retweet_count']
                favorite_count = item['favorite_count']
                in_reply_to_sid = item['in_reply_to_user_id']
                in_reply_to_uid = item['in_reply_to_status_id']
                if in_reply_to_sid or in_reply_to_uid:
                    is_reply = 1
                else:
                    is_reply = 0
                is_truncated = item['truncated']
                is_possibly_sensitive = 'false'
                geo_location = str(item['geo'])
                lang = item['lang']
                source = item['source']
                hashtag_count = len(item['entities']['hashtags'])
                user_mention_count = len(item['entities']['user_mentions'])
                url_count = len(item['entities']['urls'])
                time_collected = time.strftime("%Y%m%d")
                for i in range(hashtag_count):
                    hashtag = item['entities']['hashtags'][i]['text']
                    try:
                        q ='INSERT INTO Elite_Weekly.tweet_hashtags_%s (tweet_id, hashtag) VALUES ("%s","%s");' % (date,
                                           tweet_id,
                                           hashtag)
                        cursor.execute(q.encode('utf-8'))
                    except UnicodeEncodeError, e:
                        print 'UnicodeEncodeError occured, printed below.'
                        print e, text, user_id
                        print traceback.print_exc()
                    # except Exception, e:
                        print q
                        print 'Error occurred, printed below.'
                        print e, text, user_id
                    dbm.commit()
                for i in range(user_mention_count):
                    user_mention = item['entities']['user_mentions'][i]['screen_name']
                    try:
                        q ='INSERT INTO Elite_Weekly.tweet_user_mentions_%s (tweet_id, user_mention) VALUES ("%s","%s")' % (date,
                                           tweet_id,
                                           user_mention)
                        cursor.execute(q.encode('utf-8'))
                    except UnicodeEncodeError, e:
                        print 'UnicodeEncodeError occured, printed below.'
                        print e, text, user_id
                        print traceback.print_exc()
                    # except Exception, e:
                        print q
                        print 'Error occurred, printed below.'
                        print e, text, user_id
                    dbm.commit()
                for i in range(url_count):
                    url = item['entities']['urls'][i]['expanded_url']
                    try:
                        q ='INSERT INTO Elite_Weekly.tweet_urls_%s (tweet_id,url) VALUES ("%s","%s");' % (date,
                                           tweet_id,
                                           url)
                        cursor.execute(q.encode('utf-8'))
                    except UnicodeEncodeError, e:
                        print 'UnicodeEncodeError occured, printed below.'
                        print e, text, user_id
                        print traceback.print_exc()
                    # except Exception, e:
                        print q
                        print 'Error occurred, printed below.'
                        print e, text, user_id
                    dbm.commit()
                try:
                    q = 'INSERT INTO Elite_Weekly.tweet_%s (tweet_id, text, time_created, is_reply, is_retweet, original_tweet_id, original_user_id, original_screen_name, retweet_count, favorite_count, user_id, in_reply_to_sid, in_reply_to_uid, is_truncated, is_possibly_sensitive, geo_location, lang, source, hashtag_count, user_mention_count, url_count, time_collected) VALUES ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");' % (date , tweet_id,
                                       text.replace('"', ''),
                                       time_created,
                                       is_reply,
                                       is_retweet,
                                       original_tweet_id,
                                       original_user_id,
                                       original_screen_name,
                                       retweet_count,
                                       favorite_count,
                                       user_id,
                                       in_reply_to_sid,
                                       in_reply_to_uid,
                                       is_truncated,
                                       is_possibly_sensitive,
                                       geo_location,
                                       lang,
                                       source.replace('"', ''),
                                       hashtag_count,
                                       user_mention_count,
                                       url_count,
                                       time_collected)
                    # print q 
                    cursor.execute(q.encode('utf-8'))

                except UnicodeEncodeError, e:
                    print q
                    print 'UnicodeEncodeError occured, printed below.'
                    print e, text, user_id
                    print traceback.print_exc()
                except Exception, e:
                    print '\n\nError occurred, printed below.'
                    print e, text, user_id
                dbm.commit()
            except:
                pass
    dbm.close()
    
    user_dict = {}
    dbm = mysql.connector.connect(host='localhost',
                                  user='rmacy',
                                  passwd='RWM3cyrus',
                                  db='Elite_Weekly')
    cursor = dbm.cursor()
    command = "SELECT DISTINCT user_id,lang,COUNT(tweet_id) FROM Elite_Weekly.tweet_%s GROUP BY user_id,lang;" % date
    print command
    cursor.execute(command)
    results = cursor.fetchall()
    for i in range(len(results)):
        results[i] = re.sub(r'\(u\'([0-9]*)\', u\'([a-z]*)\', ([0-9]*)\)', r'\g<1> \g<2> \g<3>', str(results[i]))
        results[i] = results[i].split()
        results[i][2] = int(results[i][2])
        if(results[i][0] not in user_dict.keys()):
            user_dict[results[i][0]] = [results[i][1], results[i][2]]
        elif(user_dict[results[i][0]][1] < results[i][2]):
            user_dict[results[i][0]] = [results[i][1], results[i][2]]
    command = "SELECT DISTINCT user_id,COUNT(tweet_id) FROM Elite_Weekly.tweet_%s GROUP BY user_id;" %date
    print command
    cursor.execute(command)
    user_tweet_counts = cursor.fetchall()
    for i in range(len(user_tweet_counts)):
        user_tweet_counts[i] = re.sub(r'\(u\'([0-9]*)\', ([0-9]*)\)', r'\g<1> \g<2>', str(user_tweet_counts[i]))
        user_tweet_counts[i] = user_tweet_counts[i].split()
        user_tweet_counts[i][1] = int(user_tweet_counts[i][1])
        user_dict[user_tweet_counts[i][0]][1] = float(user_dict[user_tweet_counts[i][0]][1])/float(user_tweet_counts[i][1])
    language_file = base_path + 'top12k_languages_' + date
    l_f = open(language_file, 'w')
    for user in user_dict.keys():
        for i in range(len(user_dict[user])):
            user_dict[user][i] = str(user_dict[user][i])
        l_f.write(str(user) + ',' + ','.join(user_dict[user]) + '\n')
    l_f.close()
    

    topxk_sourced_lines = find_friendslite_most_followed_friends(base_path + 'pure_friends', base_path + 'top12k_sourced' , 'tokens_LMA1')
    topxk_sourced_file = base_path + 'top12k_sourced_with_mff_' + date
    out = open(topxk_sourced_file, 'w')
    for line in topxk_sourced_lines:
        out.write(str(line[0]) + ',[' + str(line[1]) + ',' + str(line[2]) + ']\n')
    out.close()
    topxk_sourced_rankings_file = base_path + 'top12k_source_rankings_' + date
    generate_topxk_sourced_ranking_report(topxk_sourced_file, topxk_sourced_rankings_file)
    topxk_ranks_file = base_path + 'top12k_source_ranks_' + date
    topxk_ranks(topxk_sourced_file, topxk_ranks_file)
    print '\n\n======   Done!  ======== \n\n'
