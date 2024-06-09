import pandas as pd
import os
import requests
from urllib.parse import urlparse
from datetime import datetime


def check_robots_txt(url):
    """
    指定されたURLのrobots.txtをチェックし、クロールが許可されているかどうかを判断する。
    """
    try:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        response = requests.get(robots_url)
        if response.status_code == 200:
            if 'Disallow' in response.text:
                disallow_paths = [line.split(': ')[1] for line in response.text.split('\n') if line.startswith('Disallow')]
                for path in disallow_paths:
                    if parsed_url.path.startswith(path):
                        return robots_url, False
            return robots_url, True
        else:
            return robots_url, "No robots.txt"
    except Exception as e:
        print(f"Error fetching robots.txt for {url}: {e}")
        return None, "Error"

# 作業ディレクトリの設定
os.chdir('C:\\Users\\ryasu\\Documents\\GitHub\\web_scraping')

# 銀行リストの読み込み
banks_df = pd.read_csv('first_check_result.csv')

# 処理する行数と開始行数を設定
start_row = 0  # 開始行数（0-indexed）
num_rows = 384  # 処理する行数
batch_size = 3  # バッチサイズ

# tmpフォルダの作成
tmp_dir = 'tmp'
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

# 結果を格納するDataFrameの作成
results = pd.DataFrame(columns=['bank_name', 'url', 'robots_txt_url', 'crawl_status'])

# 指定された範囲の行について処理を行う
for idx, (index, row) in enumerate(banks_df.iloc[start_row:start_row + num_rows].iterrows(), start=start_row + 1):
    bank_name = row['bank_name']
    url = row['url']
    
    # robots.txtのチェック
    robots_txt_url, status = check_robots_txt(url)
    
    # 結果をDataFrameに追加
    result_row = pd.DataFrame([{
        'bank_name': bank_name,
        'url': url,
        'robots_txt_url': robots_txt_url,
        'crawl_status': status
    }])
    results = pd.concat([results, result_row], ignore_index=True)
    
    # コンソールに進行状況を出力
    print(f"Processing {idx}/{len(banks_df)}: {bank_name} - {'Crawl allowed' if status else 'Crawl disallowed' if status is False else status}")

    # バッチごとに一時ファイルに保存
    if idx % batch_size == 0:
        batch_file = os.path.join(tmp_dir, f'batch_{idx // batch_size}.csv')
        results.to_csv(batch_file, index=False)
        print(f"Batch saved to {batch_file}")
        results = pd.DataFrame(columns=['bank_name', 'url', 'robots_txt_url', 'crawl_status'])

# 残りの結果を保存
if not results.empty:
    batch_file = os.path.join(tmp_dir, f'batch_{(idx // batch_size) + 1}.csv')
    results.to_csv(batch_file, index=False)
    print(f"Batch saved to {batch_file}")

# 一時ファイルを結合
all_batches = []
for batch_file in sorted(os.listdir(tmp_dir)):
    if batch_file.endswith('.csv'):
        batch_df = pd.read_csv(os.path.join(tmp_dir, batch_file))
        all_batches.append(batch_df)

final_df = pd.concat(all_batches, ignore_index=True)

# 結果を表示
print(final_df)

# 最終結果をCSVに保存
final_csv = 'robot_kakunin.csv'
final_df.to_csv(final_csv, index=False)
print(f"Final results saved to {final_csv}")
