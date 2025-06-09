# this file class DailyWorker, which is used to get data from the website

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import tempfile
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import csv, requests
import datetime
import config,os
from dotenv import load_dotenv

class DailyWorker:
    def __init__(self):
        self.driver = None
        load_dotenv()


    def get_token(self):
        '''
        login the website manually to get token
        '''
        # 设置 Chrome 选项
        chrome_options = Options()
        temp_dir = tempfile.mkdtemp() 
        chrome_options.add_argument(f"--user-data-dir={temp_dir}") 
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars") 
        chrome_options.add_argument("--disable-extensions") 
        chrome_options.add_experimental_option("detach", True)
        driver_path = "./chromedriver.exe"

        service = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            login_url = os.getenv("LOGIN_URL")
            self.driver.get(login_url)
            
            # 获取用户名输入框元素
            print("等待用户名输入框加载...")
            username_input = WebDriverWait(self.driver, timeout=60).until(
                EC.presence_of_element_located((By.XPATH, '//*[@placeholder="用户名"]')) 
            )
            print('开始输入用户名...')
            #get username from .env
            username = os.getenv("USERNAME")
            username_input.send_keys(username)

            # 获取密码输入框元素
            password_input = self.driver.find_element("xpath", '//*[@placeholder="密码"]')
            #get password from.env
            password = os.getenv("PASSWORD")
            password_input.send_keys(password)

            logging_button = WebDriverWait(self.driver, timeout=60).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "登 录")]')) 
            )
            logging_button.click()

            # 等待登录成功
            WebDriverWait(self.driver, timeout=60).until(
                lambda d: "login" not in d.current_url
            )
            print("检测到登录成功！")
            
            # 获取token
            time.sleep(1)
            token_raw = self.driver.execute_script("return window.sessionStorage.getItem('datax_mew-manage-ui_token');")
            token = json.loads(token_raw)
            with open('token.txt', 'w') as f:
                f.write(token)
                print("Token已保存到token.txt文件中")
            self.driver.quit()

        except Exception as e:
            print(f"发生错误: {e}")


    def get_last_week_alarm(self):
        '''
        get alarm data from last week
        '''
        # 获取当前日期
        today = datetime.date.today()
        # 计算一周前的日期
        last_week = today - datetime.timedelta(days=7)
        # 格式化为YYYYMMDD
        last_week_str = last_week.strftime("%Y%m%d")
        today_str = today.strftime("%Y%m%d")
        result = self.get_alarm_data_in_range(last_week_str, today_str)
        return result

    def get_today_alarm(self):
        '''
        get alarm data of today
        '''
        # 获取今天的日期
        today = datetime.date.today()
        # 格式化为YYYYMMDD
        today_str = today.strftime("%Y%m%d")
        result = self.get_alarm_data_in_range(today_str, today_str)
        return result
    

    def get_yesterday_alarm(self):
        '''
        get alarm data from yesterday
        '''
        # 获取昨天的日期
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        # 格式化为YYYYMMDD
        yesterday_str = yesterday.strftime("%Y%m%d")
        today_str = datetime.date.today().strftime("%Y%m%d")
        result = self.get_alarm_data_in_range(yesterday_str, yesterday_str)
        return result
        

    # @staticmethod
    def get_alarm_data_in_range(self,date_start: str, date_end: str):
        '''
        this function is used to get alarm data in a specific date range
        :param date_start: start date in format YYYYMMDD
        :param date_end: end date in format YYYYMMDD
        :return: alarm data in the specified date range, 1000 records in maximum
        '''
        max_length = config.MAX_LENGTH


        with open('token.txt', 'r') as f:
            token = f.read()
                
        domain = os.getenv("DOMAIN")
        referer = domain + '/mew-manage-ui/index.html'
        host = os.getenv("HOST")
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': host,
            'passKey': '',
            'Referer':referer,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'passKey': '',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile':'?0',
            'sec-ch-ua-platform': "Windows",
            'token': token
        }

        api_url = f'{domain}/mew-manage/commonbusiness/alarmevent/list-center?cityCode=&equipType=&industryType=&workersNumber=&dustType=&scaleType=&startAlarmTime={date_start}&endAlarmTime={date_end}&targetType=&alarmGrade=&warnStatus=&deald=&entName=&entId=&position=bottom&align=right&simple=false&current=1&size={max_length}&pages=0&showTotalInfo=true&showQuickJumper=false&showSizeChanger=true&maxLength=6&sizeList[]=10&sizeList[]=50&sizeList[]=100&sizeList[]=200'
        print(f'请求的API URL: {api_url}')
        try:
            # response = requests.get(api_url, headers=headers, cookies=self.cookies)
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            raw_data = response.json()
            if raw_data['code'] == -44:
                print("token已过期，请重新登录获取新的token")
                self.get_token()
            if raw_data['data']['total']> max_length:
                data = {
                    "msg": "查询结果超过最大限制，请调整查询范围。",
                    "total": raw_data['data']['total'],
                    "data": raw_data['data']['records']
                }
            else:
                data = {
                    "msg": "查询成功",
                    "total":raw_data['data']['total'],
                    "data": raw_data['data']['records']
                }
        except requests.exceptions.RequestException as e:
            print("❌ 请求失败:", e)
            data = None
        finally:
            with open(f'alarm_data_{date_start}_{date_end}.csv', 'w', encoding='gbk', newline='',errors='ignore') as f:
                field_names = ['targetName','entFullName','prodAddrName','equipName','targetTypeName','alarmGradeName','startAlarmTime','endAlarmTime','alarmContent','continueMins']
                writer = csv.DictWriter(f, fieldnames=field_names)
                writer.writeheader()
                print(raw_data)
                for record in raw_data['data']['records']:
                    # 仅保留 field_names 中的字段
                    filtered_record = {key: record.get(key, '') for key in field_names}
                    date_start = datetime.datetime.strptime(filtered_record['startAlarmTime'], '%Y%m%d%H%M%S') if filtered_record['startAlarmTime'] else ''
                    filtered_record['startAlarmTime'] = date_start.strftime('%Y-%m-%d %H:%M:%S') if filtered_record['startAlarmTime'] else ''
                    date_end = datetime.datetime.strptime(filtered_record['endAlarmTime'], '%Y%m%d%H%M%S') if filtered_record['endAlarmTime'] else ''
                    filtered_record['endAlarmTime'] = date_end.strftime('%Y-%m-%d %H:%M:%S') if filtered_record['endAlarmTime'] else ''
                    writer.writerow(filtered_record)
            return data


if __name__ == "__main__":
    worker = DailyWorker()
    result = worker.get_alarm_data_in_range('20250602','20250608')