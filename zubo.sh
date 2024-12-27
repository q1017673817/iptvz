#pwd
time=$(date +%m%d%H%M)
i=0

if [ $# -eq 0 ]; then
  echo "请选择城市："
  echo "0. 全部"
  read -t 1 -p "输入选择或在3秒内无输入将默认选择全部: " city_choice

  if [ -z "$city_choice" ]; then
      echo "未检测到输入，自动选择全部选项..."
      city_choice=0
  fi

else
  city_choice=$1
fi

# 根据用户选择设置城市和相应的stream
case $city_choice in
    1)
        city="Zhejiang_120"
        stream="udp/233.50.201.63:5140"
        channel_key="浙江电信"
        ;;
    2)
        city="Jiangsu"
        stream="udp/239.49.8.19:9614"
        channel_key="江苏电信"
        ;;
    3)
        city="Shanghai_103"
        stream="udp/239.45.1.42:5140"
	channel_key="上海电信"
        ;;
    4)
        city="Beijing_liantong_145"
        stream="rtp/239.3.1.249:8001"
        channel_key="北京联通"
        ;;
    5)
        city="Hubei_90"
        stream="rtp/239.69.1.249:11136"
        channel_key="湖北电信"
        ;;
    6)
        city="Sichuan_333"
        stream="udp/239.93.42.33:5140"
        channel_key="四川电信"
        ;;
    7)
        city="Beijing_dianxin_186"
        stream="udp/225.1.8.1:8008"
        channel_key="北京电信"
        ;;
    8)
        city="Hebei_313"
        stream="rtp/239.253.93.223:6401"
	channel_key="河北联通"
        ;;
    9)
        city="Shanxi_117"
        stream="udp/239.1.1.7:8007"
        channel_key="山西电信"
        ;;
    10)
        city="Tianjin_160"
        stream="udp/225.1.2.190:5002"
        channel_key="天津联通"
        ;;
    11)
        city="Guangdong_332"
        stream="udp/239.77.0.244:5146"
        channel_key="广东电信"
	;;
    12)
        city="Anhui_191"
        stream="rtp/238.1.78.137:6968"
        channel_key="安徽电信"
	;;
    13)
        city="Chongqing_161"
        stream="rtp/235.254.198.102:7980"
        channel_key="重庆电信"
	;;
    14)
        city="Fujian_114"
        stream="rtp/239.61.2.132:8708"
        channel_key="福建电信"
	;;
    15)
        city="Henan_327"
        stream="rtp/239.16.20.21:10210"
        channel_key="河南电信"
	;;
    16)
        city="Ningxia"
        stream="rtp/239.121.4.94:8538"
        channel_key="宁夏电信"
        ;;
    17)
        city="Shandong_279"
        stream="udp/239.21.1.87:5002"
        channel_key="山东电信"
        ;;
    18)
        city="Shanxi_184"
        stream="rtp/226.0.2.152:9128"
        channel_key="山西联通"
        ;;
    19)
        city="Guangxi"
        stream="udp/239.81.0.107:4056"
        channel_key="广西电信"
        ;;
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1,2,5,15,18}; do
          bash "$0" $option  # 假定fofa.sh是当前脚本的文件名，$option将递归调用
        done
        exit 0
        ;;

    *)
        echo "错误：无效的选择。"
        exit 1
        ;;
esac

# 使用城市名作为默认文件名，格式为 CityName.ip
rm -f ip/${channel_key}.onlygood.ip ip/${channel_key}有效.ip
ipfile="ip/${channel_key}.ip"
only_good_ip="ip/${channel_key}.onlygood.ip"
# 搜索最新 IP
cat ip/${channel_key}.html | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_ipfile
#cat ip/${channel_key}.onlygood.ip > tmp_ipfile
sort tmp_ipfile | uniq | sed '/^\s*$/d' > "$ipfile"
rm -f tmp_ipfile ip/${channel_key}.html

while IFS= read -r ip; do
    # 尝试连接 IP 地址和端口号，并将输出保存到变量中
    tmp_ip=$(echo -n "$ip" | sed 's/:/ /')
    #echo "nc -w 1 -v -z $tmp_ip 2>&1"
    output=$(nc -w 1 -v -z $tmp_ip 2>&1)
    echo $output   
    # 如果连接成功，且输出包含 "succeeded"，则将结果保存到输出文件中
    if [[ $output == *"succeeded"* ]]; then
        # 使用 awk 提取 IP 地址和端口号对应的字符串，并保存到输出文件中
        echo "$output" | grep "succeeded" | awk -v ip="$ip" '{print ip}' >> "$only_good_ip"
    fi
done < "$ipfile"

lines=$(wc -l < "$only_good_ip")
echo "【$only_good_ip】内 ip 共计 $lines 个"

i=0
mkdir -p tmpip
while read -r line; do
    ip=$(echo "$line" | sed 's/^[ \t]*//;s/[ \t]*$//')  # 去除首尾空格
    
    # 如果行不为空，则写入临时文件
    if [ -n "$ip" ]; then
        echo "$ip" > "tmpip/ip_$i.txt"  # 保存为 tmpip 目录下的临时文件
        ((i++))
    fi
done < "$only_good_ip"

i=0
for temp_file in tmpip/ip_*.txt; do
      ((i++))
     ip=$(<"$temp_file")  # 从临时文件中读取 IP 地址
     a=$(./speed.sh "$ip" "$stream")
     echo "第 $i/$lines 个：$ip $a"
     echo "$ip $a" >> "speedtest_${city}_$time.log"
done
rm -rf tmpip/* $only_good_ip

cat "speedtest_${city}_$time.log" | grep -E 'M|k' | awk '{print $2"  "$1}' | sort -n -r >"result/fofa_${city}.txt"
cat "result/fofa_${city}.txt"
ip1=$(head -n 1 result/fofa_${city}.txt | awk '{print $2}')
ip2=$(head -n 2 result/fofa_${city}.txt | tail -n 1 | awk '{print $2}')
ip3=$(head -n 3 result/fofa_${city}.txt | tail -n 1 | awk '{print $2}')
ip4=$(head -n 4 result/fofa_${city}.txt | tail -n 1 | awk '{print $2}')
ip5=$(head -n 5 result/fofa_${city}.txt | tail -n 1 | awk '{print $2}')
# awk '{print $2}' "result/fofa_${city}.txt" > "ip/${channel_key}有效.ip"
rm -f "speedtest_${city}_$time.log" result/fofa_${channel_key}.ip
# 用 5 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"
sed "s/ipipip/$ip1/g" "$program" > tmp1.txt
sed "s/ipipip/$ip2/g" "$program" > tmp2.txt
sed "s/ipipip/$ip3/g" "$program" > tmp3.txt
sed "s/ipipip/$ip4/g" "$program" > tmp4.txt
sed "s/ipipip/$ip5/g" "$program" > tmp5.txt
cat tmp1.txt tmp2.txt tmp3.txt tmp4.txt tmp5.txt > tmp_all.txt
grep -vE '/{3}' tmp_all.txt > "txt/${channel_key}.txt"
rm -rf tmp1.txt tmp2.txt tmp3.txt tmp4.txt tmp5.txt tmp_all.txt

#--------------------合并所有城市的txt文件为:   zubo.txt-----------------------------------------

echo "浙江电信,#genre#" >zubo.txt
cat txt/浙江电信.txt >>zubo.txt
echo "江苏电信,#genre#" >>zubo.txt
cat txt/江苏电信.txt >>zubo.txt
echo "湖北电信,#genre#" >>zubo.txt
cat txt/湖北电信.txt >>zubo.txt
echo "河南电信,#genre#" >>zubo.txt
cat txt/河南电信.txt >>zubo.txt
echo "山西联通,#genre#" >>zubo.txt
cat txt/山西联通.txt >>zubo.txt
