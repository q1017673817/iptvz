#pwd
time=$(date +%m%d%H%M)

if [ $# -eq 0 ]; then
  echo "请选择城市："
  echo "0. 全部"
  read -t 1 -p "输入选择或在1秒内无输入将默认选择全部: " city_choice

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
        city="浙江电信"
        stream="udp/233.50.201.63:5140"
        channel_key="浙江电信"
        ;;
    2)
        city="江苏电信"
        stream="udp/239.49.8.19:9614"
        channel_key="江苏电信"
        ;;
    3)
        city="四川电信"
        stream="udp/239.93.0.169:5140"
	    channel_key="四川电信"
        ;;
    4)
        city="湖北电信"
        stream="rtp/239.69.1.249:11136"
        channel_key="湖北电信"
        ;;
    5)
        city="广东电信"
        stream="udp/239.77.1.19:5146"
        channel_key="广东电信"
        ;;
    6)
        city="北京联通"
        stream="rtp/239.3.1.241:8000"
        channel_key="北京联通"
	    ;;
    7)
        city="湖南电信"
        stream="udp/239.76.246.101:1234"
        channel_key="湖南电信"
	    ;;
    8)
        city="广东联通"
        stream="udp/239.0.1.1:5001"
        channel_key="广东联通"
	    ;;
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..8}; do
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
ipfile="ip/${city}_ip"
good_ip="ip/${city}_good_ip"
# 搜索最新 IP
cat ip/${city}_ip | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_ipfile
cat ip/${city}_good_ip >>tmp_ipfile
sort tmp_ipfile | uniq | sed '/^\s*$/d' > "$ipfile"
rm -f tmp_ipfile $good_ip

while IFS= read -r ip; do
    # 尝试连接 IP 地址和端口号，并将输出保存到变量中
    tmp_ip=$(echo -n "$ip" | sed 's/:/ /')
    #echo "nc -w 1 -v -z $tmp_ip 2>&1"
    output=$(nc -w 1 -v -z $tmp_ip 2>&1)
    echo $output   
    # 如果连接成功，且输出包含 "succeeded"，则将结果保存到输出文件中
    if [[ $output == *"succeeded"* ]]; then
        # 使用 awk 提取 IP 地址和端口号对应的字符串，并保存到输出文件中
        echo "$output" | grep "succeeded" | awk -v ip="$ip" '{print ip}' >> "$good_ip"
    fi
done < "$ipfile"

lines=$(wc -l < "$good_ip")
echo "【$good_ip】内 ip 共计 $lines 个"

i=0
while read line; do
    i=$((i + 1))
    ip=$line
    url="http://$ip/$stream"
    echo $url
    curl $url --connect-timeout 2 --max-time 60 -o /dev/null >zubo.tmp 2>&1
    a=$(head -n 3 zubo.tmp | awk '{print $NF}' | tail -n 1)  

    echo "第$i/$lines个：$ip    $a"
    echo "$ip    $a" >> "speedtest_${city}_$time.log"
done < "$good_ip"
rm -f zubo.tmp

awk '/M|k/{print $2"  "$1}' "speedtest_${city}_$time.log" | sort -n -r >"ip/result_${city}.txt"
cat "ip/result_${city}.txt"
ip1=$(awk 'NR==1{print $2}' "ip/result_${city}.txt")
ip2=$(awk 'NR==2{print $2}' "ip/result_${city}.txt")
ip3=$(awk 'NR==3{print $2}' "ip/result_${city}.txt")
rm -f "speedtest_${city}_$time.log"         
# 用 3 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"
sed "s/ipipip/$ip1/g" "$program" > "txt/${city}1.txt"
sed "s/ipipip/$ip2/g" "$program" > "txt/${city}2.txt"
sed "s/ipipip/$ip3/g" "$program" > "txt/${city}3.txt"
cat "txt/${city}1.txt" "txt/${city}2.txt" "txt/${city}3.txt" > tmp_all.txt
grep -vE '/{3}' tmp_all.txt > "txt/${city}.txt"
rm -rf tmp_all.txt

#--------------------合并所有城市的txt文件为:   zubo2.txt-----------------------------------------
cat 广东电信.txt >zubo2.txt
cat 北京联通.txt >>zubo2.txt
cat 湖南电信.txt >>zubo2.txt
cat 广东联通.txt >>zubo2.txt
echo "湖北电信-组播,#genre#" >>zubo2.txt
cat txt/湖北电信.txt >>zubo2.txt
echo "浙江电信-组播,#genre#" >>zubo2.txt
cat txt/浙江电信.txt >>zubo2.txt
echo "江苏电信-组播,#genre#" >>zubo2.txt
cat txt/江苏电信.txt >>zubo2.txt
echo "四川电信-组播,#genre#" >>zubo2.txt
cat txt/四川电信.txt >>zubo2.txt

echo "广东电信-组播1,#genre#" >zubo.txt
cat txt/广东电信1.txt >>zubo.txt
echo "广东电信-组播2,#genre#" >>zubo.txt
cat txt/广东电信2.txt >>zubo.txt
echo "广东电信-组播3,#genre#" >>zubo.txt
cat txt/广东电信3.txt >>zubo.txt

echo "北京联通-组播1,#genre#" >>zubo.txt
cat txt/北京联通1.txt >>zubo.txt
echo "北京联通-组播2,#genre#" >>zubo.txt
cat txt/北京联通2.txt >>zubo.txt
echo "北京联通-组播3,#genre#" >>zubo.txt
cat txt/北京联通3.txt >>zubo.txt

echo "湖南电信-组播1,#genre#" >>zubo.txt
cat txt/湖南电信1.txt >>zubo.txt
echo "湖南电信-组播2,#genre#" >>zubo.txt
cat txt/湖南电信2.txt >>zubo.txt
cat 广东联通.txt >>zubo.txt

echo "湖北电信-组播1,#genre#" >>zubo.txt
cat txt/湖北电信1.txt >>zubo.txt
echo "湖北电信-组播2,#genre#" >>zubo.txt
cat txt/湖北电信2.txt >>zubo.txt
echo "湖北电信-组播3,#genre#" >>zubo.txt
cat txt/湖北电信3.txt >>zubo.txt

echo "浙江电信-组播1,#genre#" >>zubo.txt
cat txt/浙江电信1.txt >>zubo.txt
echo "浙江电信-组播2,#genre#" >>zubo.txt
cat txt/浙江电信2.txt >>zubo.txt
echo "浙江电信-组播3,#genre#" >>zubo.txt
cat txt/浙江电信3.txt >>zubo.txt

echo "江苏电信-组播1,#genre#" >>zubo.txt
cat txt/江苏电信1.txt >>zubo.txt
echo "江苏电信-组播2,#genre#" >>zubo.txt
cat txt/江苏电信2.txt >>zubo.txt
echo "江苏电信-组播3,#genre#" >>zubo.txt
cat txt/江苏电信3.txt >>zubo.txt

echo "四川电信-组播1,#genre#" >>zubo.txt
cat txt/四川电信1.txt >>zubo.txt
echo "四川电信-组播2,#genre#" >>zubo.txt
cat txt/四川电信2.txt >>zubo.txt
echo "四川电信-组播3,#genre#" >>zubo.txt
cat txt/四川电信3.txt >>zubo.txt

