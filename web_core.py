import cfscrape
import time
import json
from random import uniform
from bs4 import BeautifulSoup
from preprocessing import *


def get_movie_detail(movie_url: str,
                     host: str = "https://www.imdb.com",
                     max_iter: int = 100) -> tuple:
    # ['related movies', 'story line', 'reviews']
    s = cfscrape.create_scraper()
    movie_id = process_url_to_key(movie_url)
    movie_detail = []
    m = s.get(host + movie_url)
    soup = BeautifulSoup(m.text, 'lxml')
    rec_m = soup.select('#title_recs > div > div > div > div > div > div > div > span > a')
    if not rec_m:
        movie_detail.append([])
    else:
        movie_detail.append([process_url_to_key(x['href']) for x in rec_m if 'title' in x['href']])

    sl = soup.select('#titleStoryLine > div:nth-child(3) > p > span')
    if not sl:
        movie_detail.append([])
    else:
        movie_detail.append([sl[0].text.strip()])

    rs_gather = []

    review_url = host + "/title/{}/reviews".format(movie_id)
    review_page = s.get(review_url)
    soup = BeautifulSoup(review_page.text, 'lxml')
    if review_page.status_code == '404':
        movie_detail.append([])
        return movie_id, movie_detail

    score = soup.select(
        '#main > section > div.lister > div.lister-list > div > div.review-container > div.lister-item-content > div.ipl-ratings-bar > span > span:nth-child(2)')
    score = [x.text for x in score]
    ns = len(score)

    r_content = soup.select(
        '#main > section > div.lister > div.lister-list > div > div.review-container > div.lister-item-content > div.content > div.text.show-more__control')
    r_content = [x.text for x in r_content]
    nrc = len(r_content)

    r_date = soup.select(
        '#main > section > div.lister > div.lister-list > div > div.review-container > div.lister-item-content > div.display-name-date > span.review-date')
    r_date = [process_time(x.text) for x in r_date]
    nrd = len(r_date)

    r_agree = soup.select(
        '#main > section > div.lister > div.lister-list > div > div.review-container > div.lister-item-content > div.content > div.actions.text-muted')
    r_agree = [[''.join(filter(str.isdigit, x)) for x in k.text.split('out of')] for k in r_agree]
    r_agree = [process_agree(x) for x in r_agree]
    nra = len(r_agree)

    mn = max([ns, nrc, nrd, nra])

    score, r_content, r_date, r_agree = [auto_fill(l, mn) for l in [score, r_content, r_date, r_agree]]
    rs_gather += list(zip(score, r_content, r_date, r_agree))

    dk = soup.select('#main > section > div.lister > div.load-more-data')
    if not dk:
        movie_detail.append(rs_gather)
        return movie_id, movie_detail
    else:
        dk = dk[0].get('data-key')

    if dk:
        i = 0
        while i < max_iter:
            i += 1

            url = host + '/title/{}/reviews/_ajax?ref_=undefined&paginationKey={}'
            url = url.format(movie_id, dk)
            r = s.get(url)

            soup = BeautifulSoup(r.text, 'lxml')
            score = soup.select(
                'body > div > div.lister-list > div > div.review-container > div.lister-item-content > div.ipl-ratings-bar > span > span:nth-child(2)')
            score = [x.text for x in score]
            ns = len(score)
            r_content = soup.select(
                'body > div > div.lister-list > div > div.review-container > div.lister-item-content > div.content > div.text.show-more__control')
            r_content = [x.text for x in r_content]
            nrc = len(r_content)
            r_date = soup.select(
                'body > div > div.lister-list > div > div.review-container > div.lister-item-content > div.display-name-date > span.review-date')
            r_date = [process_time(x.text) for x in r_date]
            nrd = len(r_date)
            r_agree = soup.select(
                'body > div > div.lister-list > div > div.review-container > div.lister-item-content > div.content > div.actions.text-muted')
            r_agree = [[''.join(filter(str.isdigit, x)) for x in k.text.split('out of')] for k in r_agree]
            r_agree = [process_agree(x) for x in r_agree]
            nra = len(r_agree)
            mn = max([ns, nrc, nrd, nra])
            score, r_content, r_date, r_agree = [auto_fill(l, mn) for l in [score, r_content, r_date, r_agree]]
            rs_gather += list(zip(score, r_content, r_date, r_agree))
            dk = soup.select('body > div > div.load-more-data')
            if not dk:
                break
            dk = dk[0].get('data-key')

    movie_detail.append(rs_gather)

    return movie_id, movie_detail


def get_movie_rating_scores(movie_url: str,  # e.g.:
                            host: str = "https://www.imdb.com",
                            max_iter: int = 100):
    # Scraping user rating scores from most recent reviews
    s = cfscrape.create_scraper()
    movie_id = process_url_to_key(movie_url)
    ratings = []
    url = host + '/title/{}/reviews?sort=submissionDate&dir=desc&ratingFilter=0'.format(movie_id)
    m = s.get(url)
    soup = BeautifulSoup(m.text, 'lxml')
    r_date = soup.select(
        '#main > section > div.lister > div.lister-list > div > div.review-container > div.lister-item-content > div.display-name-date > span.review-date')

    if r_date:
        r_date = [x.text for x in r_date]
    else:
        return

    r_score = soup.select(
        '#main > section > div.lister > div.lister-list > div > div.review-container > div.lister-item-content > div.ipl-ratings-bar > span > span:nth-child(2)')

    if r_score:
        r_score = [x.text for x in r_score]
    else:
        return

    r_date, r_score = length_filler(r_date, r_score)

    ratings += list(zip(r_date, r_score))

    dk = soup.select('#main > section > div.lister > div.load-more-data')
    if not dk:
        return movie_id, ratings
    else:
        dk = dk[0].get('data-key')

    if dk:
        i = 0
        while i < max_iter:
            i += 1
            url = host + '/title/{}/reviews/_ajax?sort=submissionDate&dir=desc&ratingFilter=0&ref_=undefined&paginationKey={}'
            url = url.format(movie_id, dk)
            r = s.get(url)
            soup = BeautifulSoup(r.text, 'lxml')
            r_score = soup.select(
                'body > div > div.lister-list > div > div.review-container > div.lister-item-content > div.ipl-ratings-bar > span > span:nth-child(2)')
            r_date = soup.select(
                'body > div > div.lister-list > div > div.review-container > div.lister-item-content > div.display-name-date > span.review-date')
            r_score = [x.text for x in r_score]
            r_date = [x.text for x in r_date]
            rs, rd = length_filler(r_score, r_date)
            ratings += list(zip(rd, rs))
            dk = soup.select('body > div > div.load-more-data')
            if not dk:
                break
            dk = dk[0].get('data-key')
    return ratings


def movie_basic_info_selector(m):
    # get movie name
    # get movie year
    # get movie grade
    # get movie length
    # get movie genre
    # get movie score
    # get movie metascore
    # get movie votes
    # get movie gross
    info = [m.select('h3 > a'), m.select('h3 > span.lister-item-year.text-muted.unbold'),
            m.select('p:nth-child(2) > span.certificate'), m.select('p:nth-child(2) > span.runtime'),
            m.select('p:nth-child(2) > span.genre'), m.select('div > div.inline-block.ratings-imdb-rating > strong'),
            m.select("div > div.inline-block.ratings-metascore > span"),
            m.select('p.sort-num_votes-visible > span:nth-child(2)'),
            m.select('p.sort-num_votes-visible > span:nth-child(5)')]
    info = [x[0].text if x else "" for x in info]

    # get movie director(s) and star(s)
    da_info = m.select('p:nth-child(5)')
    d, a = process_director_actor(da_info)
    info += [d, a]
    return info


class WebUpdater(object):
    def __init__(self):
        self.s = cfscrape.create_scraper()
        print("Web Scraping Updater core initialized.")
        self.host = "https://www.imdb.com"
        self.genres_link = self.get_genres()
        self.genres_name = [x[x.find("=")+1:x.find("&")] for x in self.genres_link]
        self.gl_len = len(self.genres_link)

    def get_genres(self) -> list:
        res = self.s.get("https://www.imdb.com/feature/genre/?ref_=nv_ch_gr")
        soup = BeautifulSoup(res.text, 'lxml')
        genres_href = soup.select(
            "#main > div:nth-child(13) > span > div > div > div > div > div > div > div > div > a")
        genres_link = [self.host + x['href'] for x in genres_href]
        print('Fetched number of Movie Genres {}.'.format(len(genres_link)))
        return genres_link

    def get_all_popular_movie_detail(self,
                                     page_limit=1) -> dict:
        pop_m = {}
        for link, name in zip(self.genres_link, self.genres_name):
            print("Updating Popular Movie Database {} out of {}".format(name, self.gl_len))
            pages = [link]
            for i in range(page_limit):
                res_current = self.s.get(pages[-1])
                soup = BeautifulSoup(res_current.text, 'lxml')
                p = soup.select('#main > div > div.lister.list.detail.sub-list > div > div > div.lister-item-content')
                info = [movie_basic_info_selector(x) + [name] for x in p]
                info = [[process_text(y) for y in x] for x in info]
                movie_link = [x.select('h3 > a')[0]['href'] if x.select('h3 > a') else "" for x in p]
                movie_id = [process_url_to_key(x) for x in movie_link]
                for k, v in zip(movie_id, info):
                    if k in pop_m:
                        continue
                    pop_m[k] = v
                # save_obj(pop_m, "{} movie info.".format(name))
                if i == 0:
                    next_page_href = soup.select("#main > div > div.desc > a")
                else:
                    next_page_href = soup.select("#main > div > div.desc > a.lister-page-next.next-page")

                if not next_page_href:
                    break

                next_page_link = self.host + next_page_href[0]['href']
                pages.append(next_page_link)
                time.sleep(uniform(0, 1.21))
        return pop_m


class WebSearch(object):
    def __init__(self):
        self.s = cfscrape.create_scraper()
        print("Web Scraping core initialized.")
        self.host = "https://www.imdb.com"

    def search(self,
               movie_title: str,
               pl = 100) -> dict:
        result = {}
        if not movie_title:
            movie_title = ''
        else:
            movie_title = movie_title.strip().replace(' ', '+')
        search_query = self.host + '/search/title/?title={}&title_type=feature,documentary,short'
        search_query = search_query.format(movie_title)
        page = self.s.get(search_query)
        soup = BeautifulSoup(page.text, 'lxml')
        m = soup.select('#main > div > div.lister.list.detail.sub-list > div > div > div.lister-item-content')
        if not m:
            print('Nothing Found')
            return {}
        m = m[0]
        info = movie_basic_info_selector(m)
        info = [process_text(y) for y in info]
        movie_link = soup.select('h3 > a')[0]['href'] if soup.select('h3 > a') else ""
        movie_id = process_url_to_key(movie_link)
        _, d_info = get_movie_detail(movie_link, max_iter=pl)
        result[movie_id] = info + d_info
        return result
