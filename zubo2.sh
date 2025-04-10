#pwd
time=$(date +%m%d%H%M)

if [ $# -eq 0 ]; then
  echo "默认测试所有已设置好的城市组播地址"
  echo "输入1~8选择想要测试的城市"
  read -t 5 -p "5秒内未输入将测试全部城市" city_choice

  if [ -z "$city_choice" ]; then
      echo "未检测到输入，开始测试全部..."
      city_choice=0
  fi

else
  city_choice=$1
fi
# 设置城市和相应的stream
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
        # 逐个处理{ }内每个选项
        for option in {1..8}; do
          bash "$0" $option  # 假定fofa.sh是当前脚本的文件名，$option将递归调用
        done
        exit 0
        ;;
esac

# 使用城市名作为默认文件名，格式为 CityName.ip
ipfile="ip/${city}_ip.txt"
good_ip="ip/${city}_good_ip.txt"
# 从文件读取ip
cat ip/${city}_ip.txt | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_ipfile
awk '/M|k/{print $2}' "ip/result_${city}_ip.txt" | sort -n -r >>tmp_ipfile
sort tmp_ipfile | uniq | sed '/^\s*$/d' > "$ipfile"
rm -f tmp_ipfile

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
rm -f zubo.tmp $good_ip

awk '/M|k/{print $2"  "$1}' "speedtest_${city}_$time.log" | sort -n -r >"ip/result_${city}_ip.txt"
cat "ip/result_${city}_ip.txt"
ip1=$(awk 'NR==1{print $2}' "ip/result_${city}_ip.txt")
ip2=$(awk 'NR==2{print $2}' "ip/result_${city}_ip.txt")
ip3=$(awk 'NR==3{print $2}' "ip/result_${city}_ip.txt")
rm -f "speedtest_${city}_$time.log"         
# 用 3 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"
sed "s/ipipip/$ip1/g" "$program" > "txt/${city}1.txt"
sed "s/ipipip/$ip2/g" "$program" > "txt/${city}2.txt"
sed "s/ipipip/$ip3/g" "$program" > "txt/${city}3.txt"
cat "txt/${city}1.txt" "txt/${city}2.txt" "txt/${city}3.txt" > tmp_all.txt
grep -vE '/{3}' tmp_all.txt > "txt/${city}.txt"
rm -rf tmp_all.txt
