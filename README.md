# auto_scrapy

selenium브라우저를 GUI 설정에 의해서 
- url 이동
- frame 지정 
- click 
- input 입력, 
- text 가져오기 
- 선택자 xpath, id, class, query_selector 
지정한 작업을 순차적으로 실행할 수 있도록 GUI 환경


개발환경
- windows 10
- Python 3.10.7
- QT5
- Selenium
pip install -r requirements.txt

1. selenium 다운로드
2. config 파일에 selenium_path와 저장시 생성될 scrapy_file_path를 설정
config = {
    'encrypt_key': '',
    'selenium_path': './chromedriver.exe',
    'scrapy_file_path': 'D:/',
}

<img width="450px" height="300px" src="https://user-images.githubusercontent.com/69671250/207306483-c649e0b2-30d4-4397-a5dd-f6475a50e873.PNG">
<img width="450px" height="300px" src="https://user-images.githubusercontent.com/69671250/207306491-93933b0e-c453-43c8-aa72-d7f4f4ff6356.PNG">


<img src="https://user-images.githubusercontent.com/69671250/207466376-8c004bfc-f036-48f0-9ea0-1c2158f9f6b5.gif">
<img src="https://user-images.githubusercontent.com/69671250/207304805-524137ec-1526-47bc-ae8b-2572115433d2.gif">
