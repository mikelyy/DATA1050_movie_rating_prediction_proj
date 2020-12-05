import web_core
import database_core


if __name__ == '__main__':
    wu = web_core.WebUpdater()
    pm = wu.get_all_popular_movie_detail(page_limit=50)
    df_result = database_core.plk_to_dataframe(pm)
    df_update = database_core.transform(df_result)
    df_update1 = df_update[:10]
    df_update2 = df_update[11:20]
    database_core.upsert_movie(df_update1)
    database_core.fetch_all_movie()
    database_core.fetch_all_movies_as_df(allow_cached=False)
    database_core.upsert_movie(df_update2)
    database_core.fetch_all_movie()
    database_core.fetch_all_movies_as_df(allow_cached=False)
