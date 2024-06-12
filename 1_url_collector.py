import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# 作業ディレクトリを設定
target_dir = r"C:\Users\ryasu\Documents\GitHub\web_scraping_yokin"
os.chdir(target_dir)
print(f"Current working directory: {os.getcwd()}")

# CSVファイルの読み込み
input_csv = 'banks_list.csv'  # 入力CSVファイルの名前
output_csv = 'banks_output.csv'  # 出力CSVファイルの名前
tmp_dir = os.path.join(target_dir, 'tmp')

# 一時フォルダを作成
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

banks_df = pd.read_csv(input_csv, encoding='SHIFT_JIS')

# セットアップ
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# 検索してURLを取得する関数
def fetch_url(bank_name):
    try:
        driver.get('https://www.google.com')
        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(f"{bank_name} 普通預金金利")
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(2)  # 検索結果が表示されるまでの待機

        # 検索結果から最初の結果をクリック
        results = driver.find_elements(By.CSS_SELECTOR, 'h3')
        if results:
            results[0].click()
            time.sleep(2)  # ページがロードされるまでの待機

            # URLを取得
            return driver.current_url
    except Exception as e:
        print(f"Error fetching URL for {bank_name}: {e}")
        return None

# 各銀行名に対してURLを取得
urls = []
batch_size = 5
for index, row in banks_df.iterrows():
    bank_name = row['bank_name']
    url = fetch_url(bank_name)
    urls.append(url)
    
    # 現在の進捗を表示
    print(f"{index + 1}/{len(banks_df)}: {bank_name} の URL: {url}")
    
    # バッチごとに一時ファイルに保存
    if (index + 1) % batch_size == 0 or (index + 1) == len(banks_df):
        batch_df = banks_df.iloc[index - (index % batch_size):index + 1]
        batch_df['url'] = urls[-batch_df.shape[0]:]
        batch_file = os.path.join(tmp_dir, f'batch_{index // batch_size}.csv')
        batch_df.to_csv(batch_file, index=False)
        print(f"Batch saved to {batch_file}")

# ブラウザを閉じる
driver.quit()

# 一時ファイルを結合
all_batches = []
for batch_file in sorted(os.listdir(tmp_dir)):
    if batch_file.endswith('.csv'):
        batch_df = pd.read_csv(os.path.join(tmp_dir, batch_file))
        all_batches.append(batch_df)

final_df = pd.concat(all_batches, ignore_index=True)
final_df.to_csv(output_csv, index=False)

print(f"All batches combined and saved to {output_csv}")
