import time
import datetime
import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from queue import Queue
import requests
import threading
import eventlet
import re
###urls城市根据自己所处地理位置修改
urls = [
    "https://www.zoomeye.org/searchResult?q=ZHGXTV%20%2Bcity%3A%22changsha%22", #湖南changsha
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
        response = requests.get(url, timeout=3)
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
                                name = name.replace("CCTV1综合", "CCTV1")
                                name = name.replace("CCTV2财经", "CCTV2")
                                name = name.replace("CCTV3综艺", "CCTV3")
                                name = name.replace("CCTV4国际", "CCTV4")
                                name = name.replace("CCTV4中文国际", "CCTV4")
                                name = name.replace("CCTV4欧洲", "CCTV4")
                                name = name.replace("CCTC14少儿", "CCTV14")
                                name = name.replace("CCTV5体育", "CCTV5")
                                name = name.replace("CCTV6电影", "CCTV6")
                                name = name.replace("CCTV7军事", "CCTV7")
                                name = name.replace("CCTV7军农", "CCTV7")
                                name = name.replace("CCTV7农业", "CCTV7")
                                name = name.replace("CCTV7国防军事", "CCTV7")
                                name = name.replace("CCTV8电视剧", "CCTV8")
                                name = name.replace("CCTV9记录", "CCTV9")
                                name = name.replace("CCTV9纪录", "CCTV9")
                                name = name.replace("CCTV10科教", "CCTV10")
                                name = name.replace("CCTV11戏曲", "CCTV11")
                                name = name.replace("CCTV12社会与法", "CCTV12")
                                name = name.replace("CCTV13新闻", "CCTV13")
                                name = name.replace("CCTV新闻", "CCTV13")
                                name = name.replace("CCTV14少儿", "CCTV14")
                                name = name.replace("CCTV少儿", "CCTV14")
                                name = name.replace("CCTV15音乐", "CCTV15")
                                name = name.replace("CCTV16奥林匹克", "CCTV16")
                                name = name.replace("CCTV17农业农村", "CCTV17")
                                name = name.replace("CCTV17农业", "CCTV17")
                                name = name.replace("CCTV5+体育赛视", "CCTV5+")
                                name = name.replace("CCTV5+体育赛事", "CCTV5+")
                                name = name.replace("CCTV5+体育", "CCTV5+")
                                name = name.replace("回放", "")
                                name = name.replace("测试", "")
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

file_contents = []
file_paths = ["itv.txt", "ZHGXTV1.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 写入合并后的文件
with open("iptv0.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

with open('iptv0.txt', 'r', encoding="utf-8") as file:
 lines = file.readlines()
 
# 使用列表来存储唯一的行的顺序 
 unique_lines = [] 
 seen_lines = set() 

# 遍历每一行，如果是新的就加入unique_lines 
for line in lines:
 if line not in seen_lines:
  unique_lines.append(line)
  seen_lines.add(line)

# 将唯一的行写入新的文档 
with open('iptv1.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)

eventlet.monkey_patch()

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []

channels = []
error_channels = []

with open("iptv1.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            channels.append((channel_name, channel_url))

# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            response = requests.get(channel_url, timeout=1)
            if response.status_code == 200:
                channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
                lines = requests.get(channel_url,timeout=1).text.strip().split('\n')  # 获取m3u8文件内容
                ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀

                file_size = 0
                start_time = time.time()
                # 多获取的视频数据进行5秒钟限制
                with eventlet.Timeout(5, False):
                    for i in range(len(ts_lists)):
                        ts_url = channel_url_t + ts_lists[i]  # 拼接单个视频片段下载链接
                        response = requests.get(ts_url, stream=True, timeout=1)
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                file_size += len(chunk)
                        response.close()
                end_time = time.time()
                response_time = end_time - start_time
                if response_time >=5:
                    file_size = 0
                download_speed = file_size / response_time / 1024
                normalized_speed =download_speed / 1024  # 将速率从kB/s转换为MB/s
                ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接
                if normalized_speed >= 0.8:
                    if file_size >= 3000000:
                        result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                        results.append(result)
                        numberx = (len(results) + len(error_channels)) / len(channels) * 100
                        print(f"可用频道：{len(results)} , 网速：{normalized_speed:.3f} MB/s , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
                    else:
                        error_channel = channel_name, channel_url
                        error_channels.append(error_channel)
                        numberx = (len(results) + len(error_channels)) / len(channels) * 100
                        print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} , 网速：{normalized_speed:.3f} MB/s , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
                else:
                    error_channel = channel_name, channel_url
                    error_channels.append(error_channel)
                    numberx = (len(results) + len(error_channels)) / len(channels) * 100
                    print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} , 网速：{normalized_speed:.3f} MB/s , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
            else:
                error_channel = channel_name, channel_url
                error_channels.append(error_channel)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 10
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True) 
    t.start()

# 添加下载任务到队列
for channel in channels:
    task_queue.put(channel)

# 等待所有任务完成
task_queue.join()


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字

# 对频道进行排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
results.sort(key=lambda x: channel_key(x[0]))
now_today = datetime.date.today()

# 将结果写入文件
with open("itvs.txt", 'w', encoding='utf-8') as file:
    for result in results:
        channel_name, channel_url, speed = result
        file.write(f"{channel_name},{channel_url}\n")

result_counter = 30  # 每个频道需要的个数

with open("iptv.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
                
    file.write(f"{now_today}更新,#genre#\n")
    
os.remove("ZHGXTV0.txt")
os.remove("ZHGXTV1.txt")
os.remove("itv.txt")
os.remove("iptv0.txt")
os.remove("iptv1.txt")
