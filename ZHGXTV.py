import time
import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import threading
import re
###urls城市根据自己所处地理位置修改
urls = [
    "https://www.zoomeye.org/searchResult?q=ZHGXTV%20%2Bcity%3A%22zhengzhou%22",#河南zhengzhou
    "https://www.zoomeye.org/searchResult?q=ZHGXTV%20%2Bcity%3A%22jinan%22", #山东jinan
]

def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/ZHGXTV/Public/json/live_interface.txt"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None


results = []

for url in urls:
    try:
        # 创建一个Chrome WebDriver实例
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    
        driver = webdriver.Chrome(options=chrome_options)
        # 使用WebDriver访问网页
        driver.get(url)  # 将网址替换为你要访问的网页地址
        time.sleep(10)
        # 获取网页内容
        page_content = driver.page_source
    
        # 关闭WebDriver
        driver.quit()
    
        # 查找所有符合指定格式的网址
        pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
        urls_all = re.findall(pattern, page_content)
        # urls = list(set(urls_all))  # 去重得到唯一的URL列表
        urls = set(urls_all)  # 去重得到唯一的URL列表
        x_urls = []
        for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
            url = url.strip()
            ip_start_index = url.find("//") + 2
            ip_end_index = url.find(":", ip_start_index)
            ip_dot_start = url.find(".") + 1
            ip_dot_second = url.find(".", ip_dot_start) + 1
            ip_dot_three = url.find(".", ip_dot_second) + 1
            base_url = url[:ip_start_index]  # http:// or https://
            ip_address = url[ip_start_index:ip_dot_three]
            port = url[ip_end_index:]
            ip_end = "1"
            modified_ip = f"{ip_address}{ip_end}"
            x_url = f"{base_url}{modified_ip}{port}"
            x_urls.append(x_url)
        urls = set(x_urls)  # 去重得到唯一的URL列表
    
        valid_urls = []
        #   多线程获取可用url
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for url in urls:
                url = url.strip()
                modified_urls = modify_urls(url)
                for modified_url in modified_urls:
                    futures.append(executor.submit(is_url_accessible, modified_url))
    
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_urls.append(result)
    
        for url in valid_urls:
            print(url)
        # 遍历网址列表，获取JSON文件并解析
        for url in valid_urls:
            try:
                # 发送GET请求获取JSON文件，设置超时时间为0.5秒
                json_url = f"{url}"
                response = requests.get(json_url, timeout=1.5)
                json_data = response.content.decode('utf-8')
                try:
                    # 按行分割数据
                    lines = json_data.split('\n')
                    for line in lines:
                       if 'udp' not in line and 'rtp' not in line:
                        line = line.strip()
                        if line:
                            name, channel_url = line.split(',')
                            urls = channel_url.split('/', 3)
                            url_data = json_url.split('/', 3)
                            if len(urls) >= 4:
                                urld = (f"{urls[0]}//{url_data[2]}/{urls[3]}")
                            else:
                                urld = (f"{urls[0]}//{url_data[2]}")
                            print(f"{name},{urld}")
                            if name and urld:
                                # 删除特定文字
                                name = name.replace("cctv", "CCTV")
                                name = name.replace("中央", "CCTV")
                                name = name.replace("央视", "CCTV")
                                name = name.replace("高清", "")
                                name = name.replace("超高", "")
                                name = name.replace("HD", "")
                                name = name.replace("标清", "")
                                name = name.replace("频道", "")
                                name = name.replace("-", "")
                                name = name.replace(" ", "")
                                name = name.replace("PLUS", "+")
                                name = name.replace("＋", "+")
                                name = name.replace("(", "")
                                name = name.replace(")", "")
                                name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                                name = name.replace("CCTV1综合", "CCTV-1")
                                name = name.replace("CCTV2财经", "CCTV-2")
                                name = name.replace("CCTV3综艺", "CCTV-3")
                                name = name.replace("CCTV4国际", "CCTV-4")
                                name = name.replace("CCTV4中文国际", "CCTV-4")
                                name = name.replace("CCTV4欧洲", "CCTV-4")
                                name = name.replace("CCTV5体育", "CCTV-5")
                                name = name.replace("CCTV6电影", "CCTV-6")
                                name = name.replace("CCTV7军事", "CCTV-7")
                                name = name.replace("CCTV7军农", "CCTV-7")
                                name = name.replace("CCTV7农业", "CCTV-7")
                                name = name.replace("CCTV7国防军事", "CCTV-7")
                                name = name.replace("CCTV8电视剧", "CCTV-8")
                                name = name.replace("CCTV9记录", "CCTV-9")
                                name = name.replace("CCTV9纪录", "CCTV-9")
                                name = name.replace("CCTV10科教", "CCTV-10")
                                name = name.replace("CCTV11戏曲", "CCTV-11")
                                name = name.replace("CCTV12社会与法", "CCTV-12")
                                name = name.replace("CCTV13新闻", "CCTV-13")
                                name = name.replace("CCTV新闻", "CCTV-13")
                                name = name.replace("CCTV14少儿", "CCTV-14")
                                name = name.replace("CCTV15音乐", "CCTV-15")
                                name = name.replace("CCTV16奥林匹克", "CCTV-16")
                                name = name.replace("CCTV17农业农村", "CCTV-17")
                                name = name.replace("CCTV17农业", "CCTV-17")
                                name = name.replace("CCTV5+体育赛视", "CCTV-5+")
                                name = name.replace("CCTV5+体育赛事", "CCTV-5+")
                                name = name.replace("CCTV5+体育", "CCTV-5+")
                                name = name.replace("CCTV1", "CCTV-1")
                                name = name.replace("CCTV2", "CCTV-2")
                                name = name.replace("CCTV3", "CCTV-3")
                                name = name.replace("CCTV4", "CCTV-4")
                                name = name.replace("CCTV5", "CCTV-5")
                                name = name.replace("CCTV6", "CCTV-6")
                                name = name.replace("CCTV7", "CCTV-7")
                                name = name.replace("CCTV8", "CCTV-8")
                                name = name.replace("CCTV9", "CCTV-9")
                                name = name.replace("CCTV10", "CCTV-10")
                                name = name.replace("CCTV11", "CCTV-11")
                                name = name.replace("CCTV12", "CCTV-12")
                                name = name.replace("CCTV13", "CCTV-13")
                                name = name.replace("CCTV14", "CCTV-14")
                                name = name.replace("CCTV15", "CCTV-15")
                                name = name.replace("CCTV16", "CCTV-16")
                                name = name.replace("CCTV17", "CCTV-17")
                                name = name.replace("CCTV5+", "CCTV-5+")
                                name = name.replace("CCTV风云足球", "CCTV-风云足球")
                                name = name.replace("CCTV怀旧剧场", "CCTV-怀旧剧场")
                                name = name.replace("CCTV电视指南", "CCTV-电视指南")
                                name = name.replace("CCTV第一剧场", "CCTV-第一剧场")
                                name = name.replace("CCTV风云剧场", "CCTV-风云剧场")
                                name = name.replace("CCTV风云足球", "CCTV-风云足球")
                                name = name.replace("CCTV风云音乐", "CCTV-风云音乐")
                                name = name.replace("CCTV高尔夫网球", "CCTV-高尔夫网球")
                                name = name.replace("上海卫视", "东方卫视")
                                name = name.replace("奥运匹克", "")
                                name = name.replace("军农", "")
                                name = name.replace("回放", "")
                                name = name.replace("CCTV5卡", "CCTV-5")
                                name = name.replace("CCTV5赛事", "CCTV-5")
                                results.append(f"{name},{urld}")
                except:
                    continue
            except:
                continue
    except:
        continue

results = set(results)   # 去重得到唯一的URL列表
results = sorted(results)
with open("ZHGXTV0.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)

with open('ZHGXTV0.txt', 'r', encoding='utf-8') as file:
#从整理好的文本中按类别进行特定关键词提取
 keywords = ['hls']  # 需要提取的关键字列表
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('ZHGXTV0.txt', 'r', encoding='utf-8') as file, open('ZHGXTV1.txt', 'w', encoding='utf-8') as a:    #####定义临时文件名
    a.write('\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         a.write(line)  # 将该行写入输出文件 

channels = []
with open('ZHGXTV1.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if line:
            channel, address = line.split(',')
            channels.append((channel, address))
# 对频道进行排序
channels.sort()
# 自定义排序函数，提取频道名称中的数字并按数字排序
def channel_key(channel):
    match = re.search(r'\d+', channel)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字

# 对频道进行排序
channels.sort(key=lambda x: channel_key(x[0]))

# 生成iptv.txt文件
with open('gxtv.txt', 'w', encoding='utf-8') as file:
    file.write('央视频道,#genre#\n')
    for channel, address in channels:
        if 'cctv' in channel.lower():
            file.write(f'{channel},{address}\n')
    file.write('卫视频道,#genre#\n')
    for channel, address in channels:
        if '卫视' in channel:
            file.write(f'{channel},{address}\n')
    file.write('其他频道,#genre#\n')
    for channel, address in channels:
        if 'cctv' not in channel.lower() and '卫视' not in channel:
            file.write(f'{channel},{address}\n')
    file.write(f"{now_today}更新,#genre#\n")

os.remove("ZHGXTV0.txt")
os.remove("ZHGXTV1.txt")

