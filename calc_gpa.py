from pandas.core.frame import DataFrame


# try:
import time, datetime, sys
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import pandas as pd
from getpass import getpass
from webdriver_manager.chrome import ChromeDriverManager

# driver = webdriver.Chrome(ChromeDriverManager(version="89.0.4389.114").install())
# except ImportError:
    # print("Failed on import - debug!")
    # sys.exit(-1)

def get_data(doc : object) -> DataFrame:
    return pd.read_html(doc, attrs={'id': 'resultTableGrup'})[0][
        ["Navn", "Bedømt", "Karakter", "ECTS"]].query("Karakter not in ['U', 'B', 'I']") \
                                               .dropna(thresh = 1) \
                                               .astype({'Navn': 'str', 
                                                    'Karakter': 'float', 
                                                    'Bedømt': 'datetime64',
                                                    'ECTS': 'float'}) # returns list

def calc_gpa(data : DataFrame) -> int:
    return round(sum(data.Karakter * data.ECTS) / data.ECTS.sum(), 2)

def credentials() -> tuple:
    print("="*10, "\n" "Username: ", end = "")
    return input(), getpass("Password: ")

def login_sequence(driver : object, url : str):

        acc_name, acc_pass = credentials()
        print("="*10)
        driver.find_element_by_id("username").send_keys(acc_name)
        driver.find_element_by_id("user_pass").send_keys(acc_pass)
        driver.find_element_by_xpath('//*[@id="loginform"]/div[3]/input').click()
        time.sleep(1)

        driver.get(url)

def get_gpa(url : str = "https://sb-cbs.stads.dk/sb/resultater/studresultater.jsp"):

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(ChromeDriverManager(version = "89.0.4389.23", 
                                                  log_level = 0).install(), 
                              options = options)
    driver.get(url)

    while "studresultater" not in driver.current_url:
        login_sequence(driver, url)

    data = get_data(driver.page_source)
    
    print(f"All-time GPA: {calc_gpa(data)}")
    print(f"Masters' GPA: {calc_gpa(data[data['Bedømt'] > datetime.datetime(2019,9,1)])}")
    input("----------\nPress any key to exit")
    sys.exit(-1)
     


if __name__ == "__main__":
    get_gpa()
