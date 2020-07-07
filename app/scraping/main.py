#実行
twitter_base_url = 'https://twitter.com/search?q=%s'
instagram_base_url = 'https://www.instagram.com/explore/tags/%s/'
pinterest_base_url = 'https://www.pinterest.jp/search/pins/?q=%s&rs=rs'

max_find_num = 10000

import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

PINTEREST_USERNAME = os.environ.get("PINTEREST_USERNAME")
PINTEREST_PASSWORD = os.environ.get("PINTEREST_PASSWORD")

INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")

h_twitter = ['key', 'text', 'time', 'like_num', 'reply_num', 'retweet_num', 'url']
h_instagram = ['key', 'text', 'time', 'like_num', 'url']
h_pinterest = ['key', 'text', 'url']

#ヘッダーの書き込み
def write_header(filename, header):
    with open(DIR + filename,  'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)

#スクレピング結果の追記
def scrape_and_write(filename, url, key, parser, is_login):
    with open(DIR + filename,  'a') as f:
        writer = csv.writer(f)
        table = get_items(url, key, parser, is_login)
        writer.writerows(table)

ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
f_twitter = '%stwitter.csv' % ts
f_instagram = '%sinstagram.csv' % ts
f_pinterest = '%spinterest.csv' % ts

write_header(f_twitter, h_twitter)
write_header(f_instagram, h_instagram)
write_header(f_pinterest, h_pinterest)

driver = webdriver.Chrome('chromedriver',options=options)
login_pinterest(driver, 'https://www.pinterest.jp/', pinterest_username, pinterest_password)
login_instagram(driver, 'https://www.instagram.com/', instagram_username, instagram_password)

for i, key in tqdm(enumerate(key_df['Name'].values)):
    print(key)
    scrape_and_write(f_twitter, twitter_base_url, key, parse_item_from_twitter, driver)
    scrape_and_write(f_instagram, instagram_base_url, key, parse_item_from_instagram, driver)
    scrape_and_write(f_pinterest, pinterest_base_url, key, parse_item_from_pinterest, driver)