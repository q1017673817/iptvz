#!/bin/bash

# 检查是否提供了 URL 参数
if [ "$#" -ne 2 ]; then
    echo "用法: $0 <ip> <stream>"
    exit 1
fi

# IPTV 地址
URL="http://$1/$2"
# 输出文件名
OUTPUT_FILE="temp_video.mp4" 

# 开始时间
START_TIME=$(date +%s)

# 使用 ffmpeg 下载视频并保存 20秒
ffmpeg -i "$URL" -t 40 -c copy "$OUTPUT_FILE" -y 2>/dev/null

# 检查 ffmpeg 的退出状态
if [ $? -ne 0 ]; then
    echo "0 Mb/s"
    exit 0
fi

# 结束时间
END_TIME=$(date +%s)

# 计算下载时长
DURATION=$((END_TIME - START_TIME))

# 获取文件大小（以字节为单位）
FILE_SIZE=$(stat -c%s "$OUTPUT_FILE")
# 计算下载速度（字节/秒）
DOWNLOAD_SPEED=$(echo "scale=2; $FILE_SIZE / $DURATION" | bc)
# 将下载速度转换为 Mb/s
DOWNLOAD_SPEED_MBPS=$(echo "scale=2; $DOWNLOAD_SPEED * 8 / 1000000" | bc)

rm -rf temp_video.mp4
# 判断 DOWNLOAD_SPEED_MBPS 是否小于 1M，速度太慢的节点不要
if (( $(echo "$DOWNLOAD_SPEED_MBPS < 0.8" | bc -l) )); then
    DOWNLOAD_SPEED_MBPS=0
fi

# 输出结果
echo "$DOWNLOAD_SPEED_MBPS Mb/s"
