import os
config_files = ["ip/广东电信_config.txt", "ip/广东联通_config.txt", "ip/广西电信_config.txt", "ip/湖南电信_config.txt", "ip/湖北电信_config.txt", "ip/福建电信_config.txt", "ip/山东电信_config.txt", "ip/山西联通_config.txt", "ip/河南电信_config.txt", "ip/河北联通_config.txt", "ip/北京联通_config.txt", "ip/天津联通_config.txt"]
for config_file in config_files:
    filename = os.path.basename(config_file)
    province = filename.split('_')[0]
    if os.path.exists(f"组播_{province}.txt"):
        os.remove(f"组播_{province}.txt")
    template_file = os.path.join('template', f"template_{province}.txt")
    if not os.path.exists(template_file):
        print(f"缺少模板文件: {template_file}")
        return        
    with open(f"ip/{province}_ip.txt", 'r', encoding='utf-8') as f:    
        for line_num, line in enumerate(f, 1):
            ip = line.strip()
            with open(template_file, 'r', encoding='utf-8') as t, open(f"组播_{province}.txt", 'a', encoding='utf-8') as output:
                output.write(f"{province}-组播{line_num},#genre#\n")
                for line in t:
                    line = line.replace("ipipip", f"{ip}")
                    output.write(line)
print(f"组播地址获取完成")
