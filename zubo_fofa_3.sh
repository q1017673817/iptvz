
time=$(date +%m%d%H%M)
i=0

if [ $# -eq 0 ]; then
  echo "请选择城市："
  echo "1. 广东电信（Guangdong_332）"
  echo "2. 安徽电信（Anhui_191）"
  echo "3. 重庆电信（Chongqing_161）"
  echo "4. 福建电信（Fujian_114）"
  echo "5. 河南电信（Henan_327）"
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
        city="Guangdong_332"
        stream="udp/239.77.0.244:5146"
        channel_key="广东电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IuW5v%2BS4nCIgJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi&page=1&page_size=20"
#        url_fofa=$(echo  '"udpxy" && region="Guangdong" && org="Chinanet" && protocol="http"' | base64 |tr -d '\n')
#        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    2)
        city="Anhui_191"
        stream="rtp/238.1.78.137:6968"
        channel_key="安徽电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IuWuieW%2BvSIgJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi&page=1&page_size=20"
#        url_fofa=$(echo  '"udpxy" && region="Anhui" && org="Chinanet" && protocol="http"' | base64 |tr -d '\n')
#        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    3)
        city="Chongqing_161"
        stream="rtp/235.254.198.102:7980"
        channel_key="重庆电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IumHjeW6hiIgJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi&page=1&page_size=20"
#        url_fofa=$(echo  '"udpxy" && region="Chongqing" && org="Chinanet" && protocol="http"' | base64 |tr -d '\n')
#        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    4)
        city="Fujian_114"
        stream="rtp/239.61.2.132:8708"
        channel_key="福建电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249Iuemj%2BW7uiIgJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi&page=1&page_size=20"
        ;;
    5)
        city="Henan_327"
        stream="rtp/239.16.20.21:10210"
        channel_key="河南电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249Iuays%2BWNlyIgJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi&page=1&page_size=20"
#        url_fofa=$(echo  '"udpxy" && region="Henan" && org="Chinanet" && protocol="http"' | base64 |tr -d '\n')
#        url_fofa="https://fofa.info/result?qbase64="$url_fofa
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

# 搜索最新 IP
echo "===============从 fofa 检索 ip+端口================="
curl -o test.html "$url_fofa"
echo "$ipfile"
grep -E '^\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+$' test.html | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_onlyip
cat ip/${channel_key}有效.ip | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' >> tmp_onlyip
sort tmp_onlyip | uniq | sed '/^\s*$/d' > $ipfile
rm -f test.html tmp_onlyip
# 遍历文件中的每个 IP 地址
while IFS= read -r ip; do
    # 尝试连接 IP 地址和端口号，并将输出保存到变量中
    tmp_ip=$(echo -n "$ip" | sed 's/:/ /')
#    echo "nc -w 1 -v -z $tmp_ip 2>&1"
    output=$(nc -w 1 -v -z $tmp_ip 2>&1)
    echo $output    
    # 如果连接成功，且输出包含 "succeeded"，则将结果保存到输出文件中
    if [[ $output == *"succeeded"* ]]; then
        # 使用 awk 提取 IP 地址和端口号对应的字符串，并保存到输出文件中
        echo "$output" | grep "succeeded" | awk -v ip="$ip" '{print ip}' >> "$only_good_ip"
    fi
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
    curl "$url" --connect-timeout 2 --max-time 8 -o /dev/null >zubo.tmp 2>&1
    a=$(head -n 3 zubo.tmp | awk '{print $NF}' | tail -n 1)
    echo "第 $i/$lines 个：$ip $a"
    echo "$ip $a" >> "speedtest_${city}_$time.log"
done < "$only_good_ip"
rm -f zubo.tmp

awk '/M|k/{print $2"  "$1}' "speedtest_${city}_$time.log" | sort -n -r >"result/result_fofa_${city}.txt"
awk '{print $2}' "result/result_fofa_${city}.txt" > ${channel_key}有效.ip
cat ip/${channel_key}有效.ip ${channel_key}有效.ip > tmp_ip
sort tmp_ip | uniq | sed '/^\s*$/d' > ip/${channel_key}有效.ip

cat "result/result_fofa_${city}.txt"
ip1=$(awk 'NR==1{print $2}' result/result_fofa_${city}.txt)
ip2=$(awk 'NR==2{print $2}' result/result_fofa_${city}.txt)
ip3=$(awk 'NR==3{print $2}' result/result_fofa_${city}.txt)
ip4=$(awk 'NR==4{print $2}' result/result_fofa_${city}.txt)
ip5=$(awk 'NR==5{print $2}' result/result_fofa_${city}.txt)
#ip6=$(awk 'NR==6{print $2}' result/result_fofa_${city}.txt)
#ip7=$(awk 'NR==7{print $2}' result/result_fofa_${city}.txt)
#ip8=$(awk 'NR==8{print $2}' result/result_fofa_${city}.txt)
rm -f "speedtest_${city}_$time.log" ${channel_key}有效.ip tmp_ip

# 用 5 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"
sed "s/ipipip/$ip1/g" "$program" > tmp1.txt
sed "s/ipipip/$ip2/g" "$program" > tmp2.txt
sed "s/ipipip/$ip3/g" "$program" > tmp3.txt
sed "s/ipipip/$ip4/g" "$program" > tmp4.txt
sed "s/ipipip/$ip5/g" "$program" > tmp5.txt
#sed "s/ipipip/$ip6/g" "$program" > tmp6.txt
#sed "s/ipipip/$ip7/g" "$program" > tmp7.txt
#sed "s/ipipip/$ip8/g" "$program" > tmp8.txt
cat tmp1.txt tmp2.txt tmp3.txt tmp4.txt tmp5.txt > tmp_all.txt
grep -vE '/{3}' tmp_all.txt > "txt/fofa_${city}.txt"
rm -rf tmp1.txt tmp2.txt tmp3.txt tmp4.txt tmp5.txt tmp_all.txt $only_good_ip 

#----合并所有城市的txt文件为: zubo_fofa.txt----
echo "广东电信,#genre#" >zubo_fofa.txt
cat txt/fofa_Guangdong_332.txt >>zubo_fofa.txt
echo "江苏电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Jiangsu.txt >>zubo_fofa.txt
echo "湖北电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Hubei_90.txt >>zubo_fofa.txt
echo "上海电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Shanghai_103.txt >>zubo_fofa.txt
echo "北京联通,#genre#" >>zubo_fofa.txt
cat txt/fofa_Beijing_liantong_145.txt >>zubo_fofa.txt
echo "浙江电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Zhejiang_120.txt >>zubo_fofa.txt
echo "四川电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Sichuan_333.txt >>zubo_fofa.txt
echo "天津联通,#genre#" >>zubo_fofa.txt
cat txt/fofa_Tianjin_160.txt >>zubo_fofa.txt
echo "河北联通,#genre#" >>zubo_fofa.txt
cat txt/fofa_Hebei_313.txt >>zubo_fofa.txt
echo "山西电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Shanxi_117.txt >>zubo_fofa.txt
echo "北京电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Beijing_dianxin_186.txt >>zubo_fofa.txt
echo "福建电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Fujian_114.txt >>zubo_fofa.txt
echo "安徽电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Anhui_191.txt >>zubo_fofa.txt
echo "重庆电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Chongqing_161.txt >>zubo_fofa.txt
echo "河南电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Henan_327.txt >>zubo_fofa.txt
echo $(TZ=UTC-8 date +%Y-%m-%d" "%H:%M:%S) >>zubo_fofa.txt
rm -rf zubo_fofa1.txt zubo_fofa2.txt zubo_fofa3.txt zubo_fofa4.txt
