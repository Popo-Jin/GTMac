from os import name
import os
import sys
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import * 
from PyQt5 import uic 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
from PyQt5.QtCore import QCoreApplication, QThread
from PyQt5.uic.properties import QtWidgets 
# PYQT5 를 이용하기 위한 모듈갱신
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import datetime
import threading
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import subprocess
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
import urllib

def resource_path(relative_path): 
    """ Get absolute path to resource, works for dev and for PyInstaller """ 
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)
 
# 불러오고자 하는 .ui 파일
    # .py 파일과 같은 위치에 있어야 한다 *****
form = resource_path('new_macro_0214.ui') 
form_class = uic.loadUiType(form)[0]

print('develop v_1.4_220214')

class MyWindow(QWidget, form_class):

# 초기 설정해주는 init
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('apeach_icon.png'))
# 시그널(이벤트루프에서 발생할 이벤트) 선언
# self.객체명.객체함수.connect(self.슬롯명)
        self.show_day()
        self.btn_wait.clicked.connect(self.btn_wait_click)
        self.btn_no.clicked.connect(self.btn_no_click)
        self.btn_tool.clicked.connect(self.btn_tool_click)
        self.lbl_time.setFont(QtGui.QFont("굴림",8))
        self.worker_servertime = Worker_servertime()
        self.worker_timeattack = Worker_timeattack()
        self.worker = Worker()
        self.workflag = False
        self.btn_tool.setText('')
        self.btn_tool.setIcon(QIcon('tool_icon.png'))
        self.btn_tool.resize(24, 24)
        self.lbl_time.setFont(QtGui.QFont("굴림", 10))
        self.lbl_time.setStyleSheet("font-weight: bold")
        self.loader.setFont(QtGui.QFont("굴림", 11))
        self.loader.setStyleSheet("color:rgb(85, 170, 255); font-weight: bold")
        self.loader.setVisible(False)
        
        
        # 서버시간 표시 (자동갱신)
        # webdriver_options = webdriver.ChromeOptions()
        # webdriver_options.add_argument('headless')
        # path = chromedriver_autoinstaller.install(True)
        
        # chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        # print('Chrome Version', chrome_ver)

        # self.servertime_driver = webdriver.Chrome('./chromedriver.exe', options=webdriver_options )
        # self.servertime_driver = webdriver.Chrome(path, options=webdriver_options )

        # self.servertime_driver.get('https://time.navyism.com/?host=www.sunvalley.co.kr')

        self.worker_servertime.start()
        self.allstop = False
        self.servertime_stop_flag = False
    

    def show_day(self):
        baseDate = datetime.date.today() 
        print("오늘 날짜 : ", baseDate)



    def btn_wait_click(self):

        if myWindow.id_txt.text() == '' or myWindow.pwd_txt.text() == '':
            self.msg = QMessageBox()
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.setText('아이디와 패스워드를 입력해주세요')
            self.msg.exec_()
        elif myWindow.day_box.text() == '':
            self.msg2 = QMessageBox()
            self.msg2.setStandardButtons(QMessageBox.Ok)
            self.msg2.setText('예매날짜를 입력해주세요. ex)2021-08-10')
            self.msg2.exec_()
        elif myWindow.time_box_start.text() == '' or myWindow.time_box_end.text() == '':
            self.msg3 = QMessageBox()
            self.msg3.setStandardButtons(QMessageBox.Ok)
            self.msg3.setText('예매시간을 입력해주세요. ex)07:30')
            self.msg3.exec_()
        else:
            myWindow.worker_timeattack_flag = False
            myWindow.worker_timeattack.start()
    
    def btn_no_click(self):
        self.allstop = True
        myWindow.worker.quit()
        myWindow.worker_servertime.quit()
        myWindow.worker_timeattack.quit()
        sys.exit()

    def btn_tool_click(self):
        myTool.show()

    
class ToolWindow(QDialog):
    def __init__(self, parent):
        super(ToolWindow, self).__init__(parent)
        tool_ui = 'tool_ui.ui'
        uic.loadUi(tool_ui, self)
        self.tool_save.clicked.connect(self.btn_tool_save)
        self.tool_cancel.clicked.connect(self.btn_tool_cancel)
        self.tool_hour.setText('9')
        self.tool_min.setText('59')
        self.tool_sec.setText('30')

        print(f'자동예약시간 : {self.tool_hour.text()}시{self.tool_min.text()}분{self.tool_sec.text()}초')


    def btn_tool_save(self):
        self.tool_hour.setText(self.tool_hour.text())
        self.tool_min.setText(self.tool_min.text())
        self.tool_sec.setText(self.tool_sec.text())
        print(f'자동예약시간 : {self.tool_hour.text()}시{self.tool_min.text()}분{self.tool_sec.text()}초로 변경되었습니다.')
        print(f'자동예약시간 : {self.tool_hour.text()}시{self.tool_min.text()}분{self.tool_sec.text()}초')
        myTool.close()

    def btn_tool_cancel(self):
        myTool.close()

# --- 예매 대기 쓰레드 --- 
class Worker_timeattack(QThread):  
         
    def run(self):
        sum = 0
        loader_text = '대기중'
        myWindow.loader.setText('')
        myWindow.loader.setVisible(True)
        
        time_attack_flag = False
        while myWindow.allstop != True:
            if sum < 5:
                for i in range(sum):
                    loader_text = loader_text + '.'
                myWindow.loader.setText(loader_text)
                sum += 1
            else:
                loader_text = '대기중'
                sum = 0
            time_A = myWindow.lbl_time.text()
            B = time_A.split(" ")
            B[0] = B[0].replace('시', '')
            B[1] = B[1].replace('분', '')
            B[2] = B[2].replace('초', '')
            time.sleep(1)
            # if int(B[0]) == 9 and int(B[1]) == 59 and int(B[2] >= 40):
            if int(B[0]) == int(myTool.tool_hour.text()) and int(B[1]) == int(myTool.tool_min.text()) and int(B[2] >= myTool.tool_sec.text()):
                myWindow.workflag = False
                myWindow.worker.start()
                time_attack_flag = True
                myWindow.servertime_stop_flag = True
                myWindow.loader.setVisible(False)
                break
        if time_attack_flag == True:
            self.quit()
            self.wait(5000)
            print('timeattack quit')

class Worker_servertime(QThread):  
         
    def run(self):

        while myWindow.allstop != True and myWindow.servertime_stop_flag != True:
            # server_time = myWindow.servertime_driver.find_element(By.XPATH,'//*[@id="time_area"]').text
            date = urllib.request.urlopen('http://www.sunvalley.co.kr').headers['Date']
            d = datetime.datetime.strptime(date, "%a, %d %b %Y %X GMT")
            d = d.replace(tzinfo=datetime.timezone.utc)
            d = d.astimezone()

            servertime_spl = d.strftime("%H시 %M분 %S초")
            # server_time_spl = server_time.split('일 ')
            myWindow.lbl_time.setText(servertime_spl)
            time.sleep(1)
        self.quit()
        self.wait(5000)
        # myWindow.servertime_driver.quit()
        print('servertime quit')
    
class Worker(QThread):

    def run(self):
        if myWindow.id_txt.text() != '' and myWindow.pwd_txt.text() != '':
        
            global driver         
            subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"') # 디버거 크롬 구동
            option = Options()
            option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            # options = webdriver.ChromeOptions()
            # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

            chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
            # print('Chrome Version', chrome_ver)
            try:
                driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
            except:
                path = chromedriver_autoinstaller.install(True)
                driver = webdriver.Chrome(path, options=option)

            driver.maximize_window()
            driver.implicitly_wait(10)
            driver.get("https://www.sunvalley.co.kr/main")
            
            req = driver.page_source
            soup=BeautifulSoup(req, 'html.parser')

            login_id = myWindow.id_txt.text()
            login_pwd = myWindow.pwd_txt.text()
            
            login = soup.select_one('#header > div.header-inner.in-sec > div.header-utilMenu > ul > li:nth-child(1) > a > span')
            print(login.get_text())

            if login.get_text() == '로그인':
                driver.get("https://www.sunvalley.co.kr/member/login")
                userId = driver.find_element(By.ID, 'usrId')
                userId.send_keys(login_id) # 로그인 할 계정 id
                userPwd = driver.find_element(By.ID, 'usrPwd')
                userPwd.send_keys(login_pwd) # 로그인 할 계정의 패스워드
                userPwd.send_keys(Keys.ENTER)
                time.sleep(1)
                driver.switch_to.alert.accept()
                driver.get("https://www.sunvalley.co.kr/reservation/golf")

            elif login.get_text() == '로그아웃':
                driver.get("https://www.sunvalley.co.kr/reservation/golf")
            
            # 동원
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="selectCoIdJ24"]'))).click()
            print('dongwon-sunvalley click')
            # driver.find_element(By.XPATH, '//*[@id="selectCoIdJ24"]').click()
            # 일죽
            # driver.find_element(By.XPATH, '//*[@id="selectCoIdJ23"]').click()
            # 설악
            # driver.find_element(By.XPATH, '//*[@id="selectCoIdJ21"]').click() 

        while myWindow.workflag == False:
            ### 날짜 클릭 - 이번 달인지 다음 달인지 체크 후 클릭 (이번달 A값, 다음달 B값) ###
            day_text = str(myWindow.day_box.text())
            day_text_mod = day_text.replace("-","")
            text_result = 'A' + day_text_mod
            text_result2 = 'B' + day_text_mod
            day_text_month = day_text.split('-')
            basetime_month = datetime.date.today().strftime('%m')
            # print(day_text_month[1])
            # print(basetime_month)
            time_text_s = str(myWindow.time_box_start.text())
            time_text_e = str(myWindow.time_box_end.text())
            time.sleep(0.2)

            while myWindow.allstop != True:
                if (day_text_month[1] == basetime_month) == True:
                    driver.find_element(By.XPATH, "//*[@id='" + text_result + "']").click()
                else:
                    driver.find_element(By.XPATH, "//*[@id='" + text_result2 + "']").click()
                # day_click = driver.find_element(By.XPATH, "//*[@id='" + text_result + "']")
                # print(day_click)
                # day_click.click()
                
                ### 시간대 텍스트 가져오기 ###
                
                print('예매 날짜 선택 : ', day_text)
                print('예매 지정 시간 : ', time_text_s, '~', time_text_e)

                ### tee-off가 있는지 체크 ###
                req = driver.page_source
                soup=BeautifulSoup(req, 'html.parser')
                course = soup.select_one('#tabCourseALL > div > div > table > tbody > tr > td')
                course_check = course.get_text()
                last_break_point = False

                if course_check != 'Tee-off 타임이 없습니다.':
                    print('Tee-off 타임이 있습니다.')
                    ### tee-off가 있으면 버튼을 찾음 ###
                    buttons = driver.find_elements_by_css_selector('[class="btn btn-res"]')

                    ### tee-off 시간 텍스트 구하는 곳 ###
                    # req = driver.page_source
                    # soup=BeautifulSoup(req, 'html.parser')
                    # crawl_time = soup.select('#tabCourseALL > div > div > table > tbody > tr > td:nth-child(4)')
                    
                    # new_list2 = []
                    
                    # for t in crawl_time:
                    #     if t not in new_list2:
                    #         new_list2.append(t)

                    # index_s = myWindow.time_box_start.currenttext()
                    # index_e = myWindow.time_box_start.findText(time_text_e, QtCore.Qt.MatchFixedString)
                    # i = index_s
                    # break_point = False
                    if len(buttons) != 0:
                        for button in buttons:
                            onclick_text = button.get_attribute('onclick')
                            onclick_splited = onclick_text.split(',')
                            onclick_splited2 = onclick_splited[4]
                            onclick_splited3 = onclick_splited2[1:6]
                            # 지정 시간대에 버튼이 있을 경우
                            if time_text_s <= onclick_splited3 and onclick_splited3 <= time_text_e:
                                print(onclick_splited3,'분 예매 가능')
                                button.click()
                                print('button clicked')

                                # last_btn = driver.find_element_by_css_selector('[class="btn btn-res03"]')
                                # last_btn.click()
                                element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="btn btn-res03"]')))
                                element.send_keys(Keys.ENTER)
                                print('element_button clicked')

                                # try:
                                #     print(element)
                                # except WebDriverException:
                                #     print('WebDriverException - element_button not clickable')

                                try:
                                    WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                                                'Timed out waiting for PA creation ' +
                                                                'confirmation popup to appear.')

                                    alert = driver.switch_to.alert
                                    print('alert : ', alert.text)
                                    alert.accept()
                                    # if alert.text.find('예약이 완료되었습니다.') != -1 :
                                    #   myWindow.lbl_info.setText(myWindow.time_box_start.itemText(i),'분 예매 완료')
                                    #   break_point = True
                                    #   break
                                    # else:
                                    #   myWindow.lbl_info.setText(myWindow.time_box_start.itemText(i),'분 예매 실패')
                                    #   return_break_point = True

                                    print(onclick_splited3,'분 예매 완료')
                                    last_break_point = True
                                    break
                                except TimeoutException:
                                    print("TimeoutException - no alert")
                                    print(onclick_splited3,'분 예매 실패')
                                    driver.get("https://www.sunvalley.co.kr/reservation/golf?sel=J24")
                                    # driver.get("https://www.sunvalley.co.kr/reservation/golf?sel=J23")

                                    break
                                    
                        # if break_point == True:
                        #     last_break_point = True
                        #     break
                        #elif re_break_point == True:
                        #    driver.get("https://www.sunvalley.co.kr/reservation/golf?sel=J24")
                        #    break
                    else:
                        print('예매 가능한 시간이 없습니다.')
                elif course_check == 'Tee-off 타임이 없습니다.':
                    print('Tee-off 타임이 없습니다.')
                if last_break_point == True:
                    break
                if myWindow.workflag == True:
                    print('예매가 중단되었습니다')
                    break

        # else:
        #     myWindow.lbl_info.setText('예매가 중단되었습니다.')
        #     break


if __name__ == "__main__":
   app = QApplication(sys.argv)
   # myWindow 라는 변수에 GUI 클래스 삽입
   myWindow = MyWindow()
   myTool = ToolWindow(myWindow)

   # GUI 창 보이기
   myWindow.show()
#########################
# 이벤트루프 진입전 작업할 부분
##########By.ATH, ###*##id 
# 이벤text_result입
   app.exec_()


         
    #텍스트 입력 되었는지 확인하는 경고창 필요 //해결
    #다음 월이 13월이면 1월로 변환  //필요없을듯
    #today와 다음월을 비교하여 A, B click link 구분  //해결
    #예매 가능 발견하면 무조건 무한루프 탈출 (현재) -> 발견해도 예약이 안되면 다른곳 발견 필요 //해결
    #쓰레드 종료되는지 확인(확인법?)  //해결
    #배포 -> 업데이트? //해결
    #배포 시 exe 파일 실행 후 webdriver 어떻게?  //해결

    #버그리포트
    #1. 오늘 월이 아닌 다음 월을 기준으로 예매 시 크롤링 데이터가 일치하지 않는 현상 //해결
    #-> 시간대를 크롤링하여 일치조건문 방식에서 시간 대 사이에 존재하는 시간을 선택하는 방식 //해결
    #2. 최종 예약 버튼 클릭시, Message: element click intercepted, is not clickable at point 오류 //해결
    #-> time.sleep에서 webdriverwait으로 변경, click 메소드에서 keys.enter 메소드로 변경 //해결
    #3. 210908_프로그램 예매대기 후 Worker가 실행될 때 종료되는 현상 //해결
    #-> Chrome Driver Version 이슈 같음, 크롬 드라이버 93버전으로 재설치 //해결

    #버전업
    #1. 로그인, 날짜 정보 입력 후 대기 누르면 지정된 서버시간에 자동으로 프로그램이 실행
    #2. 210908_로그인 정보 미 입력 시 미리 알림이 뜨게 변경
