import datetime
import glob
from zubo import multicast_province
config_files = ["ip/江苏电信_config.txt", "ip/上海电信_config.txt", "ip/浙江电信_config.txt", "ip/江西电信_config.txt", "ip/安徽电信_config.txt", "ip/四川电信_config.txt", "ip/贵州电信_config.txt", "ip/重庆电信_config.txt", "ip/陕西电信_config.txt", "ip/宁夏电信_config.txt", "ip/黑龙江联通_config.txt", "ip/辽宁联通_config.txt"]
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
