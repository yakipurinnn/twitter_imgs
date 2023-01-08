import json
import tweepy
import pprint
import os
import sys
import subprocess
import urllib
import MySQLdb
import datetime
sys.path.append("./API-to-DB/functions")
from download_file import download_file
from open_json import open_json
from to_JST_time import to_JST_time

cwd = subprocess.run('find /home/ -name twitter_imgs -type d', encoding='utf8', shell=True, capture_output=True, text=True)
os.chdir(cwd.stdout.replace('\n', ''))    #pathの改行コードを削除

db_config_path = './API-to-DB/config/db_config.json'
db_config = open_json(db_config_path)

connection = MySQLdb.connect(
    host = db_config['host'],
    user = db_config['user'],
    passwd = db_config['passwd'],
    db = db_config['db'],
    charset = db_config['charset'])

cursor = connection.cursor()

tweet_id=1375937068686184453
cursor.execute(f"SELECT * from tweet_hashtag WHERE tweet_id='{tweet_id}';")

is_exists_tweet_ht=cursor.fetchall()

print(len(is_exists_tweet_ht)>0)