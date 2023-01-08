import urllib
import http
import time

def download_file(url, dst_path):
    count = 0
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)
    except http.client.IncompleteRead:
        count += 1
        time.sleep(1)
        if count < 5:
            download_file(url, dst_path)

    except FileNotFoundError as e:
        print(type(e), e, 'ダウンロード先ファイルが見つからなかったためスキップします')

    except urllib.error.URLError as e:    #banner_urlなどがapiから取得できた場合でもurlが存在しない場合がまれにある
        print(type(e), e)