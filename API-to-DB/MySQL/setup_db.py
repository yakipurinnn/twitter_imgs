import pprint
import MySQLdb
import sys
from functions.open_json import open_json

    #MySQLに接続
db_config_path = './API-to-DB/config/db_config.json'
db_config = open_json(db_config_path)

connection = MySQLdb.connect(
    host = db_config['host'],
    user = db_config['user'],
    passwd = db_config['passwd'],
    charset = db_config['charset'])
cursor = connection.cursor()

cursor.execute("""CREATE DATABASE IF NOT EXISTS twitter_stats""")

connection = MySQLdb.connect(
    host = db_config['host'],
    user = db_config['user'],
    passwd = db_config['passwd'],
    db = db_config['db'],
    charset = db_config['charset'])
cursor = connection.cursor()

# テーブルの作成
cursor.execute("""CREATE TABLE IF NOT EXISTS tweets(
    tweet_id BIGINT UNSIGNED PRIMARY KEY, 
    created_at DATETIME,
    tweet_url VARCHAR(96),
    favorite_count INT,
    retweet_count INT,
    statuses_count INT,
    tweet_text TEXT,
    user_id BIGINT UNSIGNED,
    favorited BOOLEAN,
    retweeted BOOLEAN,
    possibly_sensitive BOOLEAN,
    lang VARCHAR(8),
    is_quote_status BOOLEAN,
    quoted_tweet_id BIGINT UNSIGNED,
    in_reply_to_user_id BIGINT UNSIGNED,
    in_reply_to_status_id BIGINT UNSIGNED,
    photo_count INT DEFAULT(0), 
    tweet_type TEXT,
    deleted BOOLEAN,
    update_time DATETIME DEFAULT(CURRENT_TIMESTAMP),
    api_archive TEXT
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS photos(
    photo_id VARCHAR(64) PRIMARY KEY, 
    photo_url VARCHAR (96),
    photo_path VARCHAR(96),
    ext_alt_text TEXT,
    backup BOOLEAN DEFAULT(0),
    tweet_id BIGINT UNSIGNED
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS twitter_users(
    user_id BIGINT UNSIGNED PRIMARY KEY, 
    name TEXT ,
    screen_name VARCHAR(32),
    user_url VARCHAR(96),
    user_created_at DATETIME,
    description TEXT,
    followers_count INT,
    friends_count INT,
    statuses_count INT,
    favourites_count INT,
    following BOOLEAN,
    location TEXT,
    verified BOOLEAN,
    profile_banner_url VARCHAR(96),
    profile_banner_path VARCHAR(96),
    profile_image_url VARCHAR(96),
    profile_image_path VARCHAR(96),
    deleted BOOLEAN,
    update_time DATETIME DEFAULT(CURRENT_TIMESTAMP),
    user_api_archive TEXT
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS user_relations(
    following BIGINT UNSIGNED,
    followed BIGINT UNSIGNED,
    update_time DATETIME DEFAULT(CURRENT_TIMESTAMP),
    PRIMARY KEY(following, followed)
    )""")

#tweetとhashtagの中間テーブル
cursor.execute("""CREATE TABLE IF NOT EXISTS tweet_hashtag(
    tweet_hashtag_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tweet_id BIGINT UNSIGNED,
    hashtag_id BIGINT UNSIGNED
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS hashtags(
    hashtag_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    hashtag text
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS retweets(
    retweet_id BIGINT UNSIGNED PRIMARY KEY,
    retweeted_at DATETIME,
    user_id BIGINT UNSIGNED,
    retweeted_id BIGINT UNSIGNED
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS favorite_relations(
    user_id BIGINT UNSIGNED,
    favorited_tweet_id BIGINT UNSIGNED,
    PRIMARY KEY(user_id, favorited_tweet_id)
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS save_users(
    user_id BIGINT UNSIGNED PRIMARY KEY,
    tweets_saved_flag INT DEFAULT(0), 
    tweets_update_time DATETIME DEFAULT(CURRENT_TIMESTAMP),
    favorite_saved_flag INT DEFAULT(0), 
    favorite_update_time DATETIME DEFAULT(CURRENT_TIMESTAMP),
    relation_saved_flag INT DEFAULT(0), 
    relation_next_cursor BIGINT DEFAULT(-1),
    relation_update_time DATETIME DEFAULT(CURRENT_TIMESTAMP)
    )""")

cursor.execute("""CREATE TRIGGER IF NOT EXISTS user_id_to_save_users 
    AFTER INSERT ON twitter_users FOR EACH ROW 
    INSERT INTO save_users(user_id) VALUES(new.user_id)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS tweet_archives(
    tweet_id BIGINT UNSIGNED PRIMARY KEY,
    tweet_api_archive TEXT 
    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS twitter_user_archives(
    user_id BIGINT UNSIGNED PRIMARY KEY,
    user_api_archive TEXT 
    )""")
#インデックス作成
# cursor.execute("""DROP tweet_id_index on tweets""")

# cursor.execute("""ALTER TABLE tweet_hashtag AUTO_INCREMENT = 1""")
# cursor.execute("""ALTER TABLE hashtags AUTO_INCREMENT = 1""")

connection.commit()
connection.close()