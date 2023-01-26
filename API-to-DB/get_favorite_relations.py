import pprint
import time
import datetime
from MySQLdb import IntegrityError
from tweepy.errors import TooManyRequests
from tweepy.errors import NotFound
from tweepy.errors import Unauthorized
from tweepy.errors import TwitterServerError
from update_db import UpdateDB

class GetFavoriteRelations:
    def __init__(self, api, connection):
        '''
        apiに twitter.API(auth)を指定、connectionには MySQLdb.connect.cursor()を指定する
        '''
        self.api = api
        self.connection = connection
        self.cursor = self.connection.cursor()

    def get_user_favorite(self, user_id):
        temp = 1000
        total=1
        last_user_flag = False

        for i in range(temp):
            dupulicate_count = 0
            if last_user_flag:
                break
            try:
                following_users_status = self.api.get_friends(user_id=following_user_id, count=count, cursor=next_cursor, skip_status=True)
                print('取得されたフォロワーは', len(following_users_status[0]), '件です')
                #フォロー数が0の場合、break
                if len(following_users_status[0])==0 and last_user_flag==False and next_cursor==-1:
                    break
            except Unauthorized as e:
                print(type(e), e)
                break
            except NotFound as e:
                print("既にこのユーザーは削除された可能性があります")
                updatedb = UpdateDB(self.connection)
                updatedb.save_deleted_user(following_user_id)
                updatedb.save_relations(following_user_id)
                self.connection.commit()
                last_user_flag=True
                continue
            # except TooManyRequests as e:
            #     print(type(e), e)
            #     print("twitterAPI制限のため1分間待機します")
            #     continue
            except TwitterServerError as e:
                print(type(e), e)
                print("サーバーエラーのため1分間待機します")
                time.sleep(60)
                continue
