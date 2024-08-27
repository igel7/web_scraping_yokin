import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# set working directory
os.chdir('your working directory')
print("Changed Directory:", os.getcwd())

def get_rate(bank_name, url, selector):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check HTTP error
        soup = BeautifulSoup(response.content, 'html.parser')
        target = soup.select_one(selector)
        if target:
            return remove_muda(target.get_text()), False, True  # No Java Script, Got data
        else:
            return None, False, False  # No Java Script, Failed to get data
    except Exception as e:
        print(f"Error fetching rate for {bank_name} without JS: {e}")
        return None, False, False  # No Java Script, Failed to get data

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
            return remove_muda(target.get_text()), True, True  # Use Java Script, Got data
        else:
            return None, True, False  # Use Java Script, Failed to get data
    except Exception as e:
        print(f"Error fetching rate for {bank_name} with JS: {e}")
        return None, True, False  # Use Java Script, Failed to get data

def remove_muda(text):
    characters_to_remove = ["%", " ", "年", "％", "　"]
    for char in characters_to_remove:
        text = text.replace(char, "")
    return text

# import banks' list
banks_df = pd.read_csv('banks_list_ok.csv', encoding='SHIFT_JIS')

# how many data you do
start_row = 0  # start row（0-indexed）
num_rows = 170  # job number to go
batch_size = 3  # batch size

# make tmp directory for batch jobs
tmp_dir = 'tmp'
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

# make DataFrame to store results
results = pd.DataFrame(columns=['date', 'bank_name', 'url', 'selector', 'type', 'pref', 'code', 'interest_rate', 'js', 'success'])

# 指定された範囲の行について処理を行う
for idx, (index, row) in enumerate(banks_df.iloc[start_row:start_row + num_rows].iterrows(), start=start_row + 1):
    bank_name = row['bank_name']
    url = row['url']
    selector = row['selector']
    js = row['js']
    
    if pd.isna(selector) or not selector.strip():
        # Skip if CSS selector is blank
        rate, js, success = None, None, False
        print(f"[{idx}/{len(banks_df)}] {bank_name}: skip as the selector cell is blank")
    else:
        rate, js, success = get_rate(bank_name, url, selector)
        if success:
            print(f"[{idx}/{len(banks_df)}] {bank_name}: Success. No Java Script.")
        else:
            rate, js, success = get_rate_js(bank_name, url, selector)
            if success:
                print(f"[{idx}/{len(banks_df)}] {bank_name}: Success. No Java Script.")
            else:
                print(f"[{idx}/{len(banks_df)}] {bank_name}: failed to get data.")
    
    # add result to result data frame
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
    
    # batch job
    if idx % batch_size == 0:
        batch_file = os.path.join(tmp_dir, f'batch_{idx // batch_size}.csv')
        results.to_csv(batch_file, index=False)
        print(f"Batch saved to {batch_file}")
        results = pd.DataFrame(columns=['date', 'bank_name', 'url', 'selector', 'type', 'pref', 'code', 'interest_rate', 'js', 'success'])

# the lest
if not results.empty:
    batch_file = os.path.join(tmp_dir, f'batch_{(idx // batch_size) + 1}.csv')
    results.to_csv(batch_file, index=False)
    print(f"Batch saved to {batch_file}")

# put all the batches
all_batches = []
for batch_file in sorted(os.listdir(tmp_dir)):
    if batch_file.endswith('.csv'):
        batch_df = pd.read_csv(os.path.join(tmp_dir, batch_file))
        all_batches.append(batch_df)

final_df = pd.concat(all_batches, ignore_index=True)

# show result
print(final_df)

# save result df to csv if needed
def save_results_to_csv(results, filename='first_check_result2.csv'):
    results.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

save_results_to_csv(final_df)
