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

def check_ip(ip, port):
    try:
        url = f"http://{ip}:{port}/stat"
        resp = requests.get(url, timeout=1.5)
        if resp.status_code == 200 and 'Multi stream daemon' in resp.text:
            print(f"扫描到有效ip：{ip}:{port}")
            return f"{ip}:{port}"
        
    except Exception:
        return None


def generate_ips(ip_part, scan_type):
    a, b, c, d = map(int, ip_part.split('.'))
    if scan_type == 0:  # D段扫描
        return [f"{a}.{b}.{c}.{x}" for x in range(1, 256)]
    else:  # C+D段扫描
        return [f"{a}.{b}.{x}.{y}" for x in range(256) for y in range(256)]


def read_config(config_path):
    configs = []
    try:
        with open(config_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(',')
                if len(parts) != 2:
                    print(f"格式错误，第{line_num}行：{line}需要'ip:端口,扫描类型'格式")
                    continue
                configs.append(parts)
        return configs
    except Exception as e:
        print(f"配置文件错误: {e}")
        return []


def scan_ips(ip_part, port, scan_type):
    print(f"\n开始扫描 ip:{ip_part} 端口:{port} 类型:{scan_type}")
    valid_ips = []
    ips = generate_ips(ip_part, scan_type)
    total = len(ips)
    checked = [0]
    
    def show_progress():
        while checked[0] < total:
            print(f"已扫描：{checked[0]}/{total}，有效ip：{len(valid_ips)}个")
            time.sleep(10)
    
    Thread(target=show_progress, daemon=True).start()
    
    with ThreadPoolExecutor(max_workers=300 if scan_type==0 else 100) as executor:
        futures = {executor.submit(check_ip, ip, port): ip for ip in ips}
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_ips.append(result)
            checked[0] += 1
    
    print(f"扫描完成，有效ip数量：{len(valid_ips)}个")
    for valid_ip in valid_ips
    print(valid_ip)
    return valid_ips


def province(config_path):
    filename = os.path.basename(config_path)
    if not filename.endswith("_config.txt"):
        return
    
    province, operator = filename.split('_')[:2]
    print(f"\n{'='*30}\n 获取: {province}{operator}ip\n{'='*30}")
    
    # 扫描IP
    configs = read_config(config_path)
    all_ips = []
    for entry in configs:
        try:
            ip_port, scan_type = entry
            ip_part, port = ip_port.split(':', 1)
            all_ips.extend(scan_ips(ip_part, port, int(scan_type)))
        except Exception as e:
            print(f"配置错误: {entry} -> {e}")
                
    # 生成组播
    tmpl_file = os.path.join('template', f"template_{province}{operator}.txt")
    if not os.path.exists(tmpl_file):
        print(f"缺少模板文件: {tmpl_file}")
        return
    
    with open(tmpl_file, 'r', encoding='utf-8') as f:
        channels = [line.strip() for line in f if line.strip()]
    
    output = []
    for ip in all_ips:
        output.extend([channel.replace("ipipip", f"{ip}") for channel in channels])
    
    with open(f"txt/{province}{operator}.txt", 'w', encoding='utf-8') as f:
        f.write(f"\n{province}{operator}-组播,#genre#\n")
        f.write('\n'.join(output) + "\n")

    with open(f"ip/{province}{operator}_good_ip", 'w', encoding='utf-8') as f:
        for ip in all_ips:
            f.write(ip + "\n")
            print(ip)


def main():
    # 处理所有省份配置
    for conf in glob.glob(os.path.join('ip', '*_config.txt')):
        province(conf)
    

if __name__ == "__main__":
    main()
