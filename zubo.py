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


def generate_ips(ip_part, option):
    a, b, c, d = map(int, ip_part.split('.'))
    if option == 0:  # D段扫描
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
                    #print(f"第{line_num}行：{line}不需要扫描")
                    continue
                parts = line.split(',')
                ip_port = parts[0].strip()                
                option = int(parts[1].strip()) if len(parts) == 2 else 1  # 默认为1                 
                if ':' in ip_port:
                    print(f"第{line_num}行：{line}需要扫描")
                    configs.append((ip_port, option))
                else:
                    print(f"第{line_num}行：{line}格式错误")
        print(f"共需扫描 {len(configs)}组")
        return configs
    except Exception as e:
        print(f"配置文件错误: {e}")
        return []


def scan_ips(ip_part, port, option):
    print(f"\n开始扫描 ip:{ip_part} 端口:{port} 类型:{option}")
    valid_ips = []
    ips = generate_ips(ip_part, option)

    total = len(ips)
    checked = [0]
    
    def show_progress():
        while checked[0] < total:
            print(f"已扫描：{checked[0]}/{total}, 有效ip：{len(valid_ips)}个")
            time.sleep(30)
    
    Thread(target=show_progress, daemon=True).start()
    
    with ThreadPoolExecutor(max_workers=300 if option==0 else 100) as executor:
        futures = {executor.submit(check_ip, ip, port): ip for ip in ips}
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_ips.append(result)
            checked[0] += 1
    
    print(f"扫描完成，有效ip数量：{len(valid_ips)}个\n{valid_ips}")
#        print(valid_ip)
    return valid_ips


def province(config_path):
    filename = os.path.basename(config_path)
    if not filename.endswith("_config.txt"):
        return
    
    province, operator = filename.split('_')[:2]
    print(f"\n{'='*30}\n     获取: {province}{operator}ip\n{'='*30}")
    
    # 扫描IP
    configs = read_config(config_path)
    all_ips = []
    for entry in configs:
        try:
            ip_port, option = entry
            ip_part, port = ip_port.split(':', 1)
            all_ips.extend(scan_ips(ip_part, port, int(option)))
            print(f"{province}{operator} 扫描完成，有效ip共：{len(all_ips)}个\n{all_ips}")
        except Exception as e:
            print(f"配置错误: {entry} -> {e}")
                
    # 生成组播
    tmpl_file = os.path.join('template', f"template_{province}{operator}.txt")
    if not os.path.exists(tmpl_file):
        print(f"缺少模板文件: {tmpl_file}")
        return
    
    with open(tmpl_file, 'r', encoding='utf-8') as f:
        channels = [line for line in f if line]
    
    output = []
    for ip in all_ips:
        output.extend([channel.replace("ipipip", f"{ip}") for channel in channels])
    
    with open(f"{province}{operator}.txt", 'w', encoding='utf-8') as f:
        f.write(f"\n{province}{operator}-组播,#genre#\n")
        for channel in output:
            f.write(channel)
        print(f"成功生成可用文件 {province}{operator}.txt")

    ip_file = os.path.join('ip', f"{province}{operator}_ip.txt")
    with open(ip_file, 'a', encoding='utf-8') as f:
        for ip in all_ips:
            f.write(ip + '\n')
        print(f"有效ip成功写入文件 'ip/{province}{operator}_ip.txt'")


def main():
    # 处理所有省份配置
    for conf in glob.glob(os.path.join('ip', '*_config.txt')):
        province(conf)
    print("扫描任务运行完毕")

if __name__ == "__main__":
    main()
