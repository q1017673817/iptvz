
pwd
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
    2)
        city="Shanghai_103"
        stream="udp/239.45.1.42:5140"
	channel_key="上海电信"
        ;;
    3)
        city="Beijing_liantong_145"
        stream="rtp/239.3.1.249:8001"
        channel_key="北京联通"
        ;;
    4)
        city="Sichuan_333"
        stream="udp/239.93.42.33:5140"
        channel_key="四川电信"
        ;;
    5)
        city="Hebei_313"
        stream="rtp/239.253.93.223:6401"
	channel_key="河北联通"
        ;;
    6)
        city="Shanxi_117"
        stream="udp/239.1.1.7:8007"
        channel_key="山西电信"
        ;;
    7)
        city="Tianjin_160"
        stream="udp/225.1.2.190:5002"
        channel_key="天津联通"
        ;;
    8)
        city="Guangdong_332"
        stream="udp/239.77.0.244:5146"
        channel_key="广东电信"
	;;
    9)
        city="Anhui_191"
        stream="rtp/238.1.78.137:6968"
        channel_key="安徽电信"
	;;
    10)
        city="Chongqing_161"
        stream="rtp/235.254.198.102:7980"
        channel_key="重庆电信"
	;;
    11)
        city="Ningxia"
        stream="rtp/239.121.4.94:8538"
        channel_key="宁夏电信"
        ;;
    12)
        city="Shanxi_184"
        stream="rtp/226.0.2.152:9128"
        channel_key="山西联通"
        ;;
    13)
        city="Guangxi"
        stream="udp/239.81.0.107:4056"
        channel_key="广西电信"
        ;;
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {2..13}; do
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
rm -f ip/${channel_key}.onlygood.ip
ipfile="ip/${channel_key}.ip"
onlyport="template/${city}.port"
only_good_ip="ip/${channel_key}.onlygood.ip"
# 搜索最新 IP
#cat ip/${channel_key}.html > tmp_ipfile
cat ip/${channel_key}.html | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' > tmp_ipfile
sort tmp_ipfile | uniq | sed '/^\s*$/d' > "$ipfile"
rm -f tmp_ipfile ip/${channel_key}.html

while IFS= read -r ip; do
    while IFS= read -r port; do
        # 尝试连接 IP 地址和端口号
        # nc -w 1 -v -z $ip $port
        output=$(nc -w 1 -v -z "$ip" "$port" 2>&1)
        # 如果连接成功，且输出包含 "succeeded"，则将结果保存到输出文件中
        if [[ $output == *"succeeded"* ]]; then
            # 使用 awk 提取 IP 地址和端口号对应的字符串，并保存到输出文件中
            echo "$output" | grep "succeeded" | awk -v ip="$ip" -v port="$port" '{print ip ":" port}' >> "$only_good_ip"
        fi
    done < "$onlyport"
done < "$ipfile"

lines=$(wc -l < "$only_good_ip")
echo "【$only_good_ip】内 ip 共计 $lines 个"

i=0
time=$(date +%Y%m%d%H%M%S) # 定义 time 变量
while IFS= read -r line; do
    i=$((i + 1))
    ip="$line"
    url="http://$ip/$stream"
    echo "$url"
    curl "$url" --connect-timeout 3 --max-time 10 -o /dev/null >zubo.tmp 2>&1
    a=$(head -n 3 zubo.tmp | awk '{print $NF}' | tail -n 1)
    echo "第 $i/$lines 个：$ip $a"
    echo "$ip $a" >> "speedtest_${city}_$time.log"
done < "$only_good_ip"
rm -f zubo.tmp $ipfile

cat "speedtest_${city}_$time.log" | grep -E 'M|k' | awk '{print $2"  "$1}' | sort -n -r >"result/fofa_${city}.txt"
cat "result/fofa_${city}.txt"
ip1=$(head -n 1 result/fofa_${city}.txt | awk '{print $2}')
ip2=$(head -n 2 result/fofa_${city}.txt | tail -n 1 | awk '{print $2}')
ip3=$(head -n 3 result/fofa_${city}.txt | tail -n 1 | awk '{print $2}')
ip4=$(head -n 4 result/fofa_${city}.txt | tail -n 1 | awk '{print $2}')
ip5=$(head -n 5 result/fofa_${city}.txt | tail -n 1 | awk '{print $2}')
awk '{print $2}' "result/fofa_${city}.txt" > "ip/${channel_key}有效.ip"
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
echo "广东电信,#genre#" >zubo.txt
cat txt/广东电信.txt >>zubo.txt
echo "浙江电信,#genre#" >>zubo.txt
cat txt/浙江电信.txt >>zubo.txt
echo "江苏电信,#genre#" >>zubo.txt
cat txt/江苏电信.txt >>zubo.txt
echo "湖北电信,#genre#" >>zubo.txt
cat txt/湖北电信.txt >>zubo.txt
echo "上海电信,#genre#" >>zubo.txt
cat txt/上海电信.txt >>zubo.txt
echo "北京联通,#genre#" >>zubo.txt
cat txt/北京联通.txt >>zubo.txt
echo "四川电信,#genre#" >>zubo.txt
cat txt/四川电信.txt >>zubo.txt
echo "天津联通,#genre#" >>zubo.txt
cat txt/天津联通.txt >>zubo.txt
echo "河北联通,#genre#" >>zubo.txt
cat txt/河北联通.txt >>zubo.txt
echo "山西电信,#genre#" >>zubo.txt
cat txt/山西电信.txt >>zubo.txt
echo "安徽电信,#genre#" >>zubo.txt
cat txt/安徽电信.txt >>zubo.txt
echo "重庆电信,#genre#" >>zubo.txt
cat txt/重庆电信.txt >>zubo.txt
echo "河南电信,#genre#" >>zubo.txt
cat txt/河南电信.txt >>zubo.txt
echo "山西联通,#genre#" >>zubo.txt
cat txt/山西联通.txt >>zubo.txt
echo "宁夏电信,#genre#" >>zubo.txt
cat txt/宁夏电信.txt >>zubo.txt
echo "广西电信,#genre#" >>zubo.txt
cat txt/广西电信.txt >>zubo.txt
