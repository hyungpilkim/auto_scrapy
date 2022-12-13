from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException, InvalidArgumentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from multiprocessing import Queue
import conf

import pyperclip
from selenium.webdriver.common.keys import Keys

from define_data import DataJob, TypeSelector, TypeAction, TypeTarget
class Browser():
    def __init__(self, job_q, result_q):
        self.job_q = job_q
        self.result_q = result_q
        
    def open_browser(self ):
        self.browser = webdriver.Chrome(conf.config['selenium_path'])
        self.browser.implicitly_wait(5)
        self.browser.get("https://www.naver.com")
        self.current_url = self.browser.current_url
        self.queue_loop()

    def queue_loop(self):
        while True:
            if not self.job_q.empty():
                list = self.job_q.get()
                self.excute_job(list)
                    
                    
    def excute_job(self, list):
        #for data in list:
        print("excute_job", list)
        single_list = []
        multiple_list = []
        for data in list:
            if data[DataJob.attr_type_target] == TypeTarget.multiple:
                multiple_list.append(data)
            else:
                single_list.append(data)
        
        #print("single_list", single_list)
        #print("multiple_list", multiple_list)
        for data in single_list:
            print('current_url', self.current_url)
            #target url 이동
            if data[DataJob.attr_type_target] == TypeTarget.url:
                self.browser.get(data[DataJob.attr_text_target])
                self.current_url = self.browser.current_url
                data[DataJob.attr_text_result] = 'ok'
                self.result_q.put(data)
            #target frame 이동
            elif data[DataJob.attr_type_target] == TypeTarget.frame:
                self.browser.switch_to.frame(data[DataJob.attr_text_target])
                data[DataJob.attr_text_result] = 'ok'
                self.result_q.put(data)
            #target single
            elif data[DataJob.attr_type_target] == TypeTarget.single:
                self.single_action(data)
                self.result_q.put(data)

        #target multiple   
        if len(multiple_list) > 0:
            self.multiple_action(multiple_list);
    
    #BeautifulSoup 데이터 GET
    def multiple_action(self, multiple_list):
        #부모 리스트 가져오기 
        try:
            page_source = self.browser.page_source 
            soup = BeautifulSoup(page_source, "html.parser")
            elements = soup.select(multiple_list[0][DataJob.attr_text_target])
            results = []
            for item in elements:
                print("item", item)
                column = {}
                for idx, job in enumerate(multiple_list):
                    try:
                        subitem = item.select_one(job[DataJob.attr_text_selector])
                        print("subitem", subitem)
                        if subitem is not None:
                            column[idx] = subitem.get_text().strip()
                        else:
                            column[idx] = ''
                            
                    except NoSuchElementException as e:
                        print("NoSuchElementException", e.msg)
                        job[DataJob.attr_text_result] = e.msg
                    except InvalidSelectorException as e:
                        print("InvalidSelectorException", e.msg)
                        job[DataJob.attr_text_result] = e.msg
                    except InvalidArgumentException as e:
                        print("InvalidSelectorException", e.msg)
                        job[DataJob.attr_text_result] = e.msg
                results.append(column)

        except NoSuchElementException as e:
            print("NoSuchElementException", e.msg)
            multiple_list[0][DataJob.attr_text_result] = e.msg
        except InvalidSelectorException as e:
            print("InvalidSelectorException", e.msg)
            multiple_list[0][DataJob.attr_text_result] = e.msg
        except InvalidArgumentException as e:
            print("InvalidSelectorException", e.msg)
            multiple_list[0][DataJob.attr_text_result] = e.msg

        multiple_list[0][DataJob.attr_text_result] = results
        self.result_q.put(multiple_list[0])

    def single_action(self, data):
        element = None
        #선택자가 있으면 find element 
        if len(data[DataJob.attr_text_selector]) > 0:
            try:
                if data[DataJob.attr_type_selector] == TypeSelector.id:
                    element = self.browser.find_element(By.ID, data[DataJob.attr_text_selector])
                elif data[DataJob.attr_type_selector] == TypeSelector.class_:
                    element = self.browser.find_element((By.CLASS_NAME, data[DataJob.attr_text_selector]))
                elif data[DataJob.attr_type_selector] == TypeSelector.xpath:
                    element = self.browser.find_element(By.XPATH, data[DataJob.attr_text_selector])
                elif data[DataJob.attr_type_selector] == TypeSelector.query_selector:
                    element = self.browser.find_element(By.CSS_SELECTOR, data[DataJob.attr_text_selector])
            except NoSuchElementException as e:
                print("NoSuchElementException", e.msg)
                data[DataJob.attr_text_result] = e.msg
            except InvalidSelectorException as e:
                print("InvalidSelectorException", e.msg)
                data[DataJob.attr_text_result] = e.msg
            except InvalidArgumentException as e:
                print("InvalidSelectorException", e.msg)
                data[DataJob.attr_text_result] = e.msg

            if element is None:
                data[DataJob.attr_text_result] = "not find element"
            else:
                data[DataJob.attr_text_result] = 'ok'
                #element border
                self.check_selector(self.browser, data[DataJob.attr_type_selector], data[DataJob.attr_text_selector])

                #액션 click
                if data[DataJob.attr_type_action] == TypeAction.click:
                    element.click()
                #액션 get
                elif data[DataJob.attr_type_action] == TypeAction.get:
                    data[DataJob.attr_text_result] = element.text
                #액션 set
                elif data[DataJob.attr_type_action] == TypeAction.set:
                    element.click()
                    self.browser.implicitly_wait(10)
                    pyperclip.copy(data[DataJob.attr_text_input])
                    ActionChains(self.browser).move_to_element(element).key_down(Keys.CONTROL).send_keys("V").perform()
        else:
            data[DataJob.attr_text_result] = "selected text is empty"

    def check_selector_xpath(self, browser, xpath):
        xpath_function = "function getElementByXpath(path) { return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;};"
        print(f"{xpath_function} getElementByXpath('{xpath}').style.backgroundColor='red';")
        browser.execute_script(f"{xpath_function} getElementByXpath('{xpath}').style.border='solid 1px';")

    def check_selector(self, browser, type, select_text):
        if type == TypeSelector.id:
            browser.execute_script(f"document.querySelectorAll('#{select_text}').forEach(ele => {{ele.style.border='solid 1px';}}")
        elif type == TypeSelector.class_:
            browser.execute_script(f"document.querySelectorAll('.{select_text}').forEach(ele => {{ele.style.border='solid 1px';}}")
        elif type == TypeSelector.xpath:
            self.check_selector_xpath(browser, select_text)
        elif type == TypeSelector.query_selector:
            browser.execute_script(f"document.querySelectorAll('{select_text}').forEach(ele => {{ele.style.border='solid 1px';}}")

def callback_test(data):
    print(data)


if __name__ == "__main__":
    job_q = Queue()
    result_q = Queue()
    browser = Browser(job_q, result_q)
    browser.open_browser()

    