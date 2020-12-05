import pymongo
import pandas as pds
import expiringdict
import pickle
import pandas as pd
import numpy as np

connection_url = 'mongodb+srv://movie:moviedata1050@movie.4icao.mongodb.net/<dbname>?retryWrites=true&w=majority'
client = pymongo.MongoClient(connection_url)
RESULT_CACHE_EXPIRATION = 15  # seconds


def upsert_movie(df):
    """
    Update MongoDB database `movies` and collection `pop_movies` with the given `DataFrame`.
    """

    db = client.get_database("movies")
    collection = db.get_collection("pop_movies")
    db.pop_movies.remove({})
    for record in df.to_dict('records'):
        result = collection.replace_one(
            filter=record,  # locate the document if exists
            replacement=record,  # latest document
            upsert=True)  # update if exists, insert if not


def fetch_all_movie():
    db = client.get_database("movies")
    collection = db.get_collection("pop_movies")
    ret = list(collection.find())
    return ret


_fetch_all_movies_as_df_cache = expiringdict.ExpiringDict(max_len=1,
                                                          max_age_seconds=RESULT_CACHE_EXPIRATION)


def fetch_all_movies_as_df(allow_cached=False):
    """Converts list of dicts returned by `fetch_all_movie` to DataFrame with ID removed
    Actual job is done in `_worker`. When `allow_cached`, attempt to retrieve timed cached from
    `_fetch_all_movies_as_df_cache`; ignore cache and call `_work` if cache expires or `allow_cached`
    is False.
    """

    def _work():
        data = fetch_all_movie()
        if len(data) == 0:
            return None
        df = pds.DataFrame.from_records(data)
        df.drop('_id', axis=1, inplace=True)
        return df

    if allow_cached:
        try:
            return _fetch_all_movies_as_df_cache['cache']
        except KeyError:
            pass
    ret = _work()
    _fetch_all_movies_as_df_cache['cache'] = ret
    return ret


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def plk_to_dataframe(input_file):
    df_1 = pd.DataFrame(input_file)
    df_dataframe1 = np.transpose(df_1)
    df_dataframe1.columns = ['title', 'year', 'content_rating', 'length', 'genres', 'score', 'metascore',
                             'vote_numbers',
                             'gross', 'director', 'actors', 'genre_overall']
    df_dataframe1['year'] = df_dataframe1['year'].map(lambda x: ''.join([i for i in x if i.isdigit()]))
    df_dataframe1['length'] = [df_dataframe1['length'][i][:-3] for i in range(len(df_dataframe1['length']))]
    df_dataframe1['gross'] = [df_dataframe1['gross'][i][1:-1] for i in range(len(df_dataframe1['gross']))]
    df_dataframe1['content_rating'].replace(to_replace='', value='Not Rated', inplace=True)
    return df_dataframe1


def transform(df):
    df_update = df.reset_index().rename(columns={'index': 'movie_id'})
    return df_update
