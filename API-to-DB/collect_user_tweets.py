import tweepy
import pprint
import os
import subprocess
import MySQLdb
from functions.open_json import open_json
from get_photos import GetPhotos


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

    get_photos = GetPhotos(api, connection)
    
    cursor = connection.cursor()
    #まだタイムラインを収集していないuserでfollower5000人以上またはフォローしているuserのuser_idを取得
    sql = 'SELECT save_users.user_id FROM save_users INNER JOIN twitter_users ON save_users.user_id = twitter_users.user_id WHERE save_users.saved_flag=0 AND (twitter_users.followers_count>5000 OR twitter_users.following=1);'
    cursor.execute(sql)
    users_id = cursor.fetchall()
    
    if len(users_id)>0:
        for i in range(len(users_id)):
            print('user_id:', users_id[i][0])
            get_photos.get_user_photos(user_id=users_id[i][0], count=200, max_id=None)
    else:
        sql  = 'SELECT save_users.user_id FROM save_users INNER JOIN twitter_users ON save_users.user_id = twitter_users.user_id WHERE twitter_users.followers_count>5000 OR twitter_users.following=1 ORDER BY save_users.update_time;'
        cursor.execute(sql)
        users_id = cursor.fetchall()
        for i in range(len(users_id)):
            print('user_id:', users_id[i][0])
            get_photos.get_user_photos(user_id=users_id[i][0], count=200, max_id=None)
