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

def scan_ips(ip, port, option):
    def generate_ips(ip, option):
        a, b, c, d = map(int, ip.split('.'))
            if option == 1:  # C+D段扫描
                return [f"{a}.{b}.{x}.{y}" for x in range(256) for y in range(256)]
            else:  # D段扫描
                return [f"{a}.{b}.{c}.{x}" for x in range(1, 256)]
                
    def check_ip(ip, port):
        try:
            url = f"http://{ip}:{port}/stat"
            resp = requests.get(url, timeout=1.5)
            if resp.status_code == 200 and 'Multi stream daemon' in resp.text:
                print(f"扫描到有效ip：{ip}:{port}")
                return f"{ip}:{port}"        
        except Exception:
            return None
    
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
        futures = {executor.submit(check_ip, ip, port): ip for ip in ips}
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_ips.append(result)
            checked[0] += 1   
    #print(f"扫描完成，有效ip数量：{len(valid_ips)}个\n{valid_ips}")
    return valid_ips

def province(config_path):
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
                            configs.append((ip_port, option))
                        else:
                            print(f"第{line_num}行：{ip_port}格式错误")
                    else:
                        print(f"第{line_num}行：{line}不需要扫描")                
            print(f"读取完成，共需扫描{len(configs)}组")
            return configs
        except Exception as e:
            print(f"配置文件错误: {e}")
            return []
            
    filename = os.path.basename(config_path)
    province, operator = filename.split('_')[:2]
    print(f"\n{'='*20}\n   获取: {province}{operator}ip\n{'='*20}")    
    configs = read_config(config_path)
    all_ips = []
    for ip_port, option in configs:
        ip, port = ip_port.split(':', 1)
        all_ips.extend(scan_ips(ip, port, int(option)))
    all_ips = set(all_ips)
    print(f"{province}{operator} 扫描完成，有效ip共：{len(all_ips)}个\n{all_ips}")
    ip_file = os.path.join('ip', f"{province}{operator}_ip.txt")
    with open(ip_file, 'a', encoding='utf-8') as f:
        for ip in all_ips:
            f.write(ip + '\n')
        print(f"有效ip写入文件 {ip_file}")    
    return all_ips
                
def main():
    # 处理所有省份配置
    for config_path in glob.glob(os.path.join('ip', '*_config.txt')):
        province(config_path)
                
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
        f.write(f"\n{province}{operator}-组播,#genre#\n")
        for channel in output:
            f.write(channel)
        print(f"生成可用文件 {province}{operator}.txt")        
    print("任务运行完毕")

if __name__ == "__main__":
    main()
