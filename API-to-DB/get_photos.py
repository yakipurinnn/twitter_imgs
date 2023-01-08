import pprint
import time
import datetime
from MySQLdb import IntegrityError
from tweepy.errors import TooManyRequests
from tweepy.errors import NotFound
from tweepy.errors import Unauthorized
from tweepy.errors import TwitterServerError
from functions.to_JST_time import to_JST_time
from functions.get_tweet_type import get_tweet_type
from update_db import UpdateDB
from download_photos import DownloadPhotos


class GetPhotos:
    def __init__(self, api, connection):
        '''
        apiに twitter.API(auth)を指定、connectionには MySQLdb.connect.cursor()を指定する
        '''
        self.api = api
        self.connection = connection
        self.cursor = self.connection.cursor()
    
    def get_photos(self, get_type, user_id, count, max_id=None):
        temp = 1000
        if get_type == 'favorite':
            temp = 16
        start = 0
        total = 0
        for i in range(temp):
            only_tweet_flag = 0
            try:
                if get_type == 'favorite':
                    tweets = self.api.get_favorites(user_id=user_id, max_id=max_id, count=count, include_ext_alt_text=True)
                elif get_type == 'user_timeline':
                    tweets = self.api.user_timeline(user_id=user_id, max_id=max_id, count=count, exclude_replies=True, include_ext_alt_text=True)
                print('tweetは', len(tweets), '件です')
            except Unauthorized as e:
                print(type(e), e)
                break
            except TooManyRequests as e:
                print(type(e), e)
                print("twitterAPI制限のため1分間待機します")
                time.sleep(60)
                continue
            except TwitterServerError as e:
                print(type(e), e)
                print("サーバーエラーのため1分間待機します")
                time.sleep(60)
                continue

            #取得ツイートが0件の場合(全てreply, RTでないか確認)
            if len(tweets) == 0 and get_type == 'user_timeline':
                temp_max_id = self.get_max_id(user_id=user_id, max_id=max_id, count=count)
                if temp_max_id == 0:
                    updatedb.save()
                    self.connection.commit()
                    print('apiよりtweetを取得できなかったため終了します')
                    break
                else:
                    max_id = temp_max_id
                    continue

            #取得ツイートが1件の場合(全てreply, RTでないか確認)(最終ツイートの可能性が高い)
            elif len(tweets) == 1 and get_type == 'user_timeline':
                temp_max_id = self.get_max_id(user_id=user_id, max_id=max_id, count=count)
                if temp_max_id == max_id:
                    updatedb.save()
                    self.connection.commit()
                    print('取得できる最後のツイートのため終了します')
                    break
                else:
                    max_id = temp_max_id
                    only_tweet_flag = 1    #RTやリプライも含めてmax_idを取得した場合は0番目のtweetもDBに登録する
                
            if max_id is None and start==0:    #最初のループのみ取得した0番目のツイートを表示(次回のループではmax_idが被るため)
                start = 0
            elif only_tweet_flag == 1:
                start = 0
            else:
                start = 1

            for j in range(start, count):    #max_idのtweetはループの最後のidと次のループの最初のidで重複するためループは１から始める
                time1 = time.time()
                try:
                    tweet = tweets[j]._json
                    total += 1
                except IndexError as e :
                    # print(pprint.pprint(tweets[j-1]))
                    print(type(e), e, f'取得したtweetは {j}件でした 次のtweetを取得します')
                    break

                tweet_id = tweet['id']
                created_at = to_JST_time(tweet['created_at'])
                tweet_type = get_tweet_type(tweet)
                print('total:', total, 'loop:', i*(count-1) + j + 1, j, 'tweet_id:', tweet_id, 'screen_name:',tweet['user']['screen_name'], tweet['user']['id'], created_at, tweet_type, time.time()-time1)

                #DB登録、更新
                updatedb = self.controlldb(tweet)

                if only_tweet_flag == 0:
                    max_id = tweet_id

            self.connection.commit()

    def get_latest_photos(self, user_id, count, max_id=None):
        get_type = 'favorite'
        self.get_photos(get_type, user_id, count, max_id = max_id)

    def get_user_photos(self, user_id, count, max_id=None):
        get_type = 'user_timeline'
        self.get_photos(get_type, user_id, count, max_id = max_id)

    def get_max_id(self, user_id, count, max_id=None):
        #取得したtweetsが全てreplyまたはRTだった場合を判定する場合に利用
        # max_idのみを返す
        tweets = self.api.user_timeline(user_id=user_id, max_id=max_id, count=count, include_ext_alt_text=True)
        if len(tweets) > 1:
            max_tweet_id = tweets[len(tweets)-1]._json['id']
        else:
            max_tweet_id = 0
        return max_tweet_id

    def controlldb(self, tweet, quoted_flag=False, RT_flag=False):
        tweet_id = tweet['id']
        tweet_type = get_tweet_type(tweet)
        is_quote_status = int(tweet['is_quote_status'])
        if quoted_flag:
            print('    引用元ツイートの情報を登録します', 'tweet_id:', tweet_id, tweet_type)
        if  RT_flag:
            print('    リツイート元の情報を登録します', 'retweeted_id:', tweet_id, tweet_type)

        if is_quote_status==1:
            try:
                self.controlldb(tweet['quoted_status'], quoted_flag=True)
            except KeyError as e:    #既に引用元ツイートが削除されている場合
                print(    type(e), e, '引用元ツイートは既に削除された可能性があります')

        updatedb = UpdateDB(self.connection, tweet, tweet_type)

        #RTの場合
        if 'retweeted_status' in tweet.keys():
            try:
                self.controlldb(tweet['retweeted_status'], RT_flag=True)
                updatedb.insert_retweet()
            except IntegrityError as e:
                print('    このリツイートは既に登録済みです。', 'tweet_id:', tweet_id)
        else:
            try:
                updatedb.insert_tweet_status()    #tweetのstatusをDBにinsert
                if tweet_type == 'photo':    #画像ダウンロード
                    download_phtos = DownloadPhotos(tweet)
                    download_phtos.download()
            except IntegrityError as e:
                updatedb.update_tweet_status()    #tweetのstatusをupdate
                print('    このツイートは既に登録済みです。ツイート情報を更新します。', 'tweet_id:', tweet_id)

            updatedb.update_twitter_users()    #twitter_userをDBにinsertまたはupdate
            updatedb.insert_hash_tags()   #hashtag情報をDBに登録

        if not quoted_flag or RT_flag:
            return updatedb

