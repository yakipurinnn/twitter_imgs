import pprint
import os
import time
from functions.download_file import download_file

class DownloadPhotos:
    def __init__(self, tweet):
        #tweet_typeはphotoが前提
        self.tweet = tweet
        self.user_id = tweet['user']['id']
        self.screen_name = tweet['user']['screen_name']
        self.photo_url_list = []
        self.photo_path_list = []
        self.photo_count = len(tweet['extended_entities']['media'])

        self.user_photos_path = f'./downloaded_imgs/twitter_photos/{self.user_id}' 

        if 'profile_banner_url' in tweet['user'].keys():
            self.profile_banner_url = tweet['user']['profile_banner_url']
            self.profile_banner_id = tweet['user']['profile_banner_url'].replace(f'https://pbs.twimg.com/profile_banners/{self.user_id}/', '')
            self.user_profile_banners_path = f'./downloaded_imgs/profile_banners/{self.user_id}'
            self.profile_banner_path = f'./downloaded_imgs/profile_banners/{self.user_id}/_{self.profile_banner_id}_.jpg'

        if 'profile_image_url' in tweet['user'].keys():
            self.profile_image_url = tweet['user']['profile_image_url']
            self.profile_image_id = tweet['user']['profile_image_url'].replace(f'http://pbs.twimg.com/profile_images/', '')
            backslash_position =  self.profile_image_id.rfind('/')
            self.profile_image_id = self.profile_image_id[backslash_position+1:]
            self.user_profile_images_path = f'./downloaded_imgs/profile_images/{self.user_id}'
            self.profile_image_path = f'./downloaded_imgs/profile_images/{self.user_id}/{self.profile_image_id}'

        #保存するディレクトリをtwitter_user毎に作成
        try:
            os.makedirs(self.user_photos_path)
            if 'profile_banner_url' in tweet['user'].keys():
                os.makedirs(self.user_profile_banners_path)
            if 'profile_image_url' in tweet['user'].keys():
                os.makedirs(self.user_profile_images_path)
        except FileExistsError:
            # print('    このuserディレクトリは既に作成済みです', self.user_id , self.screen_name)
            pass


        for i in range(self.photo_count):
            photo_id = tweet['extended_entities']['media'][i]['media_url_https'].replace('https://pbs.twimg.com/media/', '')
            photo_url = tweet['extended_entities']['media'][i]['media_url_https'] + '?name=orig'
            photo_path =  f'./downloaded_imgs/twitter_photos/{self.user_id}/{self.screen_name}_{photo_id}'

            self.photo_url_list.append(photo_url)
            self.photo_path_list.append(photo_path)

    def download(self):
        if 'profile_banner_url' in self.tweet['user'].keys():
            if not os.path.exists(self.profile_banner_path):
                download_file(self.profile_banner_url, self.profile_banner_path)

        if 'profile_image_url' in self.tweet['user'].keys():
            if not os.path.exists(self.profile_image_path):
                download_file(self.profile_image_url, self.profile_image_path)

        #tweet画像を保存する場合
        # for i in range(self.photo_count):
        #     photo_url = self.photo_url_list[i]
        #     photo_path = self.photo_path_list[i]

        #     if not os.path.exists(photo_path):
        #         download_file(photo_url, photo_path)
