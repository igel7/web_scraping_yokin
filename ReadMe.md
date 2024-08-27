[日本語はこちら](ReadMe_ja.md)    

# Repository Description
## Core Features
- Collects ordinary deposit interest rate information from all financial institutions in Japan at appropriate times and stores it in an Excel file. Specifically, it covers the following three stages:
### 1. Preprocessing
- A. If you list the financial institutions you want to research in a CSV file, it automatically searches Google with the institution's name + "saving deposit interest rate" and lists the URL of the first page that appears.
- B. Process to open the listed URLs in the browser in batches of 10 (it is assumed that CSS selectors will be collected manually).
### 2. Information Acquisition
- Automatically retrieves information from the CSV file of URLs and CSS selectors.
### 3. Supplementary Features
- Automatically checks if the target web page's robots.txt allows crawling for the information acquisition directories.

## Technical Innovations
- Although collecting all the CSS selectors of the target financial institutions must be done manually, automating the acquisition of URLs and the opening of these URLs in the browser minimizes unnecessary manual effort.
- Uses BeautifulSoup for web pages not using JavaScript, and Selenium to launch a browser and retrieve information from pages that do use JavaScript. This avoids reliance solely on the slower Selenium, balancing speed and comprehensiveness.

## File Structure
- There are .py files 1 through 5, but only 4 is executed daily.
- Files 1 through 3 are for preprocessing necessary to run the program.
- It is assumed that the user creates the CSV files themselves; however, actual usage examples are stored in the ref folder for reference.

| File | Function |
|:-----|:---------|
| 1_url_collector.py | Uses Selenium to search Google for bank names and deposit interest rates, automatically collecting the first result URL. Reads bank names from `banks_list.csv` and outputs a list of bank names and URLs to `banks_output.csv`. |
| 2_open_url.py | Opens URLs from the list in batches of 10 in a browser (to efficiently gather CSS selectors). Reads URLs from `banks_output.csv`, opens them, and manual CSS selector collection is assumed to create `banks_list_ok.csv`. |
| 3_first_check.py | Tests if scraping works from the list of URLs and CSS selectors. Reads URL and CSS selector list from `banks_list_ok.csv`, performs scraping, and outputs the results to `first_check_result2.csv`. |
| 4_scraping_rate.py | Production file. Reads the results from `first_check_result.csv` and appends them to `yokin_rate.xlsx` (creates the file if it does not exist). |
| 5_check_robots_txt.py | Checks if the target site is allowed for crawling. Automatically verifies the target financial institution's website robots.txt to check if crawling is permitted. |



# Additional Instructions
## How to Register a Task with Task Scheduler (assuming registration of 4.scraping_rate.py)
- Open Task Scheduler:
    - Press Windows key + S, type "Task Scheduler," and open it.

- Select "Create Task":
    - Click "Create Basic Task" on the right side.
    - The "Create Task" wizard opens.

- Enter task name and description:
    - Enter a task name and, if necessary, a description (e.g., Daily Python Script).
    - Click "Next."

- Set the trigger:
    - Select "Daily" and click "Next."
    - Set the start date and time for the script to run (e.g., set for tomorrow at 6 AM).
    - Click "Next."

- Set the action:
    - Select "Start a program" and click "Next."

- Program/Script settings:
    - Enter the full path to the WinPython executable in "Program/Script" (e.g., C:\\Users\\ryasu\\WinPython-3.12.x\\python-3.12.x.amd64\\python.exe).
    - Add the full path of the script in "Add arguments (optional)" (e.g., C:\\Users\\ryasu\\Documents\\GitHub\\web_scraping\\4_scraping_rate.py).

- Completion:
    - Click "Next" and then "Finish."

## Path Setup (to ensure Task Scheduler can run Python)
- Open WinPython's installation directory:
    - Check the installation path of WinPython, such as C:\\Users\\ryasu\\WinPython-3.12.x.
    - Find the folder containing the Python executable (usually something like python-3.12.x.amd64).

- Copy the path of the Python executable:
    - Example: C:\\Users\\ryasu\\WinPython-3.12.x\\python-3.12.x.amd64

- Open Windows System Settings:
    - Press Windows key + S, type "Environment Variables," and click "Edit the system environment variables."

- Open Environment Variables Dialog:
    - When the "System Properties" window opens, click "Environment Variables."

- Edit the Path variable:
    - In the "System variables" list, select "Path" and click "Edit."

- Add the new path:
    - Click the "New" button and add the path to the Python executable (e.g., C:\\Users\\ryasu\\WinPython-3.12.x\\python-3.12.x.amd64).

- Save changes:
    - Click "OK" to save changes and close all dialogs.
