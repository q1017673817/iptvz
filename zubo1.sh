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
city_choice=0
# 根据用户选择设置城市和相应的stream
case $city_choice in
    1)
        city="Chongqing_161"
        stream="rtp/235.254.196.249:1268"
        channel_key="重庆电信"
	    ;;
    2)
        city="Fujian_114"
        stream="rtp/239.61.2.132:8708"
        channel_key="福建电信"
	    ;;
    3)
        city="Henan_327"
        stream="rtp/239.16.20.21:10210"
        channel_key="河南电信"
	    ;;
    4)
        city="Ningxia"
        stream="rtp/239.121.4.94:8538"
        channel_key="宁夏电信"
        ;;
    5)
        city="Shandong_279"
        stream="udp/239.21.1.87:5002"
        channel_key="山东电信"
        ;;
    6)
        city="Shanxi_184"
        stream="rtp/226.0.2.152:9128"
        channel_key="山西联通"
        ;;
    7)
        city="Guangxi"
        stream="udp/239.81.0.107:4056"
        channel_key="广西电信"
        ;;
    8)
        city="Henan_172"
        stream="rtp/225.1.4.98:1127"
        channel_key="河南联通"
        ;;
    9)
        city="Shaanxi_123"
        stream="rtp/239.111.205.35:5140"
        channel_key="陕西电信"
        ;;
    10)
        city="Jiangxi_105"
        stream="udp/239.252.220.63:5140"
        channel_key="江西电信"
        ;;
    11)
        city="Hunan_282"
        stream="udp/239.76.246.101:1234"
        channel_key="湖南电信"
        ;;
    12)
        city="Guizhou_153"
        stream="rtp/238.255.2.1:5999"
        channel_key="贵州电信"
        ;;
   13)
        city="Chongqing_77"
        stream="udp/225.0.4.188:7980"
        channel_key="重庆联通"
        ;;
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..13}; do
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
ip_file="ip/${channel_key}_ip"
good_ip2="ip/${channel_key}_good_ip"
# 搜索最新 IP
cat ip/${channel_key}.html | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_ip
sort tmp_ip | uniq | sed '/^\s*$/d' > "$ip_file"
rm -f tmp_ip ip/${channel_key}.html

while IFS= read -r ip; do
    # 尝试连接 IP 地址和端口号，并将输出保存到变量中
    tmp_ip2=$(echo -n "$ip" | sed 's/:/ /')
    #echo "nc -w 1 -v -z $tmp_ip 2>&1"
    output=$(nc -w 1 -v -z $tmp_ip2 2>&1)
    echo $output   
    # 如果连接成功，且输出包含 "succeeded"，则将结果保存到输出文件中
    if [[ $output == *"succeeded"* ]]; then
        # 使用 awk 提取 IP 地址和端口号对应的字符串，并保存到输出文件中
        echo "$output" | grep "succeeded" | awk -v ip="$ip" '{print ip}' >> "$good_ip2"
    fi
done < "$ip_file"

lines=$(wc -l < "$good_ip2")
echo "【$good_ip2】内 ip 共计 $lines 个"

i=0
time=$(date +%Y%m%d%H%M%S) # 定义 time 变量
while IFS= read -r line; do
    i=$((i + 1))
    ip="$line"
    url="http://$ip/$stream"
    echo "$url"
    curl "$url" --connect-timeout 3 --max-time 20 -o /dev/null >zubo_tmp 2>&1
    a=$(head -n 3 zubo_tmp | awk '{print $NF}' | tail -n 1)
    echo "第 $i/$lines 个：$ip $a"
    echo "$ip $a" >> "speedtest_${city}_$time.log"
done < "$good_ip2"

rm -f zubo_tmp $ip_file 

cat "speedtest_${city}_$time.log" | grep -E 'M|k' | awk '{print $2"  "$1}' | sort -n -r >"${city}.txt"
cat "${city}.txt"
ip1=$(head -n 1 ${city}.txt | awk '{print $2}')
ip2=$(head -n 2 ${city}.txt | tail -n 1 | awk '{print $2}')
ip3=$(head -n 3 ${city}.txt | tail -n 1 | awk '{print $2}')
ip4=$(head -n 4 ${city}.txt | tail -n 1 | awk '{print $2}')
ip5=$(head -n 5 ${city}.txt | tail -n 1 | awk '{print $2}')
rm -f "speedtest_${city}_$time.log"         
# 用 5 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"
sed "s/ipipip/$ip1/g" "$program" > tmp_1.txt
sed "s/ipipip/$ip2/g" "$program" > tmp_2.txt
sed "s/ipipip/$ip3/g" "$program" > tmp_3.txt
sed "s/ipipip/$ip4/g" "$program" > tmp_4.txt
sed "s/ipipip/$ip5/g" "$program" > tmp_5.txt
cat tmp_1.txt tmp_2.txt tmp_3.txt tmp_4.txt tmp_5.txt > tmp_all2.txt
grep -vE '/{3}' tmp_all2.txt > txt/"${channel_key}.txt"
rm -rf "${city}.txt" tmp_1.txt tmp_2.txt tmp_3.txt tmp_4.txt tmp_5.txt tmp_all2.txt

#--------------------合并所有城市的txt文件为:   zubo2.txt-----------------------------------------

echo "重庆电信,#genre#" >zubo2.txt
cat txt/重庆电信.txt >>zubo2.txt
echo "福建电信,#genre#" >>zubo2.txt
cat txt/福建电信.txt >>zubo2.txt
echo "河南电信,#genre#" >>zubo2.txt
cat txt/河南电信.txt >>zubo2.txt
echo "宁夏电信,#genre#" >>zubo2.txt
cat txt/宁夏电信.txt >>zubo2.txt
echo "山东电信,#genre#" >>zubo2.txt
cat txt/山东电信.txt >>zubo2.txt
echo "山西联通,#genre#" >>zubo2.txt
cat txt/山西联通.txt >>zubo2.txt
echo "广西电信,#genre#" >>zubo2.txt
cat txt/广西电信.txt >>zubo2.txt
echo "河南联通,#genre#" >>zubo2.txt
cat txt/河南联通.txt >>zubo2.txt
echo "陕西电信,#genre#" >>zubo2.txt
cat txt/陕西电信.txt >>zubo2.txt
echo "江西电信,#genre#" >>zubo2.txt
cat txt/江西电信.txt >>zubo2.txt
echo "湖南电信,#genre#" >>zubo2.txt
cat txt/湖南电信.txt >>zubo2.txt
echo "贵州电信,#genre#" >>zubo2.txt
cat txt/贵州电信.txt >>zubo2.txt
echo "重庆联通,#genre#" >>zubo2.txt
cat txt/重庆联通.txt >>zubo2.txt