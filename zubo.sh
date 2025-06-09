#pwd
if [ $# -eq 0 ]; then
  echo "开始测试······"
  echo "在5秒内输入1~4可选择城市"
  echo "1.浙江电信"
  echo "2.江苏电信"
  echo "3.天津联通"
  echo "4.湖北电信"
  echo "5.河南电信"
  read -t 5 -p "超时未输入,将按默认设置测试" city_choice

  if [ -z "$city_choice" ]; then
      echo "未检测到输入,默认测试全部"
      city_choice=0
  fi

else
  city_choice=$1
fi
# 设置城市和相应的stream
case $city_choice in
    1)
        city="浙江电信"
        stream="udp/233.50.201.100:5140"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249Iua1meaxnyIgJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi&page=1&page_size=20"
        ;;
    2)
        city="江苏电信"
        stream="udp/239.49.8.19:9614"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249Iuaxn%2BiLjyIgJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi&page=1&page_size=10"
        ;;
    5)
        city="河北联通"
        stream="rtp/239.253.92.154:6011"
        ;;
    3)
        city="湖北电信"
        stream="rtp/239.69.1.40:9880"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249Iua5luWMlyIgJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi&page=1&page_size=20"
        ;;
    4)
        city="河南电信"
        stream="rtp/239.16.20.21:10210"
        ;;
    6)
        city="广东电信"
        stream="udp/239.77.1.152:5146"
        ;;
    7)
        city="北京联通"
        stream="rtp/239.3.1.241:8000"
	;;
    8)
        city="湖南电信"
        stream="udp/239.76.246.151:1234"
	;;
    9)
        city="辽宁联通"
        stream="rtp/232.0.0.126:1234"
        ;;
    10)
        city="四川电信"
        stream="udp/239.93.0.169:5140"
        ;;
    11)
        city="山东电信"
        stream="udp/239.21.1.87:5002"
        ;;
    12)
        city="陕西电信"
        stream="rtp/239.111.205.35:5140"
        ;;
    13)
        city="广西电信"
        stream="udp/239.81.0.107:4056"
        ;;
    14)
        city="贵州电信"
        stream="rtp/238.255.2.1:5999"
        ;;
    15)
        city="山西联通"
        stream="rtp/226.0.2.152:9128"
        ;;
    16)
        city="上海电信"
        stream="udp/239.45.3.146:5140"
        ;;
    17)
        city="福建电信"
        stream="rtp/239.61.2.132:8708"
        ;;
    18)
        city="江西电信"
        stream="udp/239.252.220.63:5140"
        ;;
    19)
        city="安徽电信"
        stream="rtp/238.1.79.27:4328"
        ;;
    20)
        city="天津联通"
        stream="udp/225.1.1.111:5002"
        ;;
    21)
        city="宁夏电信"
        stream="rtp/239.121.4.94:8538"
        ;;
    22)
        city="重庆电信"
        stream="rtp/235.254.196.249:1268"
        ;;
    23)
        city="河北电信"
        stream="rtp/239.254.200.174:6000"
        ;;
    24)
        city="河南联通"
        stream="rtp/225.1.4.98:1127"
        ;;
    25)
        city="海南电信"
        stream="rtp/239.253.64.253:5140"
        ;;
    26)
        city="黑龙江联通"
        stream="rtp/229.58.190.150:5000"
        ;;
    27)
        city="甘肃电信"
        stream="udp/239.255.30.249:8231"
        ;;
    28)
        city="新疆电信"
        stream="udp/238.125.3.174:5140"
        ;;
    29)
        city="内蒙古电信"
        stream="rtp/239.29.0.2:5000"
        ;;
    30)
        city="北京电信"
        stream="rtp/225.1.8.21:8002"
        ;;
    31)
        city="湖北联通"
        stream="rtp/228.0.0.60:6108"
        ;;
    32)
        city="吉林电信"
        stream="rtp/239.37.0.231:5540"
        ;;
    33)
        city="云南电信"
        stream="rtp/239.200.200.145:8840"
        ;;
    34)
        city="山东联通"
        stream="rtp/239.253.254.78:8000"
        ;;
    35)
        city="重庆联通"
        stream="udp/225.0.4.187:7980"
        ;;
    0)
        # 逐个处理{ }内每个选项
        for option in {1..35}; do
          bash "$0" $option  # 假定fofa.sh是当前脚本的文件名，$option将递归调用
        done
        exit 0
        ;;
esac

# 使用城市名作为默认文件名，格式为 CityName.ip
time=$(date +%m%d%H%M)
ipfile=ip/${city}_ip.txt
good_ip=ip/good_${city}_ip.txt
result_ip=ip/result_${city}_ip.txt
echo "======== 开始检索 ${city} ========"
#echo "从 fofa 获取ip+端口"
#curl -o test.html $url_fofa
#grep -E '^\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+$' test.html | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_ipfile
echo "从 '${ipfile}' 读取ip并添加到检测列表"
cat $ipfile >> tmp_ipfile
sort tmp_ipfile | uniq | sed '/^\s*$/d' > $ipfile
rm -f tmp_ipfile

while IFS= read -r ip; do
    # 尝试连接 IP 地址和端口号，并将输出保存到变量中
    tmp_ip=$(echo -n "$ip" | sed 's/:/ /')
    output=$(nc -w 1 -v -z $tmp_ip 2>&1)
    # 如果连接成功，且输出包含 "succeeded"，则将结果保存到输出文件中
    if [[ $output == *"succeeded"* ]]; then
        # 使用 awk 提取 IP 地址和端口号对应的字符串，并保存到输出文件中
        echo "$output" | grep "succeeded" | awk -v ip="$ip" '{print ip}' >> $good_ip
    fi
done < $ipfile
lines=$(wc -l < $good_ip)
echo "连接成功 $lines 个,开始测速······"
i=0
while read line; do
    i=$((i + 1))
    ip=$line
    url="http://$ip/$stream"
    #echo $url
    curl $url --connect-timeout 5 --max-time 40 -o /dev/null >zubo.tmp 2>&1
    a=$(head -n 3 zubo.tmp | awk '{print $NF}' | tail -n 1)  
    echo "第$i/$lines个：$ip    $a"
    echo "$ip    $a" >> speedtest_${city}_$time.log
done < $good_ip
#cat $good_ip > $ipfile
rm -rf zubo.tmp $good_ip

echo "测速结果排序"
awk '/M|k/{print $2"  "$1}' speedtest_${city}_$time.log | sort -n -r > $result_ip
cat $result_ip
ip1=$(awk 'NR==1{print $2}' $result_ip)
ip2=$(awk 'NR==2{print $2}' $result_ip)
ip3=$(awk 'NR==3{print $2}' $result_ip)
rm -f speedtest_${city}_$time.log $result_ip    
# 用 3 个最快 ip 生成对应城市的 txt 文件
program=template/template_${city}.txt
sed "s/ipipip/$ip1/g" $program > tmp_1.txt
sed "s/ipipip/$ip2/g" $program > tmp_2.txt
sed "s/ipipip/$ip3/g" $program > tmp_3.txt
echo "${city}-组播1,#genre#" > tmp_all.txt
cat tmp_1.txt >> tmp_all.txt
echo "${city}-组播2,#genre#" >> tmp_all.txt
cat tmp_2.txt >> tmp_all.txt
echo "${city}-组播3,#genre#" >> tmp_all.txt
cat tmp_3.txt >> tmp_all.txt
grep -vE '/{3}' tmp_all.txt > "txt/${city}.txt"
rm -f tmp_1.txt tmp_2.txt tmp_3.txt tmp_all.txt
echo "${city} 测试完成，生成可用文件：'txt/${city}.txt'"
#--------合并所有城市的txt文件---------
