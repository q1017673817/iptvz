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
#ffmpeg -i "$URL" -t 20 -c copy "$OUTPUT_FILE" -y 2>/dev/null
timeout 25 ffmpeg -i "$URL" -t 20 -c copy "$OUTPUT_FILE" -y >ffmpeg.log 2>&1

# 检查 ffmpeg 的退出状态
if [ $? -eq 0 ]; then
    # 结束时间
    END_TIME=$(date +%s)

    # 计算下载时长
    DURATION=$((END_TIME - START_TIME))

    # 获取文件大小（以字节为单位）
    FILE_SIZE=$(stat -c%s "$OUTPUT_FILE")
    Frames=$(tail -n 2 ffmpeg.log |head -n 1| grep -oE 'frame=[ ]*[0-9]+'  | tail -1 | awk -F'=' '{print $2}' | tr -d ' ')
    if [ "$FILE_SIZE" -eq 0 ]; then
        echo "下载文件为空：$1"
        DOWNLOAD_SPEED_MBPS=0
    else
        # 计算下载速度（字节/秒）
        DOWNLOAD_SPEED=$(echo "scale=2; $FILE_SIZE / $DURATION" | bc)
        # 将下载速度转换为 Mb/s
        DOWNLOAD_SPEED_MBPS=$(echo "scale=2; $DOWNLOAD_SPEED * 8 / 1000000" | bc)

        # 判断 DOWNLOAD_SPEED_MBPS 是否小于 1，速度太慢的节点不要
        if (( $(echo "$DOWNLOAD_SPEED_MBPS < 1" | bc -l) )); then
            echo "-------下载速度慢：$DOWNLOAD_SPEED_MBPS  下载帧数：$Frames-------"
            DOWNLOAD_SPEED_MBPS=0
        else
            if (( $Frames < 200  ));then
                echo "-------下载速度($DOWNLOAD_SPEED_MBPS)，但测试帧数低: $Frames-------"
                DOWNLOAD_SPEED_MBPS=0
            else
                echo "-------下载速度($DOWNLOAD_SPEED_MBPS)，测试帧数: $Frames-------"
            fi

        fi
    fi

else
    echo "链接下载测速不可用!"
fi
echo "$DOWNLOAD_SPEED_MBPS Mb/s"
rm -rf ${OUTPUT_FILE}
