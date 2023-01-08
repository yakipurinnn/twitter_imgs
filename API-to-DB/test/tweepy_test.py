import json
import tweepy
import pprint
import os
import subprocess
import sys
import MySQLdb
import time
from MySQLdb import IntegrityError
from tweepy.errors import TooManyRequests
sys.path.append("./API-to-DB/functions")
from download_file import download_file
from open_json import open_json
from to_JST_time import to_JST_time

def get_tweet_type(tweet):
    if 'media' in tweet['entities'].keys() and tweet['is_quote_status'] == False:
        return tweet['extended_entities']['media'][0]['type']

    else:
        return None


if __name__ == '__main__':
    cwd = subprocess.run('find /home/ -name twitter_imgs -type d', encoding='utf8', shell=True, capture_output=True, text=True)
    os.chdir(cwd.stdout.replace('\n', ''))    #pathの改行コードを削除

    key_list_path = './API-to-DB/config/api_keys.json'
    key_list = open_json(key_list_path)

    auth = tweepy.OAuthHandler(key_list['API_KEY'], key_list['API_SECRET'])
    auth.set_access_token(key_list['ACCESS_TOKEN'], key_list['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)

    # tweets = tweepy.Cursor(api.search_tweets, q=["ドル円"], lang="ja").items(1)
    # tweets = tweepy.Cursor(api.user_timeline, id="@houk1se1", lang="ja").items(1)
    # tweets = api.get_user(id="@houk1se1", lang="ja", max_id=)

    #get_favoritesの場合はtweets[0]に対して._jsonを使う since_id, max_idで取得位置を指定max_idで過去側に遡る？(過去→現在：id小→id大?)
    #forで回したうち最後のidをmax_idに持ってくれば、過去に遡って取得できる

    tweet1 = api.get_status(1604094675899404288 , include_ext_alt_text=True)._json   #動画
    tweet2 = api.get_status(1604069937424654336 , include_ext_alt_text=True)._json   #イラスト
    tweet3 = api.get_status(1591034520689848320 , include_ext_alt_text=True)._json   #文
    tweet4 = api.get_status(1604070585234907136 , include_ext_alt_text=True)._json   #fanbox url
    tweet5 = api.get_status(1602395754496131093 , include_ext_alt_text=True)._json   #引用ツイート
    tweet6 = api.get_status(1592203447964954626 , include_ext_alt_text=True)._json   #リプライ
    tweet7 = api.get_status(1604066309205262338 , include_ext_alt_text=True)._json   #複数画像
    tweet8 = api.get_status(1604062598906793984 , include_ext_alt_text=True)._json   #ハッシュタグ付き
    tweet9 = api.get_status(1604829719081336832 , include_ext_alt_text=True)._json   #画像ありでもextend_entitiesがない
    try:
        tweet10 = api.get_status(1605202982559453186 , include_ext_alt_text=True)._json    #消されたツイート
    except Exception as e:
        print(type(e), e)

    # pprint.pprint(tweet1)
    print("-"*40)
    pprint.pprint(tweet2)
    # print("-"*40)
    # pprint.pprint(tweet3)
    # print("-"*40)
    # pprint.pprint(tweet4)
    # print("-"*40)
    pprint.pprint(tweet5)
    print("-"*40)
    # pprint.pprint(tweet6)
    print("-"*40)
    # pprint.pprint(tweet7)
    # print("-"*40)
    # pprint.pprint(tweet8)
    # print("-"*40)
    # pprint.pprint(tweet9)
    # print("-"*40)
    # pprint.pprint(tweet10)
    # print("-"*40)

    # print(api.rate_limit_status()["resources"]["search"]["/search/tweets"])

    # tweet_type = get_tweet_type(tweet9)
    # print(tweet_type)

    # backslash_position = profile_image_url_https.rfind('/')
    # print(profile_image_url_https[backslash_position+1:])


    # photo_id = 0
    # for i in range( len(tweet7['extended_entities']['media'])):
    #     photo_id = tweet7['extended_entities']['media'][i]['media_url_https'].replace('https://pbs.twimg.com/media/', '')
    #     print(photo_id)

    