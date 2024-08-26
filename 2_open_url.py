import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# set working directory
target_dir = r"your working directory"
os.chdir(target_dir)
print(f"Current working directory: {os.getcwd()}")

# import CSV file
input_csv = 'banks_output.csv'  # 入力CSVファイルの名前
banks_df = pd.read_csv(input_csv)

# driver as global variant
driver = webdriver.Chrome(options=options)

# setup
options = Options()
options.headless = False  # ヘッドレスモードをオフにする（ブラウザを表示する）

# open URL 10 by 10
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

# import URL list
urls = banks_df['url'].dropna().tolist()  # NaN値（URLが取得できなかった行）を除外する

# open 10 URLs at once
open_urls_in_batches(urls, batch_size=10)

# quit browser at last
driver.quit()