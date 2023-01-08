import datetime
from dateutil import tz

def to_JST_time(api_time):
    """
    twitter_apiで取得した時間を引数にとる
    """
    JST = tz.gettz('Asia/Tokyo')
    jst_time = datetime.datetime.strptime(api_time, "%a %b %d %H:%M:%S %z %Y")
    jst_time = jst_time.astimezone(JST).replace(tzinfo=None)

    return jst_time