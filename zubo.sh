#pwd
time=$(date +%m%d%H%M)

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
        city="Hubei_90"
        stream="rtp/239.69.1.249:11136"
        channel_key="湖北电信"
        ;;
    5)
        city="Shanxi_117"
        stream="udp/239.1.1.7:8007"
        channel_key="山西电信"
        ;;
    6)
        city="Anhui_191"
        stream="rtp/238.1.78.137:6968"
        channel_key="安徽电信"
	;;
    7)
        city="Chongqing_161"
        stream="rtp/235.254.196.249:1268"
        channel_key="重庆电信"
	;;
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1,2,4}; do
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
ipfile="ip/${channel_key}_ip"
good_ip="ip/${channel_key}_good_ip"
# 搜索最新 IP
#cat ip/${channel_key}.html | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_ipfile
cat ip/${channel_key}_good_ip >tmp_ipfile
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
mkdir -p tmpip
while read -r line; do
    ip=$(echo "$line" | sed 's/^[ \t]*//;s/[ \t]*$//')  # 去除首尾空格
    
    # 如果行不为空，则写入临时文件
    if [ -n "$ip" ]; then
        echo "$ip" > "tmpip/ip_$i.txt"  # 保存为 tmpip 目录下的临时文件
        ((i++))
    fi
done < "$good_ip"

i=0
for temp_file in tmpip/ip_*.txt; do
      ((i++))
     ip=$(<"$temp_file")  # 从临时文件中读取 IP 地址
     a=$(./speed.sh "$ip" "$stream")
     echo "第 $i/$lines 个：$ip $a"
     echo "$ip $a" >> "speedtest_${city}_$time.log"
done
rm -rf tmpip/* $ipfile $good_ip

awk '/M|k/{print $2"  "$1}' "speedtest_${city}_$time.log" | sort -n -r >"result_${city}.txt"
cat "result_${city}.txt"
ip1=$(awk 'NR==1{print $2}' result_${city}.txt)
ip2=$(awk 'NR==2{print $2}' result_${city}.txt)
ip3=$(awk 'NR==3{print $2}' result_${city}.txt)
rm -f "speedtest_${city}_$time.log"         
# 用 3 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"
sed "s/ipipip/$ip1/g" "$program" > tmp1.txt
sed "s/ipipip/$ip2/g" "$program" > tmp2.txt
sed "s/ipipip/$ip3/g" "$program" > tmp3.txt
cat tmp1.txt tmp2.txt tmp3.txt > tmp_all.txt
grep -vE '/{3}' tmp_all.txt > "txt/${channel_key}.txt"
rm -rf "result_${city}.txt" tmp1.txt tmp2.txt tmp3.txt tmp_all.txt

#--------------------合并所有城市的txt文件为:   zubo1.txt-----------------------------------------
echo "湖北电信,#genre#" >zubo1.txt
cat txt/湖北电信.txt >>zubo1.txt
echo "浙江电信,#genre#" >>zubo1.txt
cat txt/浙江电信.txt >>zubo1.txt
echo "江苏电信,#genre#" >>zubo1.txt
cat txt/江苏电信.txt >>zubo1.txt
