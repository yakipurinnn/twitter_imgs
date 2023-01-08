from update_db import UpdateDB
import os
import subprocess
import shutil
import MySQLdb
from functions.open_json import open_json


def delete_user(cursor, user_id):
    cursor.execute(f'DELETE FROM photos WHERE photos.tweet_id=(SELECT tweet_id FROM tweets WHERE tweets.user_id = {user_id})')
    cursor.execute(f'DELETE FROM tweet_hashtag WHERE tweet_hashtag.tweet_id=(SELECT tweet_id FROM tweets WHERE tweets.user_id = {user_id})')
    cursor.execute(f'DELETE FROM tweets WHERE user_id = {user_id}')
    cursor.execute(f'DELETE FROM save_users where user_id = {user_id}')
    cursor.execute(f'DELETE FROM twitter_users where user_id = {user_id}')
    delete_user_directory(user_id)

def delete_user_directory(user_id):
    cwd = subprocess.run('find /home/ -name twitter_imgs -type d', encoding='utf8', shell=True, capture_output=True, text=True)
    os.chdir(cwd.stdout.replace('\n', ''))    #pathの改行コードを削除
    if os.path.exists(f'./downloaded_imgs/profile_images/{user_id}/'):
        shutil.rmtree(f'./downloaded_imgs/profile_images/{user_id}/')

    if os.path.exists(f'./downloaded_imgs/profile_bunners/{user_id}/'):
        shutil.rmtree(f'./downloaded_imgs/profile_bunners/{user_id}/')

    if os.path.exists(f'./downloaded_imgs/twitter_photos/{user_id}/'):
        shutil.rmtree(f'./downloaded_imgs/twitter_photos/{user_id}/')


if __name__ == '__main__':
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

    user_id = 253085057

    delete_user(cursor, user_id)

    connection.commit()
    connection.close()
