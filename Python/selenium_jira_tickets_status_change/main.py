from selenium import webdriver
import json

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

#from selenium.webdriver.remote.webelement import WebElement
#from selenium.webdriver.common.keys import Keys

# Function Definations

def login_to_website(username,password):

    login_email = driver.find_element_by_xpath(var["LogIn_Email"])
    login_email.send_keys(var["Login_Email_Value"]);
    Next_MS_Button = driver.find_element_by_xpath(var["Next_MS_Button"])
    Next_MS_Button.click()

    login_pass_ms = driver.find_element_by_xpath(var["LogIn_MS_Password"])
    login_pass_ms.send_keys(var["Login_Password_Value"]);

    driver.implicitly_wait(5)
    login_Button = driver.find_element_by_xpath(var["LogIn_Button"])
    login_Button.click()

    Stay_Signed_In_Button = driver.find_element_by_xpath(var["Stay_Signed_In"])
    Stay_Signed_In_Button.click()

def export_to_csv():
    export_button = driver.find_element_by_xpath(var["Export_click"])
    export_button.click()

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, 'CSV (All fields)'))).click()

    inner_export_button = driver.find_element_by_xpath(var["Inner_Export"])
    inner_export_button.click()

def select_all_tickets():
    tools_button = driver.find_element_by_xpath(var["Tools_Click"])
    tools_button.click()

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'bulkedit_all'))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'bulkedit-select-all'))).click()

    Next_for_In_progress = driver.find_element_by_xpath(var["Next_Button"])
    Next_for_In_progress.click()

def make_in_progress():
    select_all_tickets()
    radio_button_click("aui", "Transition Issues")
    Next_for_In_progress_1 = driver.find_element_by_xpath(var["Next_Button"])
    Next_for_In_progress_1.click()

    radio_button_click("aui aui-table-rowhover", "Start Progress")
    Next_for_In_progress_2 = driver.find_element_by_xpath(var["Next_Button"])
    Next_for_In_progress_2.click()

    Next_for_In_progress_3 = driver.find_element_by_xpath(var["Next_Button"])
    Next_for_In_progress_3.click()

    Confirm_In_Progress = driver.find_element_by_xpath(var["Next_Button"])
    Confirm_In_Progress.click()

    driver.implicitly_wait(30)

    In_Progress_Done = driver.find_element_by_xpath(var["Okay_got_it"])
    In_Progress_Done.click()

def close_tickets():
    select_all_tickets()
    radio_button_click("aui", "Transition Issues")
    Next_for_In_progress_1 = driver.find_element_by_xpath(var["Next_Button"])
    Next_for_In_progress_1.click()

    radio_button_click("aui aui-table-rowhover", "Close")
    Next_for_In_progress_2 = driver.find_element_by_xpath(var["Next_Button"])
    Next_for_In_progress_2.click()


    Change_Resolution = driver.find_element_by_xpath(var["Change_Resolution"])
    Change_Resolution.click()

    option_list = Select(driver.find_element_by_id('customfield_14746'))
    option_list.select_by_value('17213')

    option_list1 = Select(driver.find_element_by_id('resolution'))
    option_list1.select_by_value('15')


    option_list = Select(driver.find_element_by_id('resolution'))
    option_list.select_by_value('15')

    Next_for_In_progress_3 = driver.find_element_by_xpath(var["Next_Button"])
    Next_for_In_progress_3.click()

    Confirm_In_Progress = driver.find_element_by_xpath(var["Next_Button"])
    Confirm_In_Progress.click()

    driver.implicitly_wait(30)

    Closed_Done = driver.find_element_by_xpath(var["Okay_got_it"])
    Closed_Done.click()


def radio_button_click(table_class,selection_string):
    temp_var = "//table[@class=\'"+ table_class + "\']"
    table = driver.find_element_by_xpath(temp_var)
    for row in table.find_elements_by_xpath(".//tr"):
        print(row.text)
        if selection_string in row.text:
            print("Write")
            td = row.find_element_by_tag_name("input")
            print(td)
            td.click()
            break


# Get/Load Variables
config_file = open('config.json')
var = json.load(config_file)
config_file.close()
print(var["LogIn"])

# Function calls and main
driver = webdriver.Chrome('C:\Program Files (x86)\chromedriver\chromedriver')

driver.get("https://jira.domain.com/issues/?jql=project%20%3D%20%22PC%22%20AND%20type%20%3D%20%22Public%20Cloud%20Finding%22%20AND%20status%20not%20in%20(%22Closed%22%2C%22Resolved%22%2C%22In%20Risk%20Acceptance%22)%20AND%20%22Team%20ID%22%20%3D%20%22Research%22%20AND%20finding%20~%20%22cost_%22%20")
print(driver.title)
login_button = driver.find_element_by_xpath(var["LogIn"])
login_button.click()

# Login Call
login_to_website("LogIn_UserName","LogIn_Password")
export_to_csv()
make_in_progress()
close_tickets()