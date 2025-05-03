import eventlet
eventlet.monkey_patch()
import time
import datetime
from threading import Thread
import os
import re
import glob
from queue import Queue
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
# 读取文件并设置参数
def read_config(config_file):
    ip_configs = []
    try:
        with open(config_file, 'r') as f:
            for line in f:
                if line and not line.startswith("#"):
                    ip_part, port = line.strip().split(':')
                    a, b, c, d = ip_part.split('.')
                    ip = f"{a}.{b}.{c}.1"
                    ip_configs.append((ip, port))
        return ip_configs
    except Exception as e:
        print(f"设置文件错误: {e}")
# 发送get请求检测url是否可访问
def check_ip_port(ip_port, url_end):
    try:
        url = f"http://{ip_port}{url_end}"
        resp = requests.get(url, timeout=2)
        resp.raise_for_status()
        if "tsfile" in resp.text or "hls" in resp.text:
            print(f"{url} 访问成功")
            return url
    except:
        return None
# 多线程检测url，获取有效ip_port
def scan_ip_port(ip, port, url_end):
    valid_urls = []
    a, b, c, d = map(int, ip.split('.'))
    ip_ports = [f"{a}.{b}.{c}.{x}:{port}" for x in range(1, 256)]
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(check_ip_port, ip_port, url_end): ip_port for ip_port in ip_ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)
    return valid_urls    
# 发送GET请求获取JSON文件, 解析JSON文件, 获取频道信息
def extract_channels(url):
    hotel_channels = []
    try:
        json_url = f"{url}"
        urls = url.split('/', 3)
        url_x = f"{urls[0]}//{urls[2]}"
        if "iptv" in json_url:
            response = requests.get(json_url, timeout=2)
            json_data = response.json()
            for item in json_data['data']:
                if isinstance(item, dict):
                    name = item.get('name')
                    urlx = item.get('url')
                    if "tsfile" in urlx:
                        urld = f"{url_x}{urlx}"
                        hotel_channels.append((name, urld))
        elif "ZHGXTV" in json_url:
            response = requests.get(json_url, timeout=2)
            json_data = response.content.decode('utf-8')
            data_lines = json_data.split('\n')
            for line in data_lines:
                if "," in line and "hls" in line:
                    name, channel_url = line.strip().split(',')
                    parts = channel_url.split('/', 3)
                    if len(parts) >= 4:
                        urld = f"{url_x}/{parts[3]}"
                        hotel_channels.append((name, urld))
        return hotel_channels
    except Exception:
        return []
# 测速
def speed_test(channels):
    def show_progress():
        while checked[0] < len(channels):
            numberx = checked[0] / len(channels) * 100
            print(f"已测试{checked[0]}/{len(channels)}，可用频道:{len(results)}个，进度:{numberx:.2f}%")
            time.sleep(5)
    # 定义工作线程函数
    def worker():
        while True:
            channel_name, channel_url = task_queue.get()  # 从队列中获取一个任务
            try:
                channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
                lines = requests.get(channel_url,timeout=2).text.strip().split('\n')  # 获取m3u8文件内容
                ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
                ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接
                ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
                with eventlet.Timeout(5, False):    # 获取视频数据进行5秒钟限制
                    start_time = time.time()
                    cont = requests.get(ts_url, timeout=2).content
                    resp_time = (time.time() - start_time) * 1                    
                if cont:
                    checked[0] += 1
                    with open(ts_lists_0, 'ab') as f:
                        f.write(cont)  # 写入文件
                    normalized_speed = max(len(cont) / resp_time / 1024 / 1024, 0.001)
                    os.remove(ts_lists_0)
                    result = channel_name, channel_url, f"{normalized_speed:.3f}"
                    results.append(result)
            except:
                checked[0] += 1
            task_queue.task_done()
    task_queue = Queue()
    results = []
    checked = [0]
    Thread(target=show_progress, daemon=True).start()
    for _ in range(20):    # 创建多个工作线程
        Thread(target=worker, daemon=True).start()
    for channel in channels:
        task_queue.put(channel)
    task_queue.join()
    return results
# 替换关键词以规范频道名
def unify_channel_name(channels_list):
    replacements = {
    "cctv": "CCTV", "中央": "CCTV", "央视": "CCTV", "超清": "", "超高清": "", "高清": "",
    "HD": "", "标清": "", "频道": "", "-": "", " ": "", "PLUS": "+", "＋": "+", "(": "", ")": "", "K1": "", "K2": "",
    "W": "", "w": "", "CCTV1综合": "CCTV1", "CCTV2财经": "CCTV2", "CCTV3综艺": "CCTV3", 
    "CCTV4国际": "CCTV4", "CCTV4广电": "CCTV4", "CCTV4中文国际": "CCTV4", 
    "CCTV4欧洲": "CCTV4", "CCTV5体育": "CCTV5", "CCTV6电影": "CCTV6", "CCTV7军事": "CCTV7", 
    "CCTV7军农": "CCTV7", "CCTV7农业": "CCTV7", "军农": "", "CCTV7国防军事": "CCTV7", 
    "CCTV8电视剧": "CCTV8", "CCTV9记录": "CCTV9", "CCTV9纪录": "CCTV9", 
    "CCTV10科教": "CCTV10", "CCTV11戏曲": "CCTV11", "CCTV12社会与法": "CCTV12", 
    "CCTV13新闻": "CCTV13", "CCTV新闻": "CCTV13", "CCTV14少儿": "CCTV14", 
    "CCTV少儿": "CCTV14", "CCTV15音乐": "CCTV15", "CCTV16奥林匹克": "CCTV16", 
    "CCTV17农业农村": "CCTV17", "CCTV17农业": "CCTV17", "CCTV17军农": "CCTV17", 
    "CCTV17军事": "CCTV17", "CCTV5+体育赛视": "CCTV5+", "CCTV5+体育赛事": "CCTV5+", 
    "CCTV5+体育": "CCTV5+", "CCTV足球": "CCTV风云足球", "上海卫视": "东方卫视", "奥运匹克": "", 
    "军农": "", "回放": "", "测试": "", "CCTV5卡": "CCTV5", "CCTV5赛事": "CCTV5", 
    "CCTV教育": "CETV1", "中国教育1": "CETV1", "CETV1中教": "CETV1", "中国教育2": "CETV2", 
    "中国教育4": "CETV4", "CCTV5+体育赛视": "CCTV5+", "CCTV5+体育赛事": "CCTV5+", 
    "CCTV5+体育": "CCTV5+", "CCTV赛事": "CCTV5+", "CCTV教育": "CETV1", "CCTVnews": "CGTN", 
    "1资讯": "凤凰资讯台", "2中文": "凤凰台", "3XG": "香港台", "上海卫视": "东方卫视", "编码": "", 
    "全纪实": "乐游纪实", "金鹰动画": "金鹰卡通", "河南新农村": "河南乡村", "河南法制": "河南法治", 
    "文物宝库": "收藏天下", "梨园": "河南戏曲", "梨园春": "河南戏曲", "吉林综艺": "吉视综艺文化", 
    "BRTVKAKU": "卡酷少儿", "kaku少儿": "卡酷少儿", "北京卡通": "卡酷少儿", "卡酷卡通": "卡酷少儿", 
    "卡酷动画": "卡酷少儿", "佳佳动画": "嘉佳卡通", "CGTN今日世界": "CGTN", "CGTN英语": "CGTN", 
    "ICS": "上视ICS外语频道", "法制天地": "法治天地", "都市时尚": "都市剧场", "广播电视台": "", 
    "上海炫动卡通": "哈哈炫动", "炫动卡通": "哈哈炫动", "回放": "", "测试": "", "旅游卫视": "海南卫视", 
    "福建东南卫视": "东南卫视", "福建东南": "东南卫视", "南方卫视粤语节目9": "广东大湾区频道", 
    "内蒙古蒙语卫视": "内蒙古蒙语频道", "南方卫视": "广东大湾区频道", "中国教育1": "CETV1", 
    "南方1": "广东经济科教", "南方4": "广东影视频道", "吉林市1": "吉林新闻综合", "XF": ""
    }
    new_channels_list =[]
    for name, channel_url, speed in channels_list:
       for old, new in replacements.items():
           name = name.replace(old, new)
           name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
           new_channels_list.append(f"{name},{channel_url}\n")
    return new_channels_list
# 定义排序函数，提取频道名称中的数字并按数字排序
def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    return int(match.group()) if match else float('inf')
# 自定义分组函数
def classify_channels(input_file, output_file, keywords):
    keywords_list = keywords.split(',')       # 使用 split(',') 来分割关键词
    pattern = '|'.join(re.escape(keyword) for keyword in keywords_list)
    extracted_lines = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if "genre" not in line:
                if re.search(pattern, line):
                    extracted_lines.append(line)
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write(f"{keywords_list[0]},#genre#\n")  # 写入头部信息
        out_file.writelines(extracted_lines)  # 写入提取的行    
# 获取酒店源流程        
def hotel_iptv(config_file):
    ip_configs = set(read_config(config_file))
    valid_urls = []
    channels = []
    configs =[]
    url_ends = ["/iptv/live/1000.json?key=txiptv", "/ZHGXTV/Public/json/live_interface.txt"]
    for url_end in url_ends:
        for ip, port in ip_configs:
            configs.append((ip, port, url_end))
    for ip, port, url_end in configs:
        valid_urls.extend(scan_ip_port(ip, port, url_end))
    print(f"扫描完成，获取有效url共：{len(valid_urls)}个")
    for valid_url in valid_urls:
        channels.extend(extract_channels(valid_url))
    print(f"共获取频道：{len(channels)}个\n开始测速")
    results = speed_test(channels)
    # 对频道进行排序
    results.sort(key=lambda x: -float(x[2]))
    results.sort(key=lambda x: channel_key(x[0]))
    with open('1.txt', 'a', encoding='utf-8') as f:
        f.writelines(unify_channel_name(results))
    print("测速完成")

def main():
    hotel_config_files = [f"ip/酒店高清.ip", f"ip/酒店标清.ip"]
    for config_file in hotel_config_files:
        hotel_iptv(config_file)
    classify_channels('1.txt', '央视.txt', keywords="央视频道,CCTV,风云剧场,怀旧剧场,第一剧场,兵器,女性,地理,央视文化,风云音乐,CHC")
    classify_channels('1.txt', '卫视.txt', keywords="卫视频道,卫视")
    classify_channels('1.txt', '少儿.txt', keywords="少儿频道,少儿,卡通,动漫,炫动")
    classify_channels('1.txt', '湖南.txt', keywords="湖南频道,湖南,金鹰,潇湘,长沙,南县")
    classify_channels('1.txt', '广东.txt', keywords="广东频道,广东,客家,广州,珠江")
    classify_channels('1.txt', '河南.txt', keywords="河南频道,河南,信阳,漯河,郑州,驻马店,平顶山,安阳,武术世界,梨园,南阳")
    classify_channels('1.txt', '广西.txt', keywords="广西频道,广西,南宁,玉林,桂林,北流")
    classify_channels('1.txt', '陕西.txt', keywords="陕西频道,陕西,西安")
    classify_channels('1.txt', '港台.txt', keywords="香港频道,凤凰,香港,明珠台,翡翠台,星河")
    classify_channels('1.txt', '其他.txt', keywords="其他频道,tsfile")
    # 合并写入文件
    file_contents = []
    file_paths = ["央视.txt","卫视.txt","txt/浙江.txt","少儿.txt","湖南.txt","广东.txt","河南.txt","广西.txt","陕西.txt","港台.txt","其他.txt"]  # 替换为实际的文件路径列表
    for file_path in file_paths:
        with open(file_path, 'r', encoding="utf-8") as f:
            content = f.read()
            file_contents.append(content)
    now = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8)
    current_time = now.strftime("%Y/%m/%d %H:%M")
    with open("1.txt", "w", encoding="utf-8") as f:
        f.write(f"{current_time}更新,#genre#\n")
        f.write(f"浙江卫视,http://ali-m-l.cztv.com/channels/lantian/channel001/1080p.m3u8\n")
        f.write('\n'.join(file_contents))
    # 原始顺序去重
    with open('1.txt', 'r', encoding="utf-8") as f:
        lines = f.readlines()
    unique_lines = [] 
    seen_lines = set() 
    for line in lines:
        if line not in seen_lines:
            unique_lines.append(line)
            seen_lines.add(line)
    with open('iptv.txt', 'w', encoding="utf-8") as f:
        f.writelines(unique_lines)
    # 移除过程文件
    files_to_remove = ["1.txt","央视.txt","卫视.txt","少儿.txt","湖南.txt","广东.txt","河南.txt","广西.txt","陕西.txt","港台.txt","其他.txt"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
    print("任务运行完毕，所有频道合并到iptv.txt")

if __name__ == "__main__":
    main()
