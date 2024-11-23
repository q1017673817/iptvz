import time
import datetime
import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from queue import Queue
import requests
import re

task_queue = Queue()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

urls = [
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgaXA9IjExMS4yMjUuMS4xLzE2Ig%3D%3D", #河北
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcity%3A%22baoding%22%20%2Bcidr%3A111.225.1.1%2F16", #河北baoding
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bsubdivisions%3A%22henan%22%20%2Bcity%3Azhengzhou", #河南zhengzhou 
       ]

def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, headers=headers, timeout=5)
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
                ip_start_index = url.find("//") + 2
                ip_dot_start = url.find(".") + 1
                ip_index_second = url.find("/", ip_dot_start)
                base_url = url[:ip_start_index]  # http:// or https://
                ip_address = url[ip_start_index:ip_index_second]
                url_x = f"{base_url}{ip_address}"
    
                json_url = f"{url}"
                response = requests.get(json_url, timeout=5)
                json_data = response.json()
    
                try:
                    # 解析JSON文件，获取name和url字段
                    for item in json_data['data']:
                        if isinstance(item, dict):
                            name = item.get('name')
                            urlx = item.get('url')
                            if ',' in urlx:
                                urlx=f"aaaaaaaa"
                                
                            if 'http' in urlx or 'udp' in urlx or 'rtp' in urlx:
                            #if 'http' in urlx:
                                urld = f"{urlx}"
                            else:
                                urld = f"{url_x}{urlx}"
    
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
                                name = name.replace("CCTV赛事", "CCTV5+")
                                name = name.replace("南方卫视粤语节目9", "广东大湾区卫视")
                                name = name.replace("三沙卫视", "海南三沙卫视")
                                name = name.replace("兵团卫视", "新疆兵团卫视")
                                name = name.replace("内蒙古蒙语卫视", "内蒙古蒙语频道")
                                name = name.replace("南方卫视", "广东大湾区卫视")
                                name = name.replace("少儿卫视", "其他")
                                name = name.replace("延边卫视", "吉林延边卫视")
                                name = name.replace("旅游卫视", "海南卫视")
                                name = name.replace("福建东南卫视", "东南卫视")
                                name = name.replace("陽光卫视", "其他")
                                name = name.replace("1", "其他")
                                name = name.replace("2", "其他")
                                name = name.replace("3", "其他")
                                name = name.replace("5", "其他")
                                name = name.replace("6", "其他")
                                name = name.replace("7", "其他")
                                name = name.replace("8", "其他")
                                name = name.replace("9", "其他")
                                name = name.replace("10", "其他")
                                name = name.replace("3（牛哥）", "其他")
                                name = name.replace("1资讯", "凤凰卫视资讯台")
                                name = name.replace("2中文", "凤凰卫视中文台")
                                name = name.replace("TV1", "凤凰卫视中文台")
                                name = name.replace("3XG", "凤凰卫视香港台")
                                name = name.replace("CETV1中教", "CETV1")
                                name = name.replace("DTV1", "其他")
                                name = name.replace("DTV2", "其他")
                                name = name.replace("DTV3", "其他")
                                name = name.replace("DTV4", "其他")
                                name = name.replace("梅州1", "其他")
                                name = name.replace("梅州2", "其他")
                                name = name.replace("中国教育1", "CETV1")
                                name = name.replace("南方1", "广东经济科教")
                                name = name.replace("南方4", "广东影视频道")
                                name = name.replace("吉林市1", "吉林新闻综合")
                                name = name.replace("影视剧场1", "CHC影迷电影")
                                name = name.replace("影视剧场2", "CHC动作电影")
                                name = name.replace("珠江台粤语节目1", "广东珠江粤语")
                                name = name.replace("广州台粤语节目2", "广东广州粤语")
                                name = name.replace("广东新闻粤语节目3", "广东新闻粤语")
                                name = name.replace("广东公共粤语节目4", "广东民生频道")
                                if 'udp' not in urld or 'rtp' not in urld:
                                    results.append(f"{name},{urld}")
                except:
                    continue
            except:
                continue
    except:
        continue

results = set(results)   # 去重得到唯一的URL列表
results = sorted(results)
with open("itv.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)
print("频道列表文件itv.txt获取完成！")


channels = []
with open('itv.txt', 'r', encoding='utf-8') as file:
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
now = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8)
current_time = now.strftime("%Y/%m/%d %H:%M")

# 生成iptv.txt文件
with open('iptv.txt', 'w', encoding='utf-8') as file:
    file.write(f"央视频道{current_time}更新,#genre#\n")
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

os.remove("itv.txt")
