from selenium import webdriver
import matplotlib.pyplot as plt
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def get_row_map(row):
    row_map = {}
    for element in row.find_elements(By.XPATH, './child::*'):
        row_map[int(element.get_attribute('aria-colindex'))] = {
            'text': element.text.replace(',',''),
            'element': element
        }
    return row_map

def get_value(row, column, attribute, table_entries):
    return table_entries[row_lbls[row]][col_lbls[column]][attribute]

def get_crime_piechart(rows, column, table_entries):
    values = list(map(lambda x: int(get_value(x, column, 'text', table_entries)), rows))
    plt.pie(values, labels = rows)
    plt.show()

def get_circle_positions(row, column table_entries):
    element = get_value(row, column, 'element', table_entries)
    return



if __name__ == "__main__":

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
            col_index = int(col.get_attribute('aria-colindex'))
            major_col_lbls[col_index - 1] = col.text
            major_col_lbls[col_index] = col.text
            major_col_lbls[col_index + 1] = col.text

    # getting all crimes listed (every entry on leftmost columns)
    crime_col = table.find_element(By.XPATH, './kendo-grid/div/kendo-grid-list/div[1]/div[1]/table/tbody')

    #map of rows and their corrisponding labels
    row_lbls = {}

    for row in crime_col.find_elements(By.XPATH, './child::*'):
        if len(row.text.strip()) != 0:
            row_index = int(row.get_attribute('aria-rowindex'))
            row_lbls[row.text] = row_index


    print(row_lbls)

    table_rows = table.find_elements(By.XPATH, './kendo-grid/div/kendo-grid-list/div[2]/div[1]/table/tbody/child::*')

    col_lbls = {}

    #looking at the labeling of the first row in the table '{column label} {major column label}'
    for col in table_rows[0].find_elements(By.XPATH, './child::*'):
        col_index = int(col.get_attribute('aria-colindex'))
        col_lbls[f"{col.text} {major_col_lbls[col_index]}"] = col_index

    print(col_lbls)



    table_entries = {}
    for row in table_rows[1:]:
        rowindex = int(row.get_attribute('aria-rowindex'))
        table_entries[rowindex] = get_row_map(row)

    get_crime_piechart(list(row_lbls.keys())[:7],'2024 Week to Date', table_entries)


    driver.quit()
