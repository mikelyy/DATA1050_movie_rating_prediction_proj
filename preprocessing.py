# Code contributed and debugged by Bangxi Xiao
import pickle

date_dict = {'January': '01',
             'February': '02',
             'March': '03',
             'April': '04',
             'May': '05',
             'June': '06',
             'July': '07',
             'August': '08',
             'September': '09',
             'October': '10',
             'November': '11',
             'December': '12'}


def process_director_actor(s):
    if not s:
        return '', ''

    s = s[0].text
    s = s.replace('\n', '')

    if "Director" in s and ("Stars:" in s or "Star:" in s ):
        s = s.replace('Directors:', '').replace('Director:', '')
        s = s.replace('Stars:', '').replace('Star:', '')
        s = s.split('|')
        s = [x.strip() if x else '' for x in s]
    elif "Director" in s and ("Star:" not in s or "Stars" not in s):
        s = s.replace('Directors:', '').replace('Director:', '')
        s = [s.strip(), '']
    elif "Director" not in s and ("Stars:" in s or "Star:" in s):
        s = s.replace('Stars:', '').replace('Star:', '')
        s = ['', s.strip()]
    else:
        s = ['', '']
    return s


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def process_url_to_key(url):
    url = url.replace('/title/', '')
    pos = url.find('/')
    id = url[0:pos]
    return id


def process_text(s):
    s = s.replace('\n', '')
    s = s.strip()
    return s


def process_time(s):
    d, m, y = s.split(' ')
    d = '0'+d if len(d) == 1 else d
    m = date_dict[m]
    return y + m + d


def length_filler(l1, l2):
    return (l1, l2+[l2[-1] for _ in range(len(l1)-len(l2))]) if len(l1) >= len(l2) else (l1+[l1[-1] for _ in range(len(l2)-len(l1))], l2)


def process_agree(l):
    try:
        r = int(l[0]) / int(l[1])
    except:
        r = 0.5
    return r


def auto_fill(l, length):
    return l + [l[-1] for _ in range(length-len(l))]

