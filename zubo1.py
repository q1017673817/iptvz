import datetime
import glob
from zubo import multicast_province
config_files = ["ip/广东电信_config.txt", "ip/广东联通_config.txt", "ip/广西电信_config.txt", "ip/湖南电信_config.txt", "ip/湖北电信_config.txt", "ip/福建电信_config.txt", "ip/山东电信_config.txt", "ip/山西联通_config.txt", "ip/河南电信_config.txt", "ip/河北联通_config.txt", "ip/北京联通_config.txt", "ip/天津联通_config.txt"]
for config_file in config_files:
    multicast_province(config_file)
file_contents = []
for file_path in glob.glob('组播_*.txt'):
    with open(file_path, 'r', encoding="utf-8") as f:
        content = f.read()
        file_contents.append(content)
now = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8)
current_time = now.strftime("%Y/%m/%d %H:%M")
with open("zubo_all.txt", "w", encoding="utf-8") as f:
    f.write(f"{current_time}更新,#genre#\n")
    f.write(f"浙江卫视,http://ali-m-l.cztv.com/channels/lantian/channel001/1080p.m3u8\n")
    f.write('\n'.join(file_contents))
print(f"组播地址获取完成")
