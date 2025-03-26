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
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)
    return modified_urls

def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=1.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

results = []
urls_all = []
with open('酒店高清.ip', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            url = line.strip()
            url = f"http://{url}"
            urls_all.append(url)
        urls = set(urls_all)  # 去重得到唯一的URL列表
        x_urls = []
        for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
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
                response = requests.get(json_url, timeout=2)
                json_data = response.json()
    
                try:
                    # 解析JSON文件，获取name和url字段
                    for item in json_data['data']:
                        if isinstance(item, dict):
                            name = item.get('name')
                            urlx = item.get('url')
                            if ',' in urlx:
                                urlx=f"aaaaaaaa"
                                
                            #if 'http' in urlx or 'udp' in urlx or 'rtp' in urlx:
                            if 'http' in urlx:
                                urld = f"{urlx}"
                            else:
                                urld = f"{url_x}{urlx}"
    
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
                                name = name.replace("K1", "")
                                name = name.replace("K2", "")
                                name = name.replace("W", "")
                                name = name.replace("w", "")
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
                                name = name.replace("文物宝库", "收藏天下")
                                name = name.replace("梨园", "河南戏曲")
                                name = name.replace("梨园春", "河南戏曲")
                                name = name.replace("吉林综艺", "吉视综艺文化")
                                name = name.replace("BRTVKAKU", "卡酷少儿")
                                name = name.replace("kaku少儿", "卡酷少儿")
                                name = name.replace("北京卡通", "卡酷少儿")
                                name = name.replace("卡酷卡通", "卡酷少儿")
                                name = name.replace("卡酷动画", "卡酷少儿")
                                name = name.replace("佳佳动画", "嘉佳卡通")
                                name = name.replace("CGTN今日世界", "CGTN")
                                name = name.replace("CGTN英语", "CGTN")
                                name = name.replace("ICS", "上视ICS外语频道")
                                name = name.replace("法制天地", "法治天地")
                                name = name.replace("都市时尚", "都市剧场")
                                name = name.replace("上海炫动卡通", "哈哈炫动")
                                name = name.replace("炫动卡通", "哈哈炫动")
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

                                if 'udp' not in urld or 'rtp' not in urld:
                                    results.append(f"{name},{urld}")
                except:
                    continue
            except:
                continue

results = sorted(set(results))   # 去重得到唯一的URL列表
with open("iptv0.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)

with open('iptv0.txt', 'r', encoding='utf-8') as file:
#从整理好的文本中按类别进行特定关键词提取
 keywords = ['tsfile']  # 需要提取的关键字列表
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('iptv0.txt', 'r', encoding='utf-8') as file, open('iptv1.txt', 'w', encoding='utf-8') as a:    #####定义临时文件名
    a.write('\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         a.write(line)  # 将该行写入输出文件        

# 线程安全的队列，用于存储下载任务
task_queue = Queue()
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

with open('1.txt', 'w', encoding='utf-8') as file:       
    for result in results:
        channel_name, channel_url, speed = result
        file.write(f"{channel_name},{channel_url}\n")

###############################        
with open('1.txt', 'r', encoding='utf-8') as file:
#从整理好的文本中按类别进行特定关键词提取#############################################################################################
 keywords = ['CCTV','风云剧场','怀旧剧场','第一剧场','兵器','女性','地理','央视文化','风云音乐']  # 需要提取的关键字列表
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('a1.txt', 'w', encoding='utf-8') as a:    #####定义临时文件名
    a.write(f"央视频道{current_time}更新,#genre#\n")                                                                 #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         a.write(line)  # 将该行写入输出文件 

################
keywords = ['卫视']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('b1.txt', 'w', encoding='utf-8') as b:    #####定义临时文件名
    b.write('\n卫视频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:        
        if re.search(pattern, line):  # 如果行中有任意关键字
         b.write(line)  # 将该行写入输出文件
         
################
keywords = ['都市剧场','上海','上视','欢笑剧场','东方影视','法治天地','纪实人文','动漫秀场','七彩戏剧','五星体育','东方财经','生活时尚','第一财经','游戏风云','金色学堂','乐游']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('c1.txt', 'w', encoding='utf-8') as c:    #####定义临时文件名
    c.write('\n上海频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         c.write(line)  # 将该行写入输出文件

############
keywords = ['湖南','金鹰','快乐垂钓','茶','先锋乒羽']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
with open('1.txt', 'r', encoding='utf-8') as file, open('d1.txt', 'w', encoding='utf-8') as d:    #####定义临时文件名
    d.write('\n湖南频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
        if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
          if re.search(pattern, line): 
              d.write(line)  # 将该行写入输出文件

################
keywords = ['山东','青岛','潍坊','烟台','高密','临沂']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('e1.txt', 'w', encoding='utf-8') as e:    #####定义临时文件名
    e.write('\n山东频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:      
        if re.search(pattern, line):  # 如果行中有任意关键字
         e.write(line)  # 将该行写入输出文件
        
################
keywords = ['河北','衡水','邯郸','石家庄','唐山','秦皇岛','昌黎']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('f1.txt', 'w', encoding='utf-8') as f:    #####定义临时文件名
    f.write('\n河北频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         f.write(line)  # 将该行写入输出文件
        
################
keywords = ['山西']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('g1.txt', 'w', encoding='utf-8') as g:    #####定义临时文件名
    g.write('\n山西频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         g.write(line)  # 将该行写入输出文件

################
keywords = ['河南','信阳','漯河','郑州','驻马店','平顶山','安阳','武术世界','梨园','南阳']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('h1.txt', 'w', encoding='utf-8') as h:    #####定义临时文件名
    h.write('\n河南频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         h.write(line)  # 将该行写入输出文件

################
keywords = ['陕西','西安','汉中']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('i1.txt', 'w', encoding='utf-8') as i:    #####定义临时文件名
    i.write('\n陕西频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         i.write(line)  # 将该行写入输出文件

################
keywords = ['广东','广州','珠江','梅州','岭南','现代教育','客家']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('j1.txt', 'w', encoding='utf-8') as j:    #####定义临时文件名
    j.write('\n广东频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         j.write(line)  # 将该行写入输出文件

################
keywords = ['广西','南宁','玉林','桂林','北流']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('k1.txt', 'w', encoding='utf-8') as k:    #####定义临时文件名
    k.write('\n广西频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         k.write(line)  # 将该行写入输出文件

################
keywords = ['吉林','吉视','松原','东北戏曲']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('l1.txt', 'w', encoding='utf-8') as l:    #####定义临时文件名
    l.write('\n吉林频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         l.write(line)  # 将该行写入输出文件

################
keywords = ['内蒙古']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('m1.txt', 'w', encoding='utf-8') as m:    #####定义临时文件名
    m.write('\n内蒙古频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         m.write(line)  # 将该行写入输出文件

################
keywords = ['辽宁']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('n1.txt', 'w', encoding='utf-8') as n:    #####定义临时文件名
    n.write('\n辽宁频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         n.write(line)  # 将该行写入输出文件

################
keywords = ['黑龙江']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('o1.txt', 'w', encoding='utf-8') as o:    #####定义临时文件名
    o.write('\n黑龙江频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         o.write(line)  # 将该行写入输出文件

################
keywords = ['江苏']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('p1.txt', 'w', encoding='utf-8') as p:    #####定义临时文件名
    p.write('\n江苏频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         p.write(line)  # 将该行写入输出文件

################
keywords = ['湖北','十堰']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('q1.txt', 'w', encoding='utf-8') as q:    #####定义临时文件名
    q.write('\n湖北频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         q.write(line)  # 将该行写入输出文件

################
keywords = ['浙江']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('r1.txt', 'w', encoding='utf-8') as r:    #####定义临时文件名
    r.write('\n浙江频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         r.write(line)  # 将该行写入输出文件

################
keywords = ['凤凰','香港','明珠','星河','翡翠']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('s1.txt', 'w', encoding='utf-8') as s:    #####定义临时文件名
    s.write('\n港澳台,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         s.write(line)  # 将该行写入输出文件

################
keywords = ['重庆']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('t1.txt', 'w', encoding='utf-8') as t:    #####定义临时文件名
    t.write('\n重庆频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         t.write(line)  # 将该行写入输出文件

keywords = [',']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('1.txt', 'r', encoding='utf-8') as file, open('z1.txt', 'w', encoding='utf-8') as z:    #####定义临时文件名
    z.write('\n其他频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         z.write(line)  # 将该行写入输出文件         

############
file_contents = []
file_paths = ["a1.txt","b1.txt","zubo.txt","r1.txt","zj","h1.txt","j1.txt","c1.txt","d1.txt","e1.txt","f1.txt","g1.txt","i1.txt","k1.txt","l1.txt","m1.txt","n1.txt","o1.txt","p1.txt","q1.txt","s1.txt","t1.txt","z1.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 写入合并后的文件
with open("去重1.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

# 原始顺序去重
# 打开文档并读取所有行 
with open('去重1.txt', 'r', encoding="utf-8") as file:
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
with open('iptv.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)

os.remove("iptv0.txt")
os.remove("iptv1.txt")
os.remove("a1.txt")
os.remove("b1.txt")
os.remove("c1.txt")
os.remove("d1.txt")
os.remove("1.txt")
os.remove("e1.txt")
os.remove("f1.txt")
os.remove("g1.txt")
os.remove("h1.txt")
os.remove("i1.txt")
os.remove("j1.txt")
os.remove("k1.txt")
os.remove("l1.txt")
os.remove("m1.txt")
os.remove("n1.txt")
os.remove("o1.txt")
os.remove("p1.txt")
os.remove("q1.txt")
os.remove("r1.txt")
os.remove("s1.txt")
os.remove("t1.txt")
os.remove("z1.txt")
os.remove("去重1.txt")
print("任务运行完毕")
