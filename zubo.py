from threading import Thread
import os
import time
import glob
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
def read_config(config_file):
    print(f"读取设置文件：{config_file}")
    ip_configs = []
    try:
        with open(config_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if "," in line and not line.startswith("#"):
                    parts = line.strip().split(',')
                    ip_part, port = parts[0].strip().split(':')
                    a, b, c, d = ip_part.split('.')
                    ip = f"{a}.{b}.1.1"
                    url_end = "/stat" if int(parts[1]) == 1 else "/status"
                    ip_configs.append((ip, port, url_end))
                    print(f"第{line_num}行：http://{ip}:{port}{url_end}添加到扫描列表")
        return ip_configs
    except Exception as e:
        print(f"读取文件错误: {e}")
        return None
# 发送get请求检测url是否可访问        
def check_ip_port(ip_port, url_end):    
    try:
        url = f"http://{ip_port}{url_end}"
        resp = requests.get(url, timeout=2)
        resp.raise_for_status()
        if "Multi stream daemon" in resp.text or "udpxy status" in resp.text:
            print(f"{url} 访问成功")
            return ip_port
    except:
        return None
# 多线程检测url，获取有效ip_port
def scan_ip_port(ip, port, url_end):
    def show_progress():
        while checked[0] < len(ip_ports):
            print(f"已扫描：{checked[0]}/{len(ip_ports)}, 有效ip_port：{len(valid_ip_ports)}个")
            time.sleep(20)
    valid_ip_ports = []
    a, b, c, d = map(int, ip.split('.'))
    ip_ports = [f"{a}.{b}.{x}.{y}:{port}" for x in range(256) for y in range(1,256)]
    checked = [0]
    Thread(target=show_progress, daemon=True).start()
    with ThreadPoolExecutor(max_workers=300) as executor:
        futures = {executor.submit(check_ip_port, ip_port, url_end): ip_port for ip_port in ip_ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_ip_ports.append(result)
            checked[0] += 1
    return valid_ip_ports

def multicast_province(config_file):
    filename = os.path.basename(config_file)
    province, operator = filename.split('_')[:2]
    print(f"{'='*25}\n   获取: {province}{operator}ip_port\n{'='*25}")
    configs = set(read_config(config_file))
    print(f"读取完成，共需扫描 {len(configs)}组")
    all_ip_ports = []
    for ip, port, url_end in configs:
        print(f"\n开始扫描  http://{ip}:{port}{url_end}")
        all_ip_ports.extend(scan_ip_port(ip, port, url_end))
    all_ip_ports = sorted(set(all_ip_ports))
    print(f"\n{province}{operator} 扫描完成，获取有效ip_port共：{len(all_ip_ports)}个\n{all_ip_ports}\n")
    with open(f"ip/{province}{operator}_ip.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_ip_ports) + '\n')    #有效ip_port写入文件
    template_file = os.path.join('template', f"template_{province}{operator}.txt")
    if not os.path.exists(template_file):
        print(f"缺少模板文件: {template_file}")
        return    
    with open(template_file, 'r', encoding='utf-8') as f:
        channels = f.readlines()    
    output = []
    for ip in all_ip_ports:
        output.extend([channel.replace("ipipip", f"{ip}") for channel in channels])    
    with open(f"组播_{province}{operator}.txt", 'w', encoding='utf-8') as f:
        f.write(f"{province}{operator}-组播,#genre#\n")
        for channel in output:
            f.write(channel)
for config_file in glob.glob(os.path.join('ip', '*_config.txt')):
    multicast_province(config_file)
print(f"组播地址获取完成")
