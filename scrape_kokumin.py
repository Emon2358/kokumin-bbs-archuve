#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 出力先フォルダとREADMEパス
OUTPUT_DIR = 'kokumin bbs'
README_PATH = os.path.join(OUTPUT_DIR, 'README.md')

# Wayback Machine CDX API
CDX_ENDPOINT = 'http://web.archive.org/cdx/search/cdx'
TARGET_URLS = {
    'index2': 'http://www.nihonkokumin.com/index2.html',
    'bbs': 'http://www2u.biglobe.ne.jp/~y05k/kokumin/bbs/ansq1.cgi'
}

# 出力フォルダ準備
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Selenium: ヘッドレスChrome設定
ochrome_opts = Options()
ochrome_opts.add_argument('--headless')
ochrome_opts.add_argument('--no-sandbox')
ochrome_opts.add_argument('--disable-dev-shm-usage')
ochrome_opts.add_argument('--disable-gpu')
ochrome_opts.binary_location = '/usr/bin/chromium-browser'

driver = webdriver.Chrome(
    ChromeDriverManager().install(), 
    options=chrome_opts
)

entries = []

try:
    for name, url in TARGET_URLS.items():
        # CDX API からタイムスタンプ一覧を取得
        params = {'url': url, 'output': 'json', 'fl': 'timestamp,original'}
        res = requests.get(CDX_ENDPOINT, params=params, timeout=30)
        res.raise_for_status()
        captures = res.json()[1:]

        for ts, orig in captures:
print(f'[INFO] {len(entries)} 件を {README_PATH} に書き込みました')
