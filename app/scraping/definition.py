#各サイトへのスクレイピング関数の定義
def parse_item_from_twitter(key, driver):
  try:
    WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.TAG_NAME, 'article')))
  except TimeoutException as te:
    print('timeout or no hits')
    return []
  
  res = {}
  before_num = -1
  after_num = 0
  check_count = 0
  while before_num != after_num or check_count < 3:
    if len(res) > max_find_num:
      break
    if before_num == after_num:
      check_count += 1
    else:
      check_count = 0
    before_num = after_num
    articles = driver.find_elements(By.TAG_NAME, 'article')
    print(str(len(articles)) + ' found')
    for article in articles[:4]:
      sleep(0.1)
      line = [key]
      if len(article.find_elements(By.TAG_NAME, 'a')) < 2:
        #センシティブなコンテンツ
        continue
      url = article.find_elements(By.TAG_NAME, 'a')[2].get_attribute('href')
      #収集済み
      if url in res:
        print('already got.')
        continue
      #本文
      text = remove_emoji(article.text)
      line.append(text)
      #日時
      time = article.find_elements(By.TAG_NAME, 'time')
      #広告は日時がない
      if not time:
        continue
      line.append(time[0].get_attribute('datetime'))

      #いいね
      like_tag = article.find_element(By.CLASS_NAME, 'r-1mdbhws').get_attribute('aria-label')
      if like_tag is not None:
        like_dict = { kv.split(' ')[1]:kv.split(' ')[0] for kv in like_tag.split(', ')}

        if 'likes' in like_dict:
          line.append(like_dict['likes'])
        elif 'like' in like_dict:
          line.append(like_dict['like'])
        else:
          line.append('')

        if 'replies' in like_dict:
          line.append(like_dict['replies'])
        elif 'reply' in like_dict:
          line.append(like_dict['reply'])
        else:
          line.append('')

        if 'Retweets' in like_dict:
          line.append(like_dict['Retweets'])
        elif 'Retweet' in like_dict:
          line.append(like_dict['Retweet'])
        else:
          line.append('')
        #テキスト末尾から不要箇所を削除する
        line[1] = re.sub('\n[0-9]+','',line[1])
      else:
        line.extend(['','',''])
      like_tag = None
      line.append(url)
      print(line)
      res[url] = line
    #ActionChains(driver).move_to_element(articles[min(len(articles)-1, 5)]).perform()
    for i in range(5):
      ActionChains(driver).key_down('j').perform()
      sleep(0.1)
      ActionChains(driver).key_up('j').perform()
    sleep(0.5)
    after_num = len(res)
  
  print(res.keys())
  #コメントのある記事は取得しにいく
  for url, line in res.items():
    try:
      if not line[4] ==''  and int(line[4]) > 0:
        driver.get(url)
        print(url)
        #ここでのTimeout発生は無視する
        try:
          WebDriverWait(driver, 2).until(expected_conditions.visibility_of_element_located((By.TAG_NAME, 'article')))
        except TimeoutException as e:
          print('Timeout occured skip to move')
          continue
        replies = driver.find_elements(By.TAG_NAME, 'article')
        for i, reply in enumerate(replies):
          #１件目は本文
          if i==0:
            continue
          line[1] = line[1] + '\n\n' + re.sub('\n[0-9]+','',remove_emoji(reply.text))
        print('comments added: ' + str(line))
    except Exception as e:
      print('comment skip')
  return res.values()

def parse_item_from_pinterest(key, driver):
  try:
    WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'vbI')))
  except TimeoutException as te:
    print('timeout or no hits')
    return []
  grid = driver.find_elements(By.CLASS_NAME, 'vbI')

  before_num = -1
  after_num = 0
  urls_dict = {}
  while not before_num == after_num and len(urls_dict) < max_find_num:
    before_num = after_num
    a_tags = grid[0].find_elements(By.TAG_NAME, 'a')
    for a in a_tags:
      #パターンにマッチしなければgetしない
      url = a.get_attribute('href')
      if  not re.fullmatch(r'https://www.pinterest.jp/pin/[0-9]+/', url):
        continue
      urls_dict[url] = ''
    ActionChains(driver).move_to_element(a_tags[len(a_tags)-1]).perform()
    sleep(1)
    after_num = len(urls_dict)

  table = []
  for url in urls_dict.keys():
    line = [key]
    driver.get(url)
    WebDriverWait(driver, 30).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'TwP')))
    article = driver.find_element(By.CLASS_NAME, 'TwP')
    #本文
    text = remove_emoji(article.text)
    #不要な文字列を削除する
    for del_str in ['\n写真', '\nコメント', '\nこのピンを試しましたか？', '\n写真を投稿して感想を伝えましょう！', '\n写真を追加','を投稿して感想を伝えましょう！を追加']:
      text = re.sub(del_str,'',text)
    line.append(text)
    line.append(url)
    print(url)
    #コメント
    try:
      comment_tab = driver.find_element(By.XPATH, "//div[@data-test-id='tab-1']")
      print(comment_tab.text)
      if len(comment_tab.text.split('：')) ==2:
        ActionChains(driver).move_to_element(comment_tab).click()
        sleep(0.1)
        comments = driver.find_elements(By.XPATH, "//div[@data-test-id='canonical-comment']")
        for comment in comments:
          print(comment.get_attribute("textContent"))
          line[1] = line[1] + '\n\n' + remove_emoji(comment.get_attribute("textContent"))
    except NoSuchElementException as e:
      print('No tabs')
    table.append(line)
    print(line)
  return table

def parse_item_from_instagram(key, driver):
  try:
    WebDriverWait(driver, 5).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'MWDvN')))
  except TimeoutException as te:
    print('timeout or no hits')
    return []
  sleep(0.5)

  res = {}

  WebDriverWait(driver, 5).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'v1Nh3')))
  article = driver.find_element(By.CLASS_NAME, 'v1Nh3').find_element(By.TAG_NAME, 'a')
  print('article='+article.get_attribute('href'))
  article.click()
  
  last_len = -1
  while len(res) < max_find_num and last_len != len(res):
    last_len = len(res)
    print(driver.current_url)
    line = [key]
    try:
      WebDriverWait(driver, 30).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'eo2As')))
    except Exception as e:
      continue
    #本文
    text = driver.find_element(By.CLASS_NAME, 'eo2As').text
    if 'likes' in text:
      line.append(remove_emoji(text.split(' likes')[1]))
    else:
      line.append(remove_emoji(text))
    #日時
    div = driver.find_element(By.CLASS_NAME, 'k_Q0X')
    time = div.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
    line.append(time)
    #いいね
    if 'likes' in text:
      iine = text.split(' likes')[0]
    else:
      iine = ''
    line.append(iine)
    url = driver.current_url
    line.append(url)
    print(line)
    if url in res:
      break
    
    res[url] = line
    ActionChains(driver).move_to_element(article).key_down(Keys.RIGHT).perform()
    sleep(1)
    ActionChains(driver).move_to_element(article).key_up(Keys.RIGHT).perform()
      
  return res.values()
  

def get_items(base_url, key_word, parser, driver):
  cnt_limit = 3
  cnt = 0
  table = []
  while cnt < cnt_limit:
    try:
      cnt += 1
      if 'twitter' in base_url:
        driver = webdriver.Chrome('chromedriver',options=options)
      res = driver.get(base_url % key_word)
      print(driver.current_url)
      table = parser(key_word, driver)
      break
    except Exception as e:
      type_, value, traceback_ = sys.exc_info()
      error = traceback.format_exception(type_, value, traceback_)
      for es in error:
        print(es)
      print('retry %i' % cnt)
      sleep(10)
      if cnt >= cnt_limit:
        print('aborted... go to next word')
  return table

def login_pinterest(driver, login_url, user, password):
  driver.get(login_url)
  print('login_pinterest get')
  #ログインボタンフォームを開く
  WebDriverWait(driver, 30).until(expected_conditions.visibility_of_element_located((By.TAG_NAME, 'button')))
  driver.find_element(By.XPATH, '//*[@id="__PWS_ROOT__"]/div[1]/div/div/div/div[3]/div[1]/div[1]/div[2]/div[1]/button').click()
  print('login_pinterest form')
  #メールアドレスとパスワードを入力
  WebDriverWait(driver, 30).until(expected_conditions.visibility_of_element_located((By.TAG_NAME, 'input')))
  driver.find_elements(By.TAG_NAME, 'input')[0].send_keys(user)
  sleep(random.random() + 0.5)
  driver.find_elements(By.TAG_NAME, 'input')[1].send_keys(password)
  sleep(random.random() + 0.5)
  print('login_pinterest mail')
  #ログインボタンを押す
  driver.find_element(By.CLASS_NAME, 'SignupButton').click()
  print('login_pinterest login')
  sleep(1)
  print(driver.current_url)

def login_instagram(driver, login_url, user, password):
  driver.get(login_url)
  print('login_instagram get')
  #ログインボタンフォームを開く
  WebDriverWait(driver, 30).until(expected_conditions.visibility_of_element_located((By.TAG_NAME, 'input')))
  #メールアドレスとパスワードを入力
  driver.find_elements(By.TAG_NAME, 'input')[0].send_keys(user)
  sleep(random.random() + 0.5)
  driver.find_elements(By.TAG_NAME, 'input')[1].send_keys(password)
  sleep(random.random() + 0.5)
  print('login_instagram mail')
  #ログインボタンを押す
  driver.find_element(By.XPATH, '//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[4]/button').click()
  print('login_instagram login')
  sleep(3)
  print(driver.current_url)

def remove_emoji(src_str):
    return ''.join(c for c in src_str if c not in emoji.UNICODE_EMOJI)