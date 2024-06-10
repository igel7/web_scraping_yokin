import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import openpyxl
import re
import os

# 作業ディレクトリを設定
target_dir = r"C:\Users\ryasu\Documents\GitHub\web_scraping_yokin"
os.chdir(target_dir)
print(f"Current working directory: {os.getcwd()}")


def remove_muda(text):
    # 削除したい文字のリスト
    characters_to_remove = ["%", " ", "年", "％", "　", "(", ")", "金利", "普通預金", "Ç¯"]
    for char in characters_to_remove:
        text = text.replace(char, "")
    # 全角数字を半角に変換
    text = text.translate(str.maketrans({
        "０": "0", "１": "1", "２": "2", "３": "3", "４": "4", 
        "５": "5", "６": "6", "７": "7", "８": "8", "９": "9", 
        "．": ".", "（": "", "）": ""}))
    # 不要な括弧内の文字を削除
    text = re.sub(r'\（.*?\）', '', text)
    # 数字以外の部分を削除
    text = re.sub(r'[^0-9.]', '', text)
    # 数値に変換
    try:
        return float(text)
    except ValueError:
        return None


def get_rate(bank_name, url, selector, use_js=False):
    try:
        if use_js:
            options = Options()
            options.headless = True
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            driver.quit()
        else:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

        target = soup.select_one(selector)
        if target:
            return remove_muda(target.get_text()), use_js, True
        else:
            return None, use_js, False
    except Exception as e:
        print(f"Error fetching rate for {bank_name} with{' JS' if use_js else ''}: {e}")
        return None, use_js, False

# first_check_result.csvからsuccess=Trueの行を抽出
df = pd.read_csv('first_check_result.csv')
success_df = df[df['success'] == True]

# 種類ごとに成功率をコンソールに出力
type_counts = success_df['type'].value_counts()
type_totals = df['type'].value_counts()

print("取得対象金融機関の状況: ")
for t in type_totals.index:
    print(f"{t}: {type_counts.get(t, 0)}/{type_totals[t]} ({(type_counts.get(t, 0) / type_totals[t]) * 100:.2f}%)")

# 全体の行数を取得
total_rows = len(success_df)

# 対象となる金融機関を順番にスクレイピング
results = []

for idx, row in success_df.iterrows():
    bank_name = row['bank_name']
    url = row['url']
    selector = row['selector']
    use_js = row['js']

    rate, js_used, success = get_rate(bank_name, url, selector, use_js)

    results.append({
        'date': datetime.now().strftime('%Y-%m-%d'),
        'bank_name': bank_name,
        'type': row['type'],
        'pref': row['pref'],
        'code': row['code'],
        'interest_rate': rate,
        'js': js_used,
        'success': success
    })

    # コンソールに進行状況を出力
    print(f"Processing {idx + 1}/{total_rows}: {bank_name} - {'Success' if success else 'Failed'}")




# 結果をエクセルファイルに追加
results_df = pd.DataFrame(results)

excel_file = 'yokin_rate.xlsx'

if not os.path.exists(excel_file):
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        results_df.to_excel(writer, index=False)
else:
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        existing_df = pd.read_excel(excel_file)
        combined_df = pd.concat([existing_df, results_df], ignore_index=True)
        combined_df.to_excel(writer, index=False)

print(f"Results saved to {excel_file}")
