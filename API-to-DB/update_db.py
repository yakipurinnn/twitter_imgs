import json
import time
import pprint
import datetime
from MySQLdb import IntegrityError
from functions.to_JST_time import to_JST_time

class UpdateDB:
    def __init__(self, connection, tweet, tweet_type=None):
        self.connection = connection
        self.cursor = self.connection.cursor()

        self.tweet = tweet

        #twitter_user関連
        self.tweet_id = self.tweet['id']
        self.user_id = self.tweet['user']['id']
        self.name = self.tweet['user']['name']
        self.screen_name = self.tweet['user']['screen_name']
        self.user_url = f'https://twitter.com/{self.screen_name}'
        self.user_created_at = to_JST_time(self.tweet['user']['created_at'])
        self.description = self.tweet['user']['description']
        self.followers_count = self.tweet['user']['followers_count']
        self.friends_count = self.tweet['user']['friends_count']
        self.statuses_count = self.tweet['user']['statuses_count']
        self.following = int(self.tweet['user']['following'])
        self.location = self.tweet['user']['location']
        self.verified = int(self.tweet['user']['verified'])
        #profile_banner_url, profile_image_urlが含まれているかを判定
        if 'profile_banner_url' in self.tweet['user'].keys():
            self.profile_banner_url = self.tweet['user']['profile_banner_url']
            self.profile_banner_path = f'./downloaded_imgs/profile_banners/{self.user_id}/{self.screen_name}_banner'
        else:
            self.profile_banner_url = None
            self.profile_banner_path = None
        if 'profile_image_url' in self.tweet['user'].keys():
            self.profile_image_url = self.tweet['user']['profile_image_url']
            self.profile_banner_path = f'./downloaded_imgs/profile_images/{self.user_id}/{self.screen_name}_image'
        else:
            self.profile_image_url = None
            self.profile_banner_path = None
        self.user_api_archive = json.dumps(self.tweet['user'])

        #tweet_status関連
        #tz情報を除去し、日本標準時に変換
        self.created_at = to_JST_time(self.tweet['created_at'])
        self.tweet_url = f'https://twitter.com/{self.screen_name}/status/{self.tweet_id}'
        self.favorite_count = self.tweet['favorite_count']
        self.retweet_count = self.tweet['retweet_count']
        self.tweet_text = str(self.tweet['text'])
        self.user_id = self.tweet['user']['id']
        self.favorited = int(self.tweet['favorited'])
        self.retweeted = int(self.tweet['retweeted'])
        if 'possibly_sensitive' in self.tweet.keys():
            self.possibly_sensitive = int(self.tweet['possibly_sensitive'])
        else:
            self.possibly_sensitive = 0
        self.lang = self.tweet['lang']
        self.is_quote_status = int(self.tweet['is_quote_status'])
        if self.is_quote_status ==1:
            try:
                self.quoted_tweet_id=self.tweet['quoted_status']['id']
            except KeyError as e:    #既に引用元ツイートが削除されている場合
                self.quoted_tweet_id = None
        else:
            self.quoted_tweet_id = None
        self.in_reply_to_user_id = self.tweet['in_reply_to_user_id']
        self.tweet_type = tweet_type
        if self.tweet_type == 'photo':
            self.photo_count = len(self.tweet['extended_entities']['media'])
        else:
            self.photo_count = 0
        self.api_archive = json.dumps(self.tweet)  #json形式に変換

        self.twetter_users_columns =  {'user_id': self.user_id, 'name': self.name, 'screen_name':self.screen_name, 'user_url':self.user_url,
                                        'user_created_at':self.user_created_at, 'description':self.description, 'followers_count':self.followers_count, 'friends_count':self.friends_count, 
                                        'statuses_count':self.statuses_count, 'following':self.following, 'location':self.location, 'verified':self.verified, 
                                        'profile_banner_url':self.profile_banner_url, 'profile_banner_path':self.profile_banner_path, 'profile_image_url':self.profile_image_url, 'profile_image_path':self.profile_banner_path,
                                        'user_api_archive':self.user_api_archive}

        self.tweets_columns = {'tweet_id':self.tweet_id, 'created_at':self.created_at, 'tweet_url':self.tweet_url, 'favorite_count':self.favorite_count,
                                'retweet_count':self.retweet_count, 'tweet_text':self.tweet_text, 'user_id':self.user_id, 'favorited':self.favorited,
                                'retweeted':self.retweeted, 'possibly_sensitive':self.possibly_sensitive, 'lang':self.lang, 'is_quote_status':self.is_quote_status, 'quoted_tweet_id':self.quoted_tweet_id,
                                'in_reply_to_user_id':self.in_reply_to_user_id, 'photo_count':self.photo_count, 'tweet_type':self.tweet_type, 'api_archive':self.user_api_archive}

        #photos関連
        if self.tweet_type == 'photo':
            self.photo_list = []
            for i in range(self.photo_count):
                #まれにある'https://pbs.twimg.com/media/'以下に画像がない場合の回避、その場合photo_countを1少なくする
                if not 'https://pbs.twimg.com/media/' in self.tweet['extended_entities']['media'][i]['media_url_https']:
                    self.photo_count -= 1
                    continue
                photo_id = self.tweet['extended_entities']['media'][i]['media_url_https'].replace('https://pbs.twimg.com/media/', '')
                photo_url = self.tweet['extended_entities']['media'][i]['media_url_https']
                photo_path =  f'./downloaded_imgs/twitter_photos/{self.user_id}/{self.screen_name}_{photo_id}'

                if 'ext_alt_text' in self.tweet['extended_entities']['media'][i].keys():
                    ext_alt_text = self.tweet['extended_entities']['media'][i]['ext_alt_text']
                else:
                    ext_alt_text = None

                photo_columns = {'photo_id': photo_id, 'photo_url': photo_url, 'photo_path': photo_path, 
                                'ext_alt_text': ext_alt_text, 'tweet_id': self.tweet_id}
                self.photo_list.append(photo_columns)

        #hash_tag_関連、tweet_hashtag関連
        self.hashtag_list = []
        self.tweet_hashtag_list = []
        for i in range(len(self.tweet['entities']['hashtags'])):
            hashtag = self.tweet['entities']['hashtags'][i]['text']
            
            hashtag_columns = {'hashtag': hashtag}
            self.hashtag_list.append(hashtag_columns)

            self.cursor.execute(f"SELECT hashtag_id FROM hashtags WHERE hashtag='{hashtag}'")
            inserted_ht_id = self.cursor.fetchall()

            if len(inserted_ht_id) == 0:
                #hashtagがまだDBに登録されていない場合、hashtag_idはこの時点で未定のため一時的に0を入れる
                tweet_hashtag_columns = {'tweet_id': self.tweet_id, 'hashtag_id': 0}
            else:
                tweet_hashtag_columns = {'tweet_id': self.tweet_id, 'hashtag_id': inserted_ht_id[0][0]}
            
            self.tweet_hashtag_list.append(tweet_hashtag_columns)

        self.inserted_ht_list = []    #既にDBにあるhashtagのリスト[xxx, yyy, ...]の形
        self.insert_ht_list = []     #これからinsertするhashtagのリスト[{'hashtag': xxx}, ...]の形
        if not self.hashtag_list == []:    #hashtagがあるなら
            #hashtagがすでに登録されていなか確認する
            self.cursor.execute('SELECT hashtag FROM hashtags')
            for ht in self.cursor.fetchall():
                self.inserted_ht_list.append(ht[0])

            for i in range(len(self.hashtag_list)):
                #DB上に存在しないhashtagのみをinsertする
                if not self.hashtag_list[i]['hashtag'] in self.inserted_ht_list:
                    self.insert_ht_list.append(self.hashtag_list[i])
        
            #DBより最大のhashtag_idを取り出す
            self.cursor.execute('SELECT hashtag_id FROM hashtags ORDER BY hashtag_id DESC')
            self.last_id = self.cursor.fetchone()
            #last_idがNoneの場合(hashtagがまだ1つも登録されていない場合)last_idは0とする)
            if not self.last_id is None:
                 self.last_id = self.last_id[0]
            else:
                self.last_id = 0

            new_ht_count = 0  
            for i in range(len(self.tweet_hashtag_list)):
                if self.tweet_hashtag_list[i]['hashtag_id'] == 0:
                    self.tweet_hashtag_list[i]['hashtag_id'] = self.last_id + 1 + new_ht_count
                    new_ht_count += 1

        #retweets関連
        self.retweets_columns={'retweet_id': self.tweet_id, 'retweeted_at': self.created_at, 'user_id': self.user_id, 
                                'retweeted_id': None}
        if 'retweeted_status' in tweet.keys():
            self.retweets_columns['retweeted_id'] = self.tweet['retweeted_status']['id']
            
        #save_points関連
        self.save_points_columns = {'saved_flag': 'saved_flag + 1'}

    def escape_sql(self, string):
        #SQL文用エスケープ
        if type(string) == str:
            if "'" in string:
                string = string.replace("'", "''")
            if '"' in string:
                string = string.replace('"', '""')
            if '\\' in string:
                string = string.replace('\\', '\\\\')
        return string

    def insert_tweet_id(self):
        '''
        tweet_idのみをtweetsテーブルにinsertする
        '''
        # tweer_idをDBにinsert
        self.cursor.execute(f"""INSERT INTO tweets (tweet_id) 
            VALUES ('{self.tweet_id}')""")

    def del_None_from_columns(self, columns):
        #Noneを値にもつ値は挿入しない(DB上の値をNoneではなくNULLにするため)
        del_key_list = []
        for key, value in columns.items():
            if value is None:
                del_key_list.append(key)

        for key in del_key_list:
            del columns[key]

        return columns
    
    def insert_tweet_status(self):
        '''
        tweetの各status全てをtweets, photoデーブルにinsertする
        '''
        insert_columns = self.tweets_columns.copy()
        insert_columns = self.del_None_from_columns(insert_columns)
        
        sql = self.create_insert_statement('tweets', insert_columns)
        self.cursor.execute(sql)

        if self.tweet_type == 'photo':
            for i in range(self.photo_count):
                photo_columns = self.photo_list[i].copy()
                photo_columns = self.del_None_from_columns(photo_columns)
                sql = self.create_insert_statement('photos', photo_columns)
                self.cursor.execute(sql)

    def update_tweet_status(self):
        update_columns = self.tweets_columns.copy()
        
        update_columns['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')    #update_timeも更新する

        del update_columns['tweet_id'], update_columns['created_at'], update_columns['tweet_url'], update_columns['user_id'],\
            update_columns['is_quote_status'], update_columns['in_reply_to_user_id'], update_columns['photo_count'], update_columns['tweet_type'],\
            update_columns['favorited'], update_columns['retweeted'] #更新が必要ないカラムを除去、favorite, retweet記録は基本的に更新しない
        
        update_columns = self.del_None_from_columns(update_columns)
        sql = self.create_update_statement('tweets', update_columns, 'tweet_id', self.tweet_id)
        self.cursor.execute(sql)

    def update_twitter_users(self):
        update_columns = self.twetter_users_columns.copy()
        update_columns = self.del_None_from_columns(update_columns)
        try:
            sql = self.create_insert_statement('twitter_users', update_columns)
            self.cursor.execute(sql)
        except IntegrityError as e:
            update_columns['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')    #update_timeも更新する

            del update_columns['user_id'], update_columns['user_created_at']    #更新が必要ないカラムを除去

            sql = self.create_update_statement('twitter_users', update_columns, 'user_id', self.user_id)
            self.cursor.execute(sql)

    def insert_hash_tags(self):
        if not self.hashtag_list == []:    #hashtagがあるなら
            self.cursor.execute(f"SELECT * from tweet_hashtag WHERE tweet_id='{self.tweet_id}'")
            is_exists_tweet_ht=self.cursor.fetchall()

            if len(is_exists_tweet_ht)==0:    #まだtweet_hashtagテーブルに今回のtweet_idが登録されていなければ 
                for i in range(len(self.tweet_hashtag_list)):
                    tweet_hashtag_columns = self.tweet_hashtag_list[i].copy()
                    sql = self.create_insert_statement('tweet_hashtag', tweet_hashtag_columns)
                    self.cursor.execute(sql)

                for i in range(len(self.insert_ht_list)):
                    sql = self.create_insert_statement('hashtags', self.insert_ht_list[i])
                    self.cursor.execute(sql)

    def insert_retweet(self):
        retweets_columns = self.retweets_columns.copy()
        retweets_columns = self.del_None_from_columns(retweets_columns)
        sql = self.create_insert_statement('retweets', retweets_columns)
        self.cursor.execute(sql)

    def create_insert_statement(self, table_name, columns):
        '''
        insertのsql文を生成し返す
        引数table_nameにtable名の文字列を指定
        columnsに**{カラム名:挿入する値, ...}のように指定する
        例: create_insert_statement('tweets', **{'tweet_id': self.tweet_id, 'created_at':self.created_at}
        '''
        insert_columns =''
        insert_values = ''
        
        for name, value in columns.items():
            value = self.escape_sql(value)
            insert_columns += ', ' + str(name)
            insert_values += f", '{value}'"

        #最初の , を消去する
        insert_columns = insert_columns.replace(',', '', 1)
        insert_values = insert_values.replace(',', '', 1)

        sql = f'INSERT INTO {table_name}({insert_columns}) VALUES ({insert_values})'
        return sql

    def create_update_statement(self, table_name, columns, id_name, id_value):
        '''
        create_insert_statementのupdate文バージョン
        引数は同様
        更新するレコードを指定するためid_nameとid_valueを指定する
        '''
        update_columns = ''
        for name, value in columns.items():
            value = self.escape_sql(value)
            update_columns += f", {name} = '{value}'"

        update_columns = update_columns.replace(',', '', 1)

        sql = f'UPDATE {table_name} SET {update_columns} WHERE {id_name} = {id_value}'
        return sql

    def save(self):
        save_points_columns = self.save_points_columns.copy()
        save_points_columns['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')    #update_timeも更新する
        
        sql = self.create_update_statement('save_users', save_points_columns, 'user_id', self.user_id).replace("'saved_flag + 1'", "saved_flag + 1")
        self.cursor.execute(sql) 
        print(sql)
        
    #テスト用関数
    def test(self):
        sql = self.create_update_statement('tweets', {'tweet_id': self.tweet_id, 'created_at':self.created_at}, 'user_id', self.user_id)
        print(sql)

