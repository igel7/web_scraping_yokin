import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# 作業ディレクトリの設定
os.chdir('C:\\Users\\ryasu\\Documents\\GitHub\\web_scraping')
print("Changed Directory:", os.getcwd())

def get_rate(bank_name, url, selector):
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーをチェック
        soup = BeautifulSoup(response.content, 'html.parser')
        target = soup.select_one(selector)
        if target:
            return remove_muda(target.get_text()), False, True  # JS未使用, 取得成功
        else:
            return None, False, False  # JS未使用, 取得失敗
    except Exception as e:
        print(f"Error fetching rate for {bank_name} without JS: {e}")
        return None, False, False  # JS未使用, 取得失敗

def get_rate_js(bank_name, url, selector):
    try:
        options = Options()
        options.headless = False
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        target = soup.select_one(selector)
        driver.quit()
        if target:
            return remove_muda(target.get_text()), True, True  # JS使用, 取得成功
        else:
            return None, True, False  # JS使用, 取得失敗
    except Exception as e:
        print(f"Error fetching rate for {bank_name} with JS: {e}")
        return None, True, False  # JS使用, 取得失敗

def remove_muda(text):
    characters_to_remove = ["%", " ", "年", "％", "　"]
    for char in characters_to_remove:
        text = text.replace(char, "")
    return text

# 銀行リストの読み込み
banks_df = pd.read_csv('banks_list_ok.csv', encoding='SHIFT_JIS')

# 処理する行数と開始行数を設定
start_row = 0  # 開始行数（0-indexed）
num_rows = 170  # 処理する行数
batch_size = 3  # バッチサイズ

# tmpフォルダの作成
tmp_dir = 'tmp'
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

# 結果を格納するDataFrameの作成
results = pd.DataFrame(columns=['date', 'bank_name', 'url', 'selector', 'type', 'pref', 'code', 'interest_rate', 'js', 'success'])

# 指定された範囲の行について処理を行う
for idx, (index, row) in enumerate(banks_df.iloc[start_row:start_row + num_rows].iterrows(), start=start_row + 1):
    bank_name = row['bank_name']
    url = row['url']
    selector = row['selector']
    js = row['js']
    
    if pd.isna(selector) or not selector.strip():
        # セレクターが空欄の場合はスキップ
        rate, js, success = None, None, False
        print(f"[{idx}/{len(banks_df)}] {bank_name}: セレクターが空欄のためスキップ")
    else:
        rate, js, success = get_rate(bank_name, url, selector)
        if success:
            print(f"[{idx}/{len(banks_df)}] {bank_name}: JS未使用で成功")
        else:
            rate, js, success = get_rate_js(bank_name, url, selector)
            if success:
                print(f"[{idx}/{len(banks_df)}] {bank_name}: JS使用で成功")
            else:
                print(f"[{idx}/{len(banks_df)}] {bank_name}: 取得失敗")
    
    # 結果をDataFrameに追加
    result_row = pd.DataFrame([{
        'date': datetime.now().strftime('%Y-%m-%d'),
        'bank_name': bank_name,
        'url': url,
        'selector': selector,
        'type': row['type'],
        'pref': row['pref'],
        'code': row['code'],
        'interest_rate': rate,
        'js': js,
        'success': success
    }])
    results = pd.concat([results, result_row], ignore_index=True)
    
    # バッチごとに一時ファイルに保存
    if idx % batch_size == 0:
        batch_file = os.path.join(tmp_dir, f'batch_{idx // batch_size}.csv')
        results.to_csv(batch_file, index=False)
        print(f"Batch saved to {batch_file}")
        results = pd.DataFrame(columns=['date', 'bank_name', 'url', 'selector', 'type', 'pref', 'code', 'interest_rate', 'js', 'success'])

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

# 必要に応じてCSVに保存する関数
def save_results_to_csv(results, filename='first_check_result2.csv'):
    results.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

# 結果をCSVに保存（この行はコメントアウトしています。実行する場合はコメントを外してください。）
save_results_to_csv(final_df)
