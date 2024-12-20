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
import eventlet
import re

urls = []

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
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None


results = []

urls_all = []

with open('酒店源ip.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            url = line.strip()
            urls_all.append(url)
        
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
                response = requests.get(json_url, timeout=3)
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
                                name = name.replace("怀旧剧场", "CCTV怀旧剧场")
                                name = name.replace("电视指南", "CCTV电视指南")
                                name = name.replace("第一剧场", "CCTV第一剧场")
                                name = name.replace("风云剧场", "CCTV风云剧场")
                                name = name.replace("风云足球", "CCTV风云足球")
                                name = name.replace("风云音乐", "CCTV风云音乐")
                                name = name.replace("高尔夫", "CCTV高尔夫")
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

                                if 'udp' not in urld or 'rtp' not in urld:
                                    results.append(f"{name},{urld}")
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
        
with open('itv.txt', 'r', encoding='utf-8') as file:
#从整理好的文本中按类别进行特定关键词提取
 keywords = ['tsfile']  # 需要提取的关键字列表
 pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('itv.txt', 'r', encoding='utf-8') as file, open('itv1.txt', 'w', encoding='utf-8') as a:    #####定义临时文件名
    a.write('\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         a.write(line)  # 将该行写入输出文件

channels = []
with open('itv1.txt', 'r', encoding='utf-8') as file:
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

with open('2.txt', 'w', encoding='utf-8') as file:
    file.write('\n')        
    for channel, address in channels:
        if 'tsfile' in address:
            file.write(f'{channel},{address}\n')


###############################        
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

################
keywords = ['卫视']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('b.txt', 'w', encoding='utf-8') as b:    #####定义临时文件名
    b.write('\n卫视频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:        
        if re.search(pattern, line):  # 如果行中有任意关键字
         b.write(line)  # 将该行写入输出文件
         
################
keywords = ['都市剧场', '上海', '上视', '欢笑剧场', '东方影视', '法治天地', '纪实人文', '动漫秀场', '七彩戏剧', '五星体育', '东方财经', '生活时尚', '第一财经', '金色学堂', '乐游']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('c.txt', 'w', encoding='utf-8') as c:    #####定义临时文件名
    c.write('\n上海频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         c.write(line)  # 将该行写入输出文件

############
keywords = ['湖南','金鹰','快乐垂钓','茶','先锋乒羽']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
with open('2.txt', 'r', encoding='utf-8') as file, open('d.txt', 'w', encoding='utf-8') as d:    #####定义临时文件名
    d.write('\n湖南频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
        if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
          if re.search(pattern, line): 
              d.write(line)  # 将该行写入输出文件

################
keywords = ['山东','潍坊','烟台','高密','临沂']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('e.txt', 'w', encoding='utf-8') as e:    #####定义临时文件名
    e.write('\n山东频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:      
        if re.search(pattern, line):  # 如果行中有任意关键字
         e.write(line)  # 将该行写入输出文件
        
################
keywords = ['河北','衡水','邯郸','石家庄','唐山','秦皇岛','昌黎']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('f.txt', 'w', encoding='utf-8') as f:    #####定义临时文件名
    f.write('\n河北频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         f.write(line)  # 将该行写入输出文件
        
################
keywords = ['山西']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('g.txt', 'w', encoding='utf-8') as g:    #####定义临时文件名
    g.write('\n山西频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         g.write(line)  # 将该行写入输出文件

################
keywords = ['河南','信阳','漯河','郑州','驻马店','平顶山','安阳','武术世界','梨园','南阳']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('h.txt', 'w', encoding='utf-8') as h:    #####定义临时文件名
    h.write('\n河南频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         h.write(line)  # 将该行写入输出文件

################
keywords = ['陕西','汉中']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('i.txt', 'w', encoding='utf-8') as i:    #####定义临时文件名
    i.write('\n陕西频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         i.write(line)  # 将该行写入输出文件

################
keywords = ['广东','广州','珠江','梅州','岭南','现代教育','客家']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('j.txt', 'w', encoding='utf-8') as j:    #####定义临时文件名
    j.write('\n广东频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         j.write(line)  # 将该行写入输出文件

################
keywords = ['广西','南宁','玉林','桂林','北流']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('k.txt', 'w', encoding='utf-8') as k:    #####定义临时文件名
    k.write('\n广西频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'CCTV' not in line and '卫视' not in line and 'CHC' not in line and '4K' not in line and 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         k.write(line)  # 将该行写入输出文件

################
keywords = ['吉林','吉视','松原','东北戏曲']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('l.txt', 'w', encoding='utf-8') as l:    #####定义临时文件名
    l.write('\n吉林频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         l.write(line)  # 将该行写入输出文件

################
keywords = ['内蒙古']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('m.txt', 'w', encoding='utf-8') as m:    #####定义临时文件名
    m.write('\n内蒙古频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         m.write(line)  # 将该行写入输出文件

################
keywords = ['辽宁']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('n.txt', 'w', encoding='utf-8') as n:    #####定义临时文件名
    n.write('\n辽宁频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         n.write(line)  # 将该行写入输出文件

################
keywords = ['黑龙江']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('o.txt', 'w', encoding='utf-8') as o:    #####定义临时文件名
    o.write('\n黑龙江频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         o.write(line)  # 将该行写入输出文件

################
keywords = ['江苏']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('p.txt', 'w', encoding='utf-8') as p:    #####定义临时文件名
    p.write('\n江苏频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         p.write(line)  # 将该行写入输出文件

################
keywords = ['湖北','十堰']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('q.txt', 'w', encoding='utf-8') as q:    #####定义临时文件名
    q.write('\n湖北频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         q.write(line)  # 将该行写入输出文件

################
keywords = ['浙江']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('r.txt', 'w', encoding='utf-8') as r:    #####定义临时文件名
    r.write('\n浙江频道,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         r.write(line)  # 将该行写入输出文件

################
keywords = ['凤凰','香港','明珠','星河','翡翠']  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
#pattern = r"^(.*?),(?!#genre#)(.*?)$" #以分类直接复制
with open('2.txt', 'r', encoding='utf-8') as file, open('s.txt', 'w', encoding='utf-8') as s:    #####定义临时文件名
    s.write('\n港澳台,#genre#\n')                                                                  #####写入临时文件名
    for line in file:
      if 'genre' not in line:
        if re.search(pattern, line):  # 如果行中有任意关键字
         s.write(line)  # 将该行写入输出文件

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
file_paths = ["a.txt","b.txt","c.txt","d.txt","e.txt","f.txt","g.txt","h.txt","i.txt","j.txt","k.txt","l.txt","m.txt","n.txt","o.txt","p.txt","q.txt","r.txt","s.txt","z.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 写入合并后的文件
with open("去重.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

##############################原始顺序去重
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
with open('iptv.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)

os.remove("itv.txt")
os.remove("itv1.txt")
os.remove("a.txt")
os.remove("b.txt")
os.remove("c.txt")
os.remove("d.txt")
os.remove("2.txt")
os.remove("e.txt")
os.remove("f.txt")
os.remove("g.txt")
os.remove("h.txt")
os.remove("i.txt")
os.remove("j.txt")
os.remove("k.txt")
os.remove("l.txt")
os.remove("m.txt")
os.remove("n.txt")
os.remove("o.txt")
os.remove("p.txt")
os.remove("q.txt")
os.remove("r.txt")
os.remove("s.txt")
os.remove("z.txt")
os.remove("去重.txt")
print("任务运行完毕")
