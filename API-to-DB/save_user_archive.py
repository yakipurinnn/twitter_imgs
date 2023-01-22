import json
import time
import pprint
import datetime
import subprocess
import os
import MySQLdb
from MySQLdb import IntegrityError
from functions.to_JST_time import to_JST_time
from functions.open_json import open_json


if __name__ == '__main__':
    cwd = subprocess.run('find /home/ -name twitter_imgs -type d', encoding='utf8', shell=True, capture_output=True, text=True)
    os.chdir(cwd.stdout.replace('\n', ''))    #pathの改行コードを削除

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

    max_user_id=0
    for i in range(10000):
        cursor.execute(f"""INSERT INTO twitter_user_archives (twitter_user_archives.user_id, twitter_user_archives.user_api_archive) SELECT twitter_users.user_id, twitter_users.user_api_archive FROM twitter_users WHERE twitter_users.user_id>{max_user_id} ORDER BY twitter_users.user_id LIMIT 1000;""")
        cursor.execute(f"""SELECT twitter_users.user_id, twitter_users.user_api_archive FROM twitter_users WHERE twitter_users.user_id>{max_user_id} ORDER BY twitter_users.user_id LIMIT 1000""")
        selected_records = cursor.fetchall()
        max_user_id=selected_records[len(selected_records)-1][0]

        print(i, len(selected_records), selected_records[0][0], max_user_id)

        connection.commit()

        if len(selected_records)<1000:
            break
