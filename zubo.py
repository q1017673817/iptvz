from threading import Thread
import os
import glob
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
def read_config(config_file):
    print(f"读取设置文件：{config_file}")
    ip_configs = []
    try:
        with open(config_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line and not line.startswith("#"):
                    parts = line.strip().split(',')
                    ip, port = parts[0].strip().split(':')
                    a, b, c, d = ip.split('.')
                    if int(parts[1]) == 1:
                        ip, option = f"{a}.{b}.1.1", 1
                    elif int(parts[1]) == 0:
                        ip, option = f"{a}.{b}.{c}.1", 0
                    ip_configs.append((ip, port, option))
                    print(f"第{line_num}行：http://{ip}:{port}添加到扫描列表")
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
def scan_ip_port(ip, port, option, url_end):
    def show_progress():
        while checked[0] < len(ip_ports) and option == 1:
            print(f"已扫描：{checked[0]}/{len(ip_ports)}, 有效ip_port：{len(valid_ip_ports)}个")
            time.sleep(20)
    valid_ip_ports = []
    ip_ports = generate_ip_ports(ip, port, option)
    checked = [0]
    Thread(target=show_progress, daemon=True).start()
    with ThreadPoolExecutor(max_workers=300 if option==1 else 50) as executor:
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
    configs = sorted(set(read_config(config_file)))
    valid_ip_ports = []
    for ip, port, option in configs:
        url_ends = ["/stat", "/status"]
        for url_end in url_ends:
            print(f"\n开始扫描 ip：{ip}，port：{port}，url_end：{url_end} ")
            valid_ip_ports.extend(scan_ip_port(ip, port, option, url_end))
    valid_ip_ports = sorted(set(valid_ip_ports))
    print(f"{province}{operator} 扫描完成，获取有效ip_port共：{len(valid_ip_ports)}个\n{valid_ip_ports}")
    with open(f"ip/{province}{operator}_ip.txt", 'a', encoding='utf-8') as f:
        f.write('\n'.join(valid_ip_ports) + '\n')    #有效ip_port写入文件

print("\n开始获取组播源")
for config_file in glob.glob(os.path.join('ip', '*_config.txt')):
    multicast_province(config_file)
print(f"组播源获取完成")
