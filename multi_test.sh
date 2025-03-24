#read -p "确定要运行脚本吗？(y/n): " choice
pwd
time=$(date +%m%d%H%M)
i=0

if [ $# -eq 0 ]; then
  echo "请选择城市："
  echo "0. 全部"
  read -t 1 -p "输入选择或在3秒内无输入将默认选择全部: " city_choice

  if [ -z "$city_choice" ]; then
      echo "未检测到输入，自动选择全部选项..."
      city_choice=1
  fi

else
  city_choice=$1
fi

# 根据用户选择设置城市和相应的stream
case $city_choice in
    1)
        city="Hubei_90"
        stream="rtp/239.69.1.249:11136"
        channel_key="湖北综合"
        ;;
    2)
        city="Zhejiang_120"
        stream="rtp/233.50.201.63:5140"
        channel_key="浙江电信"
        ;;
    3)
        city="Henan_327"
        stream="rtp/239.16.20.1:10010"
        channel_key="河南电信"
        ;;
    4)
        city="Shanxi_117"
        stream="udp/239.1.1.7:8007"
        channel_key="山西电信" 
        ;;
    5)
        city="Tianjin_160"
        stream="udp/225.1.2.190:5002"
        channel_key="天津联通"
        ;;    
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..5}; do
          bash  ./multi_test.sh $option  # 假定script_name.sh是当前脚本的文件名，$option将递归调用
        done
        exit 0
        ;;

    *)
        echo "错误：无效的选择。"
        exit 1
        ;;
esac

# 使用城市名作为默认文件名，格式为 CityName.ip
ipfile="ip/${city}.ip"
only_good_ip="ip/${city}.onlygood.ip"
onlyport="template/${city}.port"
# 搜索最新ip

#echo "===============从tonkiang检索    $channel_key    最新ip================="
/usr/bin/python3 hoteliptv.py $channel_key  >test.html
grep -o "href='hotellist.html?s=[^']*'"  test.html > tempip.txt
sed -n "s/^.*href='hotellist.html?s=\([^:]*\):[0-9].*/\1/p" tempip.txt > tmp_onlyip
sort tmp_onlyip | uniq | sed '/^\s*$/d' > $ipfile
rm -f test.html tempip.txt tmp_onlyip $only_good_ip
# 遍历ip和端口组合
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

rm -f $ipfile
echo "===============检索完成================="
# 检查文件是否存在
if [ ! -f "$only_good_ip" ]; then
    echo "错误：文件 $only_good_ip 不存在。"
    exit 1
fi

lines=$(wc -l < "$only_good_ip")
echo "【$only_good_ip】内 ip 共计 $lines 个"
i=0
while read line; do
    i=$((i + 1))
    ip=$line
    url="http://$ip/$stream"
    echo $url
    curl $url --connect-timeout 3 --max-time 20 -o /dev/null >zubo.tmp 2>&1
    a=$(head -n 3 zubo.tmp | awk '{print $NF}' | tail -n 1)  

    echo "第$i/$lines个：$ip    $a"
    echo "$ip    $a" >> "speedtest_${city}_$time.log"
done < "$only_good_ip"

rm -f zubo.tmp 
cat "speedtest_${city}_$time.log" | grep -E 'M|k' | awk '{print $2"  "$1}' | sort -n -r >"result/result_${city}.txt"
cat "result/result_${city}.txt"
ip1=$(head -n 1 result/result_${city}.txt | awk '{print $2}')
ip2=$(head -n 2 result/result_${city}.txt | tail -n 1 | awk '{print $2}')
rm -f speedtest_${city}_$time.log 

#----------------------用2个最快ip生成对应城市的txt文件---------------------------

# if [ $city = "Shanghai_103" ]; then
program="template/template_${city}.txt"
# else
#     program="template_min/template_${city}.txt"
# fi

sed "s/ipipip/$ip1/g" $program >tmp1.txt
sed "s/ipipip/$ip2/g" $program >tmp2.txt
cat tmp1.txt tmp2.txt >txt/${city}.txt

rm -rf tmp1.txt tmp2.txt

#--------------------合并所有城市的txt文件为:   zubo.txt-----------------------------------------
echo "湖北电信,#genre#" >zubo3.txt
cat txt/Hubei_90.txt >>zubo3.txt

