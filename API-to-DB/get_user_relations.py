import pprint
import time
import datetime
from MySQLdb import IntegrityError
from tweepy.errors import TooManyRequests
from tweepy.errors import NotFound
from tweepy.errors import Unauthorized
from tweepy.errors import TwitterServerError
from update_db import UpdateDB


class GetUserRelations:
    def __init__(self, api, connection):
        '''
        apiに twitter.API(auth)を指定、connectionには MySQLdb.connect.cursor()を指定する
        '''
        self.api = api
        self.connection = connection
        self.cursor = self.connection.cursor()

    def get_following_users(self, following_user_id, next_cursor, count):
        temp = 1000
        total=1
        next_cursor = next_cursor
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

            for j in range(len(following_users_status[0])):
                try:
                    user_status = following_users_status[0][j]._json
                    user_id = user_status['id']
                    screen_name = user_status['screen_name']
                    print(total, i*200+j, j, 'following_user_id:', following_user_id, 'followed_user_id:', user_id, screen_name)

                    updatedb = UpdateDB(self.connection, user_status , user_only=True)
                    updatedb.update_twitter_users()
                    updatedb.insert_user_relations(following_user_id)
                    
                except IntegrityError as e:    #重複エラーの場合はbreak (following_usersは新しくfollowした順に返されるため)
                    self.connection.commit()
                    print(type(e), e)
                    dupulicate_count += 1
                    if dupulicate_count >10:
                        print('10回連続で重複したため次のユーザーへ移ります')
                        last_user_flag=True
                        break

                total += 1
                
                if j+1 == len(following_users_status[0]):
                    if following_users_status[1][1]==0:
                        updatedb.save_relations(following_user_id)
                        updatedb.update_relation_next_cursor(following_user_id, -1)
                        self.connection.commit()
                        last_user_flag=True
                        break
                        
                    else:
                        next_cursor = following_users_status[1][1]
                        updatedb.update_relation_next_cursor(following_user_id, next_cursor)
                        self.connection.commit()

