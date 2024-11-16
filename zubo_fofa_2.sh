#!/bin/bash
# cd /root/iptv
# read -p "确定要运行脚本吗？(y/n): " choice

# 判断用户的选择，如果不是"y"则退出脚本
# if [ "$choice" != "y" ]; then
#     echo "脚本已取消."
#     exit 0
# fi

time=$(date +%m%d%H%M)
i=0

if [ $# -eq 0 ]; then
  echo "请选择城市："
  echo "1. 四川电信（Sichuan_333）"
  echo "2. 安徽电信（Anhui_191）"
  echo "3. 河北联通（Hebei_313）"
  echo "4. 山西电信（Shanxi_117）"
  echo "5. 天津联通（Tianjin_160）"
  echo "0. 全部"
  read -t 1 -p "输入选择或在10秒内无输入将默认选择全部: " city_choice

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
        city="Sichuan_333"
        stream="udp/239.93.0.184:5140"
        channel_key="四川电信"
        url_fofa=$(echo  '"udpxy" && region="Sichuan" && org="Chinanet" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    2)
        city="Anhui_191"
        stream="rtp/238.1.78.166:7200"
        channel_key="安徽电信"
        url_fofa=$(echo  '"udpxy" && region="Anhui" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
        ;;
    3)
        city="Hebei_313"
        stream="rtp/239.253.92.154:6011"
	channel_key="河北联通"
        url_fofa=$(echo  '"udpxy" && region="Hebei" && org="CHINA UNICOM China169 Backbone" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    4)
        city="Shanxi_117"
        stream="udp/239.1.1.7:8007"
        channel_key="山西电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PXRhaXl1YW4gJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi"
        ;;
    5)
        city="Tianjin_160"
        stream="udp/225.1.1.120:5002"
        channel_key="天津联通"
        url_fofa=$(echo  '"udpxy" && country="CN" && region="Tianjin" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..5}; do
          bash  "$0" $option  # 假定fofa.sh是当前脚本的文件名，$option将递归调用
        done
        exit 0
        ;;
    *)
        echo "错误：无效的选择。"
        exit 1
        ;;
esac



# 使用城市名作为默认文件名，格式为 CityName.ip
ipfile="${city}.ip"
only_good_ip="${city}.onlygood.ip"
onlyport="template/${city}.port"

echo $(TZ=UTC-8 date +%Y-%m-%d" "%H:%M:%S) >iptvall.txt
cat iptv.txt zubo.txt zubo_fofa1.txt zubo_fofa2.txt >>iptvall.txt
# 搜索最新 IP
echo "===============从 fofa 检索 ip+端口================="
curl -o test.html "$url_fofa"
#echo $url_fofa
echo "$ipfile"
grep -E '^\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+$' test.html | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' > tmp_onlyip
sort tmp_onlyip | uniq | sed '/^\s*$/d' > $ipfile
rm -f test.html tmp_onlyip
# 遍历文件中的每个 IP 地址
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

echo "===============检索完成================="
rm -f "$ipfile"
# 检查文件是否存在
if [ ! -f "$only_good_ip" ]; then
    echo "错误：文件 $only_good_ip 不存在。"
    exit 1
fi

lines=$(wc -l < "$only_good_ip")
echo "【$only_good_ip】内 ip 共计 $lines 个"

i=0
time=$(date +%Y%m%d%H%M%S) # 定义 time 变量
while IFS= read -r line; do
    i=$((i + 1))
    ip="$line"
    url="http://$ip/$stream"
    echo "$url"
    curl "$url" --connect-timeout 5 --max-time 15 -o /dev/null >zubo.tmp 2>&1
    a=$(head -n 3 zubo.tmp | awk '{print $NF}' | tail -n 1)

    echo "第 $i/$lines 个：$ip $a"
    echo "$ip $a" >> "speedtest_${city}_$time.log"
done < "$only_good_ip"
rm -f zubo.tmp

awk '/M|k/{print $2"  "$1}' "speedtest_${city}_$time.log" | sort -n -r >"result/result_fofa_${city}.txt"
cat "result/result_fofa_${city}.txt"
ip1=$(awk 'NR==1{print $2}' result/result_fofa_${city}.txt)
ip2=$(awk 'NR==2{print $2}' result/result_fofa_${city}.txt)
ip3=$(awk 'NR==3{print $2}' result/result_fofa_${city}.txt)
rm -f "speedtest_${city}_$time.log"

# 用 3 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"
sed "s/ipipip/$ip1/g" "$program" > tmp1.txt
sed "s/ipipip/$ip2/g" "$program" > tmp2.txt
sed "s/ipipip/$ip3/g" "$program" > tmp3.txt
#cat tmp1.txt tmp2.txt tmp3.txt > "txt/fofa_${city}.txt"
cat tmp1.txt tmp2.txt tmp3.txt > tmp_all.txt
grep -vE '/{3}' tmp_all.txt > "txt/fofa_${city}.txt"

rm -rf tmp1.txt tmp2.txt tmp3.txt tmp_all.txt $only_good_ip 


#--------------------合并所有城市的txt文件为:   zubo_fofa.txt-----------------------------------------


echo "安徽电信,#genre#" >zubo_fofa2.txt
cat txt/fofa_Anhui_191.txt >>zubo_fofa2.txt
echo "四川电信,#genre#" >>zubo_fofa2.txt
cat txt/fofa_Sichuan_333.txt >>zubo_fofa2.txt
echo "天津联通,#genre#" >>zubo_fofa2.txt
cat txt/fofa_Tianjin_160.txt >>zubo_fofa2.txt
echo "河北联通,#genre#" >>zubo_fofa2.txt
cat txt/fofa_Hebei_313.txt >>zubo_fofa2.txt
echo "山西电信,#genre#" >>zubo_fofa2.txt
cat txt/fofa_Shanxi_117.txt >>zubo_fofa2.txt
