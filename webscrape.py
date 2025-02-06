from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless=new')
options.add_argument("--window-size=1920,1200")  # Set the window size


driver = webdriver.Chrome(options=options)

driver.get('https://compstat.nypdonline.org/');

cs_book = driver.find_element(By.XPATH, "/html/body/app-root/div[1]/app-home/div/div/app-report[1]")

book_header = cs_book.find_element(By.XPATH, './div/div[1]')

header_elements = book_header.find_element(By.XPATH, "./child::*").find_elements(By.XPATH, "./child::*")
week = list(map(lambda x: x.text, header_elements))[1]

print(week)

# getting information from the compstat book table
table = cs_book.find_element(By.XPATH, './div/div[2]')

table_header = table.find_element(By.XPATH, './kendo-grid/div/div/div[2]/table/thead/tr')

major_col_lbls = {}

#dictionary for which columns are associated with which major headers
for col in table_header.find_elements(By.XPATH, './child::*'):
    if len(col.text) != 0:
        col_num = int(col.get_attribute('aria-colindex'))
        major_col_lbls[col_num - 1] = col.text
        major_col_lbls[col_num] = col.text
        major_col_lbls[col_num + 1] = col.text

# getting all crimes listed (every entry on leftmost columns)
crime_col = table.find_element(By.XPATH, './kendo-grid/div/kendo-grid-list/div[1]/div[1]/table/tbody')

#map of rows and their corrisponding labels
row_lbls = {}

for row in crime_col.find_elements(By.XPATH, './child::*'):
    if len(row.text.strip()) != 0:
        cur_row = int(row.get_attribute('aria-rowindex'))
        row_lbls[cur_row] = row.text


print(row_lbls)




driver.quit()
