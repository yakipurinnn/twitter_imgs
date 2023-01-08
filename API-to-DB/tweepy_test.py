import tweepy
import pprint
import os
import sys
import subprocess
sys.path.append("./API-to-DB/functions")
from open_json import open_json
from get_tweet_type import get_tweet_type


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

    tweet1 = api.get_status(1610959627893764096, include_ext_alt_text=True)._json
    pprint.pprint(tweet1)