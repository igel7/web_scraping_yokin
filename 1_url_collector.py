import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# set working directory
target_dir = r"your working directory"
os.chdir(target_dir)
print(f"Current working directory: {os.getcwd()}")

# import csv file
input_csv = 'banks_list.csv
output_csv = 'banks_output.csv'  # set output csv file name
tmp_dir = os.path.join(target_dir, 'tmp')

# make temp directory
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

banks_df = pd.read_csv(input_csv, encoding='SHIFT_JIS')

# setup
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# Get URLs by keyword search at google
def fetch_url(bank_name):
    try:
        driver.get('https://www.google.com')
        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(f"{bank_name} 普通預金金利")
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(2)  # wait till the search result comes out

        # click the first web page from the search reault
        results = driver.find_elements(By.CSS_SELECTOR, 'h3')
        if results:
            results[0].click()
            time.sleep(2)  # wait until the page loads

            # get URL
            return driver.current_url
    except Exception as e:
        print(f"Error fetching URL for {bank_name}: {e}")
        return None

# get URLs of banks listed in csv
urls = []
batch_size = 5
for index, row in banks_df.iterrows():
    bank_name = row['bank_name']
    url = fetch_url(bank_name)
    urls.append(url)
    
    # current status on console
    print(f"{index + 1}/{len(banks_df)}: {bank_name} の URL: {url}")
    
    # batch jobs
    if (index + 1) % batch_size == 0 or (index + 1) == len(banks_df):
        batch_df = banks_df.iloc[index - (index % batch_size):index + 1]
        batch_df['url'] = urls[-batch_df.shape[0]:]
        batch_file = os.path.join(tmp_dir, f'batch_{index // batch_size}.csv')
        batch_df.to_csv(batch_file, index=False)
        print(f"Batch saved to {batch_file}")

# close browser
driver.quit()

# make result file from batch files
all_batches = []
for batch_file in sorted(os.listdir(tmp_dir)):
    if batch_file.endswith('.csv'):
        batch_df = pd.read_csv(os.path.join(tmp_dir, batch_file))
        all_batches.append(batch_df)

final_df = pd.concat(all_batches, ignore_index=True)
final_df.to_csv(output_csv, index=False)

print(f"All batches combined and saved to {output_csv}")
