import re
import requests
from bs4 import BeautifulSoup

def get_course_detail(course_serial_number):
    # 定義目標URL
    url = 'https://cis.ncu.edu.tw/Course/main/support/courseDetail.html?crs=' + course_serial_number

    # 設置請求頭
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'zh-TW,zh;q=0.9'
    }

    # 發送HTTP請求
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    def get_value_by_label(label):
        td = soup.find('td', class_='subTitle', string=label)
        if td:
            next_td = td.find_next_sibling('td')
            if next_td:
                # 排除不需要的部分
                for span in next_td.find_all('span', class_='engclass'):
                    span.decompose()
                return next_td.get_text(strip=True)
        return None

    course_name = get_value_by_label('課程名稱/備註')
    course_code = get_value_by_label('流水號  / 課號')
    course_time = get_value_by_label('時間/教室')
    course_teacher = get_value_by_label('授課教師')

    # 提取課號
    match = re.search(r'[A-Za-z0-9]+ - [A-Za-z*]', course_code)
    if match:
        course_code = match.group()
    else:
        print('未知課號\n')
        return

    enrollment_limit = get_value_by_label('人數限制')

    # 查找特定內容出現的次數
    td_elements = soup.find_all('td')

    selected_count = 0 # 中選人數
    for index in range(len(td_elements)):
        text = td_elements[index].get_text(strip=True)
        if text == '中選' or text == '中選(初選)' or text == '人工加選':
            selected_count += 1

    # 處理時間格式
    if course_time:
        time_matches = re.findall(r'星期[一二三四五六日]\s*\w+', course_time)
        time_slots = {}
        for match in time_matches:
            day, period = re.split(r'\s+', match.strip())
            if day in time_slots:
                time_slots[day].append(period)
            else:
                time_slots[day] = [period]

        course_time = ' / '.join([f"{day} {'/'.join(periods)}" for day, periods in time_slots.items()])

    print(f'課程名稱: {course_name} {course_code}')
    print(f'授課教師: {course_teacher}')
    print(f'課堂時間: {course_time}')
    print(f'人數限制: {enrollment_limit}')
    print(f'中選人數: {selected_count}')

    total_remaining_slots = int(enrollment_limit) - int(selected_count)
    remaining_slots = total_remaining_slots
    accumulated_count = 0 # 累積人數

    for priority in range(1, 10):
        count = 0
        for index in range(len(td_elements)):
            if td_elements[index].get_text(strip=True) == str(priority) and td_elements[index + 1].get_text(strip=True) == '待分發':
                count += 1
        accumulated_count += count
        if count == 0 and remaining_slots > 0:
            print(f'第{priority}志願累積人數: {accumulated_count}, 機率: 100.00%')
            continue
        if count == 0:
            count = 1
        probability = remaining_slots / count * 100
        if probability > 100:
            probability = 100
        elif probability < 0:
            probability = 0
        print(f'第{priority}志願累積人數: {accumulated_count}, 機率: {probability:.2f}%')
        remaining_slots -= count
        if accumulated_count >= total_remaining_slots * 2:
            break
    print()

# 輸入你想要的課程流水號(4或5位號碼)
pe_course_numbers = ["1041", "1043"]
language_course_numbers = ["0001", "0002"]
general_course_numbers = ["9007", "9018"]

print("<體育課程>\n")
for serial_number in pe_course_numbers:
    get_course_detail(serial_number)

print("<語言課程>\n")
for serial_number in language_course_numbers:
    get_course_detail(serial_number)

print("<通識課程>\n")
for serial_number in general_course_numbers:
    get_course_detail(serial_number)