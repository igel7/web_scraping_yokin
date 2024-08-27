import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import openpyxl
import re
import os

# set working directory
target_dir = r"C:\Users\ryasu\Documents\GitHub\web_scraping_yokin"
os.chdir(target_dir)
print(f"Current working directory: {os.getcwd()}")


def remove_muda(text):
    # letters to remove
    characters_to_remove = ["%", " ", "年", "％", "　", "(", ")", "金利", "普通預金", "Ç¯"]
    for char in characters_to_remove:
        text = text.replace(char, "")
    # change string to number
    text = text.translate(str.maketrans({
        "０": "0", "１": "1", "２": "2", "３": "3", "４": "4", 
        "５": "5", "６": "6", "７": "7", "８": "8", "９": "9", 
        "．": ".", "（": "", "）": ""}))
    # remove any strings inside ()
    text = re.sub(r'\（.*?\）', '', text)
    # remove anything besides numbers
    text = re.sub(r'[^0-9.]', '', text)
    # change sting to number
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

# From first_check_result.csv, choose rows that have success colum =True
df = pd.read_csv('first_check_result.csv')
success_df = df[df['success'] == True]

# show successful rate by type on console
type_counts = success_df['type'].value_counts()
type_totals = df['type'].value_counts()

print("Status: ")
for t in type_totals.index:
    print(f"{t}: {type_counts.get(t, 0)}/{type_totals[t]} ({(type_counts.get(t, 0) / type_totals[t]) * 100:.2f}%)")

# get total number of banks
total_rows = len(success_df)

# scraping
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

    # shows status on console
    print(f"Processing {idx + 1}/{total_rows}: {bank_name} - {'Success' if success else 'Failed'}")




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
