import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import chromedriver_binary  # adds chromedriver to PATH
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Wayback CDX API endpoint
CDX_BASE = 'http://web.archive.org/cdx/search/cdx'
TARGETS = {
    'index2': 'http://www.nihonkokumin.com/index2.html',
    'bbs': 'http://www2u.biglobe.ne.jp/~y05k/kokumin/bbs/ansq1.cgi'
}

OUTPUT_DIR = 'kokumin bbs'
README_FILE = os.path.join(OUTPUT_DIR, 'README.md')

# フォルダ作成
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Selenium headless Chrome 設定
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)
all_entries = []

for name, url in TARGETS.items():
    # Wayback CDX API からキャプチャ一覧を取得
    params = {'url': url, 'output': 'json', 'fl': 'timestamp,original'}
    resp = requests.get(CDX_BASE, params=params)
    captures = resp.json()[1:]

    for ts, orig in captures:
        snap_url = f'https://web.archive.org/web/{ts}id_/{orig}'
        driver.get(snap_url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        if name == 'bbs':
            # <div align="right"> の直後のメッセージを抽出
            for div in soup.find_all('div', align='right'):
                nxt_text = div.find_next_sibling(text=True)
                if nxt_text:
                    text = nxt_text.strip()
                else:
                    nxt_tag = div.find_next_sibling()
                    text = nxt_tag.get_text(strip=True) if nxt_tag else ''
                date = datetime.strptime(ts, '%Y%m%d%H%M%S')
                all_entries.append((date.isoformat(), text, snap_url))
        else:
            # index2 ページは本文全テキストを結合
            body = soup.body
            text = ' '.join(body.stripped_strings)
            date = datetime.strptime(ts, '%Y%m%d%H%M%S')
            all_entries.append((date.isoformat(), text, snap_url))

# Selenium ドライバ終了
driver.quit()

# 日付でソートし README.md を生成
all_entries.sort(key=lambda x: x[0])
with open(README_FILE, 'w', encoding='utf-8') as f:
    f.write('# kokumin bbs captures\n\n')
    for date, msg, url in all_entries:
        f.write(f'- **{date}**: {msg}  \n  (_source_: {url})\n')

print(f'Wrote {len(all_entries)} entries to {README_FILE}')
