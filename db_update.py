import web_core
import database_core
import pymongo


if __name__ == '__main__':
    connection_url = 'mongodb+srv://movie:moviedata1050@movie.4icao.mongodb.net/<dbname>?retryWrites=true&w=majority'
    client = pymongo.MongoClient(connection_url)
    RESULT_CACHE_EXPIRATION = 15  # seconds
    wu = web_core.WebUpdater()
    pm = wu.get_all_popular_movie_detail(page_limit=10)
    df_result = database_core.plk_to_dataframe(pm)
    df_update = database_core.transform(df_result)
    database_core.upsert_movie(df_update)
    database_core.fetch_all_movie()
    database_core.fetch_all_movies_as_df(allow_cached=False)
