import httpx
from bs4 import BeautifulSoup
import time

def crawl_notices():
    url = 'https://www.gachon.ac.kr/kor/7986/subview.do'
    # httpx를 사용하여 웹 페이지로부터 HTML 가져오기
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()  # 네트워크 오류 발생 시 예외 처리
    
    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(response.text, 'html.parser')

    # 원하는 데이터 추출
    link_title = soup.find_all('td','td-subject')

    notices = []
    for num in range(5):
        notices.append(link_title[num].get_text().strip())
    
    return notices

def crawl_academic_schedule():
    url = 'https://www.gachon.ac.kr/kor/1075/subview.do'
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()  # 네트워크 오류 발생 시 예외 처리

    soup = BeautifulSoup(response.text, 'html.parser')

    target = soup.find('div', 'sche-comt')
    tbody = target.find('tbody')
    tr = tbody.find_all('tr')

    schedule = []
    for num in range(len(tr)):
        schedule.append(tr[num].get_text().strip())

    return schedule

def crawl_library_seats(type='READING', libno='2'):
    url = 'https://lib.gachon.ac.kr/main/seatAjax'
    data = {
        'type': type,
        'libno': libno,
        'time': int(time.time()*1000)
    }

    with httpx.Client() as client:
        response = client.get(url, params=data)
        response.raise_for_status()

    body = response.json()

    return body

def crawl_cafeteria_menu():
    url = 'https://www.gachon.ac.kr/kor/7350/subview.do'
    # httpx를 사용하여 웹 페이지로부터 HTML 가져오기
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    
    link_title = soup.find("div", {"class": "table_1"}).find_all(text=True)
    
    menu = []
    for num in range(len(link_title)):
        menu.append(link_title[num].get_text().strip())
    
    return menu
