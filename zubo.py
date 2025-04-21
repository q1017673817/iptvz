import os
import re
import time
import glob
import requests
import threading
from queue import Queue
from threading import Thread
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def read_config(config_path):
    print(f"读取设置文件：{config_path}")
    configs = []
    try:
        with open(config_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line and not line.startswith("#"):
                    parts = line.strip().split(',')
                    ip_port = parts[0].strip()
                    option = int(parts[1]) if len(parts) == 2 else 1  # 默认为1                 
                    if ':' in ip_port:
                        print(f"第{line_num}行：{ip_port},{option}添加到扫描列表")
                        ip, port = ip_port.split(':')
                        configs.append((ip, port, option))
                    else:
                        print(f"第{line_num}行：{ip_port}格式错误")
        print(f"读取完成，共需扫描{len(configs)}组")
        return configs
    except Exception as e:
        print(f"配置文件错误: {e}")
        return []

def generate_ips(ip, option):
    a, b, c, d = map(int, ip.split('.'))
    if option == 1:  # C+D段扫描
        return [f"{a}.{b}.{x}.{y}" for x in range(256) for y in range(256)]
    else:  # D段扫描
        return [f"{a}.{b}.{c}.{x}" for x in range(1, 256)]

def check_ip_port(ip, port, url_end):
    try:
        url = f"http://{ip}:{port}{url_end}"
        resp = requests.get(url, timeout=1.5)
        if resp.status_code == 200 and 'Multi stream daemon' in resp.text:
            print(f"扫描到有效ip：{ip}:{port}")
            return f"{ip}:{port}"        
    except Exception:
        return None

def scan_ip_port(ip, port, url_end, option):                            
    def show_progress():
        while checked[0] < total:
            print(f"已扫描：{checked[0]}/{total}, 有效ip：{len(valid_ips)}个")
            time.sleep(30)
            
    print(f"\n开始扫描 ip:{ip} 端口:{port} 类型:{option}")            
    valid_ips = []
    ips = generate_ips(ip, option)
    total = len(ips)
    checked = [0]    
    Thread(target=show_progress, daemon=True).start()
    with ThreadPoolExecutor(max_workers=300 if option==1 else 100) as executor:
        futures = {executor.submit(check_ip_port, ip, port, url_end): ip for ip in ips}
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_ips.append(result)
            checked[0] += 1   
    return valid_ips

def province(config_path):
    filename = os.path.basename(config_path)
    province, operator = filename.split('_')[:2]
    print(f"\n{'='*20}\n   获取: {province}{operator}ip\n{'='*20}")    
    configs = read_config(config_path)
    all_ips = []
    url_end = "/stat"
    for ip, port, option in configs:
        all_ips.extend(scan_ip_port(ip, port, url_end, option))
    print(f"{province}{operator} 扫描完成，有效ip共：{len(all_ips)}个\n{all_ips}")
    all_ips = set(all_ips)
    with open(f"ip/{province}{operator}_ip.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_ips))
    template_file = os.path.join('template', f"template_{province}{operator}.txt")
    if not os.path.exists(template_file):
        print(f"缺少模板文件: {template_file}")
        return    
    with open(template_file, 'r', encoding='utf-8') as f:
        channels = f.readlines()    
    output = []
    for ip in all_ips:
        output.extend([channel.replace("ipipip", f"{ip}") for channel in channels])    
    with open(f"{province}{operator}.txt", 'w', encoding='utf-8') as f:
        f.write(f"{province}{operator}-组播,#genre#\n")
        for channel in output:
            f.write(channel)
        print(f"生成可用文件 {province}{operator}.txt") 
    
def main():
    # 处理所有省份配置
    for config_path in glob.glob(os.path.join('ip', '*_config.txt')):
        province(config_path)
    print("组播源获取完成")
    
if __name__ == "__main__":
    main()
