from get_photos import GetPhotos
import tweepy
import pprint
import os
import subprocess
import MySQLdb
from functions.open_json import open_json


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
    cursor = connection.cursor()

    get_photos = GetPhotos(api, connection)
    get_photos.get_latest_photos(user_id=my_user_id['user_id'], count=200)