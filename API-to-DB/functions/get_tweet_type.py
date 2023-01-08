def get_tweet_type(tweet):
    if 'media' in tweet['entities'].keys() and tweet['is_quote_status'] == False:
        return tweet['extended_entities']['media'][0]['type']

    else:
        return None
