import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# 作業ディレクトリの設定
target_dir = r"C:\Users\ryasu\Documents\GitHub\web_scraping_yokin"
os.chdir(target_dir)
print(f"Current working directory: {os.getcwd()}")

# CSVファイルの読み込み
input_csv = 'banks_output.csv'  # 入力CSVファイルの名前
banks_df = pd.read_csv(input_csv)

# グローバル変数としてdriverを宣言
driver = webdriver.Chrome(options=options)

# セットアップ
options = Options()
options.headless = False  # ヘッドレスモードをオフにする（ブラウザを表示する）

# URLを10個ずつ開く関数
def open_urls_in_batches(urls, batch_size=10):
    global driver
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        for url in batch:
            driver.execute_script(f'window.open("{url}", "_blank");')
            time.sleep(1)  # 少し待機して次のURLを開く
        print(f"Opened batch {i // batch_size + 1}")
        input("Press Enter to close this batch and open the next one...")  # 次のバッチを開く前にEnterキーを待つ
        driver.quit()
        driver = webdriver.Chrome(options=options)  # 新しいブラウザウィンドウを開く

# URLのリストを取得
urls = banks_df['url'].dropna().tolist()  # NaN値（URLが取得できなかった行）を除外する

# URLを10個ずつ開く
open_urls_in_batches(urls, batch_size=10)

# 最後にドライバを閉じる
driver.quit()