import eventlet
eventlet.monkey_patch()
import re
import time
import datetime
import threading
from queue import Queue
import requests
# 定义工作线程函数
def worker():
    error_channels = []
    results = []
    while True:
        channel_name, channel_url = task_queue.get()    # 从队列中获取一个任务
        try:
            with eventlet.Timeout(10, False):
                file_size = 0
                start_time = time.time()
                r = requests.get(channel_url, stream=True, timeout=2)
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        file_size += len(chunk)
                    r.close()
                r_time = time.time() - start_time
                if r_time >=10:
                    file_size = 0
                normalized_speed = file_size / r_time / 1024 / 1024
                if normalized_speed >= 1.05 and file_size >= 9000000:
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(f"可用频道：{len(results)}个，下载速度：{normalized_speed:.3f}MB/s，总频道：{len(channels)}个，进度：{numberx:.2f}%")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
        # 标记任务完成
        task_queue.task_done()
task_queue = Queue()
results = []
channels = []
with open('iptv.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if ',' in line and 'genre' not in line:
            channel_name, channel_url = line.split(',')
            channels.append((channel_name, channel_url))

for _ in range(20):    # 创建多个工作线程
    threading.Thread(target=worker, daemon=True).start()
for channel in channels:
    task_queue.put(channel)
task_queue.join()

def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    return int(match.group()) if match else float('inf')

results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
results.sort(key=lambda x: channel_key(x[0]))
now_today = datetime.date.today()
# 将结果写入文件
with open("speed_results.txt", 'w', encoding='utf-8') as file:
    for channel_name, channel_url, speed in results:
        file.write(f"{channel_name},{channel_url},{speed}\n")

result_counter = 20  # 每个频道需要的个数
now = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=8)
current_time = now.strftime("%Y/%m/%d %H:%M")
with open("iptv_list.m3u", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('#EXTM3U\n')
    for channel_name, channel_url, speed in results:
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    for result in results:
        channel_name, channel_url, speed = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1

    file.write(f"#EXTINF:-1 group-title=\"{current_time}更新\"\n")
