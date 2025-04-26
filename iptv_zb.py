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
    print(f"读取设置文件：{config_file}")
    ip_configs = []
    try:
        with open(config_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line and not line.startswith("#"):
                    parts = line.strip().split(',')
                    ip_port = parts[0].strip()
                    if ':' in ip_port:
                        ip, port = ip_port.split(':')
                        a, b, c, d = ip.split('.')
                        if len(parts) == 1:
                            ip, option, keyword = f"{a}.{b}.{c}.1", 0, "tsfile"
                            url_end = "/iptv/live/1000.json?key=txiptv"
                        elif int(parts[1]) == 0:
                            ip, option = f"{a}.{b}.{c}.1", 0
                            url_end, keyword = "/stat", "Multi stream daemon"
                        elif int(parts[1]) == 1:
                            ip, option = f"{a}.{b}.1.1", 1
                            url_end, keyword = "/stat", "Multi stream daemon"
                        elif int(parts[1]) == 2:
                            ip, option, keyword = f"{a}.{b}.{c}.1", 0, "hls"
                            url_end = "/ZHGXTV/Public/json/live_interface.txt"
                        elif int(parts[1]) == 3:
                            ip, option = f"{a}.{b}.1.1", 1
                            url_end, keyword = "/status", "udpxy status"
                        ip_configs.append((ip, port, option, url_end, keyword))
                        print(f"第{line_num}行：http://{ip}:{port}{url_end}添加到扫描列表")
                    else:
                        print(f"第{line_num}行：{ip_port}格式错误")
        print(f"读取完成，共需扫描 {len(ip_configs)}组\n开始扫描")
        return ip_configs
    except Exception as e:
        print(f"设置文件错误: {e}")
        return None
# 生成待扫描ip_port
def generate_ip_ports(ip, port, option):
    a, b, c, d = map(int, ip.split('.'))
    if option == 1:  # C+D段扫描
        return [f"{a}.{b}.{x}.{y}:{port}" for x in range(256) for y in range(1,256)]
    else:  # D段扫描
        return [f"{a}.{b}.{c}.{x}:{port}" for x in range(1, 256)]
# 发送get请求检测url是否可访问
def check_ip_port(ip_port, url_end, keyword):
    try:
        url = f"http://{ip_port}{url_end}"
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200 and keyword in resp.text:
            print(f"{url} 访问成功")
        return ip_port
    except:
        return None
# 多线程检测url，获取有效ip_port
def scan_ip_port(ip, port, option, url_end, keyword):
    def show_progress():
        while checked[0] < len(ip_ports) and option == 1:
            print(f"已扫描：{checked[0]}/{len(ip_ports)}, 有效ip_port：{len(valid_ip_ports)}个")
            time.sleep(20)
    valid_ip_ports = []
    ip_ports = generate_ip_ports(ip, port, option)
    checked = [0]
    Thread(target=show_progress, daemon=True).start()
    with ThreadPoolExecutor(max_workers=300 if option==1 else 100) as executor:
        futures = {executor.submit(check_ip_port, ip_port, url_end, keyword): ip_port for ip_port in ip_ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_ip_ports.append(result)
            checked[0] += 1
    return valid_ip_ports    
# 发送GET请求获取JSON文件, 解析JSON文件, 获取频道信息
def extract_channels(ip_port, url_end, keyword):
    hotel_channels = []
    try:
        json_url = f"http://{ip_port}{url_end}"
        url_x = f"http://{ip_port}"
        if "iptv" in json_url:
            response = requests.get(json_url, timeout=2)
            json_data = response.json()
            for item in json_data['data']:
                if isinstance(item, dict):
                    name = item.get('name')
                    urlx = item.get('url')
                    if keyword in urlx:
                        urld = f"{url_x}{urlx}"
                        hotel_channels.append((name, urld))
        elif "ZHGXTV" in json_url:
            response = requests.get(json_url, timeout=2)
            json_data = response.content.decode('utf-8')
            data_lines = json_data.split('\n')
            for line in data_lines:
                if "," in line and keyword in line:
                    name, channel_url = line.strip().split(',')
                    parts = channel_url.split('/', 3)
                    if len(parts) >= 4:
                        urld = f"{url_x}/{parts[3]}"
                        hotel_channels.append((name, urld))
        return hotel_channels
    except Exception as e:
        print(f"解析json错误 {e}")
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
    new_channels_list =[]
    for name, channel_url, speed in channels_list:
        name = name.replace("cctv", "CCTV")
        name = name.replace("中央", "CCTV")
        name = name.replace("央视", "CCTV")
        name = name.replace("超清", "")
        name = name.replace("超高清", "")
        name = name.replace("高清", "")
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
        name = name.replace("CHC家庭影院", "家庭影院")
        name = name.replace("CHC动作电影", "动作电影")
        name = name.replace("CHC影迷电影", "影迷电影")
        name = name.replace("广播电视台", "")
        name = name.replace("编码", "")
        name = name.replace("XF", "")
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
# 获取组播ip_port流程
def multicast_province(config_file):
    filename = os.path.basename(config_file)
    province, operator = filename.split('_')[:2]
    print(f"{'='*25}\n   获取: {province}{operator}ip_port\n{'='*25}")
    configs = set(read_config(config_file))
    valid_ip_ports = []
    for ip, port, option, url_end, keyword in configs:
        print(f"开始扫描 ip：{ip}，port：{port}，类型：C+D段扫描")
        valid_ip_ports.extend(scan_ip_port(ip, port, option, url_end, keyword))
    print(f"{province}{operator} 扫描完成，获取有效ip_port共：{len(valid_ip_ports)}个\n{valid_ip_ports}")
    all_ip_ports = set(valid_ip_ports)
    with open(f"ip/{province}{operator}_ip.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_ip_ports))    #有效ip_port写入文件
# 获取酒店源流程        
def hotel_iptv(config_file):
    configs = set(read_config(config_file))
    valid_ip_ports = []
    channels = []
    for ip, port, option, url_end, keyword in configs:
        valid_ip_ports.extend(scan_ip_port(ip, port, option, url_end, keyword))
    print(f"扫描完成，获取有效ip_port共：{len(valid_ip_ports)}个")
    for valid_ip_port in valid_ip_ports:
        channels.extend(extract_channels(valid_ip_port, url_end, keyword))
    print(f"共获取频道：{len(channels)}个\n开始测速")
    results = speed_test(channels)
    # 对频道进行排序
    results.sort(key=lambda x: -float(x[2]))
    results.sort(key=lambda x: channel_key(x[0]))
    with open('1.txt', 'a', encoding='utf-8') as f:
        f.writelines(unify_channel_name(results))
    print("测速完成，排序后写入文件：'1.txt'")

def main():
    print("\n开始获取组播源")
    for config_file in glob.glob(os.path.join('ip', '*_config.txt')):
        multicast_province(config_file)
    print(f"组播源获取完成\n{'='*25}\n开始获取酒店源\n{'='*25}")
    hotel_config_files = [f"ip/酒店高清.ip", f"ip/酒店标清.ip"]
    for config_file in hotel_config_files:
        hotel_iptv(config_file)
    classify_channels('1.txt', '央视.txt', keywords="央视频道,CCTV,风云剧场,怀旧剧场,第一剧场,兵器,女性,地理,央视文化,风云音乐,CHC")
    classify_channels('1.txt', '卫视.txt', keywords="卫视频道,卫视")
    classify_channels('1.txt', '河南.txt', keywords="河南频道,河南,信阳,漯河,郑州,驻马店,平顶山,安阳,武术世界,梨园,南阳")
    classify_channels('1.txt', '广西.txt', keywords="广西频道,广西,南宁,玉林,桂林,北流")
    classify_channels('1.txt', '港台.txt', keywords="香港频道,凤凰,香港,明珠台,翡翠台,星河")
    classify_channels('1.txt', '其他.txt', keywords="其他频道,tsfile")
    # 合并写入文件
    file_contents = []
    file_paths = ["央视.txt","卫视.txt","txt/浙江.txt","河南.txt","广西.txt","港台.txt","其他.txt"]  # 替换为实际的文件路径列表
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
    files_to_remove = ["1.txt","央视.txt","卫视.txt","河南.txt","广西.txt","港台.txt","其他.txt"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
    print("任务运行完毕，所有频道合并到iptv.txt")

if __name__ == "__main__":
    main()
