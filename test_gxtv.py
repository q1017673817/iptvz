import eventlet
eventlet.monkey_patch()

import time
import datetime
import threading
import os
import re
import concurrent.futures
from queue import Queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

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
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

results = []
urls_all = []
with open('测试.ip', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        url = line.strip()
        url = f"http://{url}"
        urls_all.append(url)        
    urls_1 = set(urls_all)  # 去重得到唯一的URL列表

    x_urls = []
    urls_x = []
    for url in urls_1:  # 对urls进行处理，ip第四位修改为1，并去重
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
        modified_ip = f"{ip_address}{ip_end}{port}"
        urls_x.append(modified_ip)
        x_url = f"{base_url}{modified_ip}"
        x_urls.append(x_url)
        
    urls_a = sorted(set(urls_x))
    with open("更新光迅源.ip", 'w', encoding='utf-8') as file:
        for url in urls_a:
            file.write(url + "\n")
    urls_2 = sorted(set(x_urls))  # 去重得到唯一的URL列表

    valid_urls = []  # 多线程获取可用url
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for url in urls_2:
            url = url.strip()
            modified_urls = modify_urls(url)
            for modified_url in modified_urls:
                futures.append(executor.submit(is_url_accessible, modified_url))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)
                print(result)
        valid_urls = sorted(set(valid_urls))

        urls = []
        for valid_url in valid_urls:
            url_e = valid_url.find("Z") - 1
            url = valid_url[:url_e]
            ip_start_index = url.find("//") + 2
            ip_end_index = url.find(":", ip_start_index)
            ip_dot_start = url.find(".") + 1
            ip_dot_second = url.find(".", ip_dot_start) + 1
            ip_dot_three = url.find(".", ip_dot_second) + 1
            base_url = url[:ip_start_index]  # http:// or https://
            ip_address = url[ip_start_index:ip_dot_three]
            port = url[ip_end_index:]
            ip_end = "1"
            modified_ip = f"{ip_address}{ip_end}{port}"
            urls.append(modified_ip)
        urls_b = sorted(set(urls))
        with open("可用光迅源.ip", 'w', encoding='utf-8') as file:
            for url in urls_b:
                file.write(url + "\n")
       
    # 遍历网址列表，获取JSON文件并解析
    for url in valid_urls:
        try:
            # 发送GET请求获取JSON文件，设置超时时间为0.5秒
            json_url = f"{url}"
            response = requests.get(json_url, timeout=1)
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
                                urld = f"{urls[0]}//{url_data[2]}/{urls[3]}"
                            else:
                                urld = f"{urls[0]}//{url_data[2]}"
                          #  print(f"{name},{urld}")

                            if name and urld:
                                # 删除特定文字
                                name = name.replace("cctv", "CCTV")
                                name = name.replace("中央", "CCTV")
                                name = name.replace("央视", "CCTV")
                                name = name.replace("高清", "")
                                name = name.replace("超清", "")
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
                                name = name.replace("CCTV4广电", "CCTV4")
                                name = name.replace("CCTV4中文国际", "CCTV4")
                                name = name.replace("CCTV4欧洲", "CCTV4")
                                name = name.replace("CCTV5体育", "CCTV5")
                                name = name.replace("CCTV6电影", "CCTV6")
                                name = name.replace("CCTV7军事", "CCTV7")
                                name = name.replace("CCTV7军农", "CCTV7")
                                name = name.replace("CCTV7农业", "CCTV7")
                                name = name.replace("军农", "")
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
                                name = name.replace("CCTV17军农", "CCTV17")
                                name = name.replace("CCTV17军事", "CCTV17")
                                name = name.replace("CCTV5+体育赛视", "CCTV5+")
                                name = name.replace("CCTV5+体育赛事", "CCTV5+")
                                name = name.replace("CCTV5+体育", "CCTV5+")
                                name = name.replace("CCTV足球", "CCTV风云足球")
                                name = name.replace("上海卫视", "东方卫视")
                                name = name.replace("奥运匹克", "")
                                name = name.replace("军农", "")
                                name = name.replace("回放", "")
                                name = name.replace("测试", "")
                                name = name.replace("CCTV5卡", "CCTV5")
                                name = name.replace("CCTV5赛事", "CCTV5")
                                name = name.replace("CCTV教育", "CETV1")
                                name = name.replace("中国教育1", "CETV1")
                                name = name.replace("CETV1中教", "CETV1")
                                name = name.replace("中国教育2", "CETV2")
                                name = name.replace("中国教育4", "CETV4")
                                name = name.replace("CCTV5+体育赛视", "CCTV5+")
                                name = name.replace("CCTV5+体育赛事", "CCTV5+")
                                name = name.replace("CCTV5+体育", "CCTV5+")
                                name = name.replace("CCTV赛事", "CCTV5+")
                                name = name.replace("CCTV教育", "CETV1")
                                name = name.replace("CCTVnews", "CGTN")
                                name = name.replace("1资讯", "凤凰资讯台")
                                name = name.replace("2中文", "凤凰台")
                                name = name.replace("3XG", "香港台")
                                name = name.replace("上海卫视", "东方卫视")
                                name = name.replace("全纪实", "乐游纪实")
                                name = name.replace("金鹰动画", "金鹰卡通")
                                name = name.replace("河南新农村", "河南乡村")
                                name = name.replace("河南法制", "河南法治")
                                name = name.replace("文物宝库", "河南收藏天下")
                                name = name.replace("梨园", "河南戏曲")
                                name = name.replace("梨园春", "河南戏曲")
                                name = name.replace("吉林综艺", "吉视综艺文化")
                                name = name.replace("BRTVKAKU", "BRTV卡酷少儿")
                                name = name.replace("kaku少儿", "BRTV卡酷少儿")
                                name = name.replace("纪实科教", "BRTV纪实科教")
                                name = name.replace("北京卡通", "BRTV卡酷少儿")
                                name = name.replace("卡酷卡通", "BRTV卡酷少儿")
                                name = name.replace("卡酷动画", "BRTV卡酷少儿")
                                name = name.replace("佳佳动画", "嘉佳卡通")
                                name = name.replace("CGTN今日世界", "CGTN")
                                name = name.replace("CGTN英语", "CGTN")
                                name = name.replace("ICS", "上视ICS外语频道")
                                name = name.replace("法制天地", "法治天地")
                                name = name.replace("都市时尚", "都市剧场")
                                name = name.replace("上海炫动卡通", "哈哈炫动")
                                name = name.replace("炫动卡通", "哈哈炫动")
                                name = name.replace("经济科教", "TVB星河")
                                name = name.replace("回放", "")
                                name = name.replace("测试", "")
                                name = name.replace("旅游卫视", "海南卫视")
                                name = name.replace("福建东南卫视", "东南卫视")
                                name = name.replace("福建东南", "东南卫视")
                                name = name.replace("南方卫视粤语节目9", "广东大湾区频道")
                                name = name.replace("内蒙古蒙语卫视", "内蒙古蒙语频道")
                                name = name.replace("南方卫视", "广东大湾区频道")
                                name = name.replace("中国教育1", "CETV1")
                                name = name.replace("南方1", "广东经济科教")
                                name = name.replace("南方4", "广东影视频道")
                                name = name.replace("吉林市1", "吉林新闻综合")
                                name = name.replace("家庭影院", "CHC家庭影院")
                                name = name.replace("动作电影", "CHC动作电影")
                                name = name.replace("影迷电影", "CHC影迷电影")
                                results.append(f"{name},{urld}")
            except:
                continue
        except:
            continue

results = sorted(set(results))   # 去重得到唯一的URL列表
with open("gxtv0.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)

with open('gxtv0.txt', 'r', encoding='utf-8') as file:
#从整理好的文本中按类别进行特定关键词提取
 keywords = ['hls']  # 需要提取的关键字列表
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('gxtv0.txt', 'r', encoding='utf-8') as file, open('gxtv1.txt', 'w', encoding='utf-8') as a:    #####定义临时文件名
    a.write('\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         a.write(line)  # 将该行写入输出文件        
         
task_queue = Queue()
results = []
channels = []
error_channels = []
with open("gxtv1.txt", 'r', encoding='utf-8') as file:
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
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url,timeout=1).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url,timeout=1).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                # print(f"文件大小：{file_size} 字节")
                download_speed = file_size / response_time / 1024
                # print(f"下载速度：{download_speed:.3f} kB/s")
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                #print(f"标准化后的速率：{normalized_speed:.3f} MB/s")
                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
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
# 自定义排序函数，提取频道名称中的数字并按数字排序
def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字
# 对频道进行排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
results.sort(key=lambda x: channel_key(x[0]))
now = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8)
current_time = now.strftime("%Y/%m/%d %H:%M")
# 生成iptv.txt文件
with open('2.txt', 'w', encoding='utf-8') as file:       
    for result in results:
        channel_name, channel_url, speed = result
        file.write(f"{channel_name},{channel_url}\n")
#############     
with open('2.txt', 'r', encoding='utf-8') as file:
#从整理好的文本中按类别进行特定关键词提取#############################################################################################
 keywords = ['CCTV', '风云剧场', '兵器', '女性', '地理', '央视文化', '风云音乐', '怀旧剧场', '第一剧场']  # 需要提取的关键字列表
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('a.txt', 'w', encoding='utf-8') as a:    #####定义临时文件名
    a.write(f"央视频道{current_time}更新,#genre#\n")                                                                 #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         a.write(line)  # 将该行写入输出文件 

#############
keywords = ['卫视']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('b.txt', 'w', encoding='utf-8') as b:    #####定义临时文件名
    b.write('\n卫视频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:        
        if re.search(pattern, line):  # 如果行中有任意关键字
         b.write(line)  # 将该行写入输出文件
         
##############   
keywords = [',']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('z.txt', 'w', encoding='utf-8') as z:    #####定义临时文件名
    z.write('\n其他频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         z.write(line)  # 将该行写入输出文件                    

############
file_contents = []
file_paths = ["a.txt","b.txt","z.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 写入合并后的文件
with open("去重.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

# 原始顺序去重
# 打开文档并读取所有行 
with open('去重.txt', 'r', encoding="utf-8") as file:
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
with open('测试结果gxtv.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)

os.remove("测试.ip")
os.remove("gxtv0.txt")
os.remove("gxtv1.txt")
os.remove("a.txt")
os.remove("b.txt")
os.remove("2.txt")
os.remove("z.txt")
os.remove("去重.txt")
print("任务运行完毕")
