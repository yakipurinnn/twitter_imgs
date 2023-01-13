import tweepy
import pprint
import time
import os
import subprocess
import MySQLdb
from functions.open_json import open_json
from get_photos import GetPhotos
from get_user_relations import GetUserRelations
from tweepy.errors import TooManyRequests

def collect_user_tweets(connection, get_photos, limit_time, sql=None): 
    #まだタイムラインを収集していないuserでフォローしているuserのuser_idを取得
    cursor = connection.cursor()
    if sql is None:
        sql = 'SELECT save_users.user_id FROM save_users INNER JOIN twitter_users ON save_users.user_id = twitter_users.user_id WHERE save_users.tweets_saved_flag=0 AND (twitter_users.following=1);'
    cursor.execute(sql)
    users_id = cursor.fetchall()

    if len(users_id)>0:
        for i in range(len(users_id)):
            print('user_id:', users_id[i][0])
            get_photos.get_user_photos(user_id=users_id[i][0], count=200, max_id=None)
            print('user_timeline取得から経過時間は', time.time()-limit_time, '秒です')
            if time.time()-limit_time > 900:        
                break
    else:
        sql  = 'SELECT save_users.user_id FROM save_users INNER JOIN twitter_users ON save_users.user_id = twitter_users.user_id WHERE twitter_users.following=1;'
        collect_user_tweets(api, connection, sql=sql)


def collect_user_relations(connection, get_user_relations, sql=None):
    cursor = connection.cursor()
    if sql is None:
        sql = 'SELECT save_users.user_id, save_users.relation_next_cursor FROM save_users INNER JOIN twitter_users ON save_users.user_id = twitter_users.user_id WHERE save_users.relation_saved_flag=0 AND (twitter_users.following=1);'
    cursor.execute(sql)
    users_status = cursor.fetchall()

    if len(users_status) > 0:
        for i in range(len(users_status)):
            print('user_id:', users_status[i][0], users_status[i][1])
            get_user_relations.get_following_users(following_user_id=users_status[i][0], next_cursor=users_status[i][1], count=200)
    else:
        sql = 'SELECT save_users.user_id, save_users.relation_next_cursor FROM save_users INNER JOIN twitter_users ON save_users.user_id = twitter_users.user_id WHERE twitter_users.following=1;'
        collect_user_relations(api, connection, sql=sql)



if __name__ == '__main__':
    cwd = subprocess.run('find /home/ -name twitter_imgs -type d', encoding='utf8', shell=True, capture_output=True, text=True)
    os.chdir(cwd.stdout.replace('\n', ''))    #pathの改行コードを削除

    my_user_id_path = './API-to-DB/config/my_user_id.json'
    my_user_id = open_json(my_user_id_path)
    
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

    get_photos = GetPhotos(api, connection)
    get_user_relations = GetUserRelations(api, connection)
    
    temp = 10000

    for i in range(temp):
        print('main: ', i)
        try:
            collect_user_relations(connection, get_user_relations)
        except TooManyRequests as e:
            print(type(e), e, 'api制限に達したためuser_timelineの取得に移ります')

        time1 = time.time()
        if i%32 == 0 and i>0:
            get_photos.get_latest_photos(user_id=my_user_id['user_id'], count=200)
        
        collect_user_tweets(connection, get_photos, time1)
        print('15分経過したためuser_ralationsの取得に移ります')








