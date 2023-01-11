import pprint
import time
import datetime
import os
import subprocess
import tweepy
import MySQLdb
from MySQLdb import IntegrityError
from functions.open_json import open_json
from update_db import UpdateDB
from get_user_relations import GetUserRelations


if __name__ == '__main__':
    cwd = subprocess.run('find /home/ -name twitter_imgs -type d', encoding='utf8', shell=True, capture_output=True, text=True)
    os.chdir(cwd.stdout.replace('\n', ''))    #pathの改行コードを削除

    #twitterAPIに接続
    key_list_path = './API-to-DB/config/api_keys.json'
    key_list = open_json(key_list_path)

    auth = tweepy.OAuthHandler(key_list['API_KEY'], key_list['API_SECRET'])
    auth.set_access_token(key_list['ACCESS_TOKEN'], key_list['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)

    #MySQLに接続
    db_config_path = './API-to-DB/config/db_config.json'
    db_config = open_json(db_config_path)

    connection = MySQLdb.connect(
        host = db_config['host'],
        user = db_config['user'],
        passwd = db_config['passwd'],
        db = db_config['db'],
        charset = db_config['charset'])
    cursor = connection.cursor()

    get_user_relations = GetUserRelations(api, connection)

    sql = 'SELECT save_users.user_id, save_users.relation_next_cursor FROM save_users INNER JOIN twitter_users ON save_users.user_id = twitter_users.user_id WHERE save_users.relation_saved_flag=0 AND (twitter_users.following=1);'
    cursor.execute(sql)
    users_status = cursor.fetchall()

    for i in range(len(users_status)):
        print('user_id:', users_status[i][0], users_status[i][1])
        get_user_relations.get_following_users(following_user_id=users_status[i][0], next_cursor=users_status[i][1], count=200)
