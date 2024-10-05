pwd
time=$(date +%m%d%H%M)
i=0

if [ $# -eq 0 ]; then
  echo "请选择城市："
  echo "1. 四川电信（Sichuan_333）"
  echo "2. 浙江电信（Zhejiang_120）"
  echo "3. 江苏（Jiangsu）"
  echo "4. 天津联通（Tianjin_160）"
  echo "5. 湖北电信（Hubei_90）"
  echo "6. 安徽电信（Anhui_191）"
  echo "7. 河北联通（Hebei_313）"
  echo "8. 山东电信（Shandong_279）"
  echo "9. 江西电信（Jiangxi_105）"
  echo "10. 山西电信（Shanxi_117）"
  echo "11. 陕西电信（Shanxi_123）"
  echo "12. 北京联通（Beijing_liantong_145）"
  echo "13. 广东电信（Guangdong_332）"
  echo "14. 湖南电信（Hunan_282）"
  echo "0. 全部"
  read -t 3 -p "输入选择或在3秒内无输入将默认选择全部: " city_choice

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
        stream="udp/239.93.0.169:5140"
        channel_key="四川电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJDaGVuZ2R1IiAmJiBwcm90b2NvbD0iaHR0cCIgJiYgb3JnPSJDaGluYW5ldCIgJiYgaXAhPTEyNS42OS41OC4xLzI0"
        ;;
    2)
        city="Zhejiang_120"
        stream="rtp/233.50.201.63:5140"
        channel_key="浙江电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249InpoZWppYW5nIiAmJiBvcmc9IkNoaW5hbmV0IiAmJiBwcm90b2NvbD0iaHR0cCI%3D"
        ;;
    3)
        city="Jiangsu"
        stream="udp/239.49.8.16:9602"
        channel_key="江苏"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJOYW5qaW5nIiAmJiBwcm90b2NvbD0iaHR0cCIgfHwgInVkcHh5IiAmJiBjaXR5PSJTdXpob3UiICYmIHByb3RvY29sPSJodHRwIg%3D%3D"
        ;;
    4)
        city="Tianjin_160"
        stream="udp/225.1.1.111:5002"
        channel_key="天津联通"
        url_fofa=$(echo  '"udpxy" && region="Tianjin" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    5)
        city="Hubei_90"
        stream="rtp/239.69.1.249:11136"
        channel_key="湖北电信"
        url_fofa=$(echo  '"udpxy" && region="Hubei" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    6)
        city="Anhui_191"
        stream="rtp/238.1.79.27:4328"
        channel_key="安徽电信"
        url_fofa=$(echo  '"udpxy" && region="Anhui" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    7)
        city="Hebei_313"
        stream="rtp/239.253.92.154:6011"
        channel_key="河北联通"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkhlYmVpIiAmJiBvcmc9IkNISU5BIFVOSUNPTSBDaGluYTE2OSBCYWNrYm9uZSIgJiYgcHJvdG9jb2w9Imh0dHAi"
        ;;
    8)
        city="Shandong_279"
        stream="udp/239.21.1.87:5002"
        channel_key="山东电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IlNoYW5kb25nIiAmJiBvcmc9IkNoaW5hbmV0IiAmJiBwcm90b2NvbD0iaHR0cCIg"
        ;;
    9)
        city="Jiangxi_105"
        stream="udp/239.252.220.63:5140"
        channel_key="江西电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkppYW5neGkiICAmJiBvcmc9IkNoaW5hbmV0IiAmJiBwcm90b2NvbD0iaHR0cCI%3D"
        ;;
    10)
        city="Shanxi_117"
        stream="udp/239.1.1.1:8001"
        channel_key="山西电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PXRhaXl1YW4gJiYgb3JnPSJDaGluYW5ldCIgJiYgcHJvdG9jb2w9Imh0dHAi"
        ;;
    11)
        city="Shaanxi_123"
        stream="rtp/239.111.205.35:5140"
        channel_key="陕西电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IlNoYWFueGkiICYmIG9yZz0iQ2hpbmFuZXQiICYmIHByb3RvY29sPSJodHRwIg%3D%3D"
        ;;
    12)
        city="Beijing_liantong_145"
        stream="rtp/239.3.1.241:8000"
        channel_key="北京联通"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IuWMl%2BS6rCIgICYmIHByb3RvY29sPSJodHRwIg%3D%3D"
        ;;
    13)
       city="Guangdong_332"
       stream="udp/239.77.1.152:5146"
       channel_key="广东电信"
       url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJTaGVuemhlbiIgJiYgcHJvdG9jb2w9Imh0dHAiIHx8ICJ1ZHB4eSIgJiYgY2l0eT0iR3Vhbmd6aG91IiAmJiBwcm90b2NvbD0iaHR0cCI%3D"
        ;;
    14)
        city="Hunan_282"
        stream="udp/239.76.253.100:9000"
        channel_key="湖南电信"
        url_fofa="https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249Ikh1bmFuIiAmJiBwcm90b2NvbD0iaHR0cCIgJiYgb3JnPSJDaGluYW5ldCI%3D"
        ;;

    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..14}; do
          bash  ./zubo_fofa.sh $option  # 假定fofa.sh是当前脚本的文件名，$option将递归调用
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
rm -f $only_good_ip
# 搜索最新 IP
echo "===============从 fofa 检索 ip+端口================="
curl -o test.html "$url_fofa"
#echo $url_fofa
echo "$ipfile"
grep -E '^\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+$' test.html | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > "$ipfile"
rm -f test.html
# 遍历文件 A 中的每个 IP 地址
while IFS= read -r ip; do
    # 尝试连接 IP 地址和端口号，并将输出保存到变量中
    tmp_ip=$(echo -n "$ip" | sed 's/:/ /')
    echo "nc -w 1 -v -z $tmp_ip 2>&1"
    output=$(nc -w 1 -v -z $tmp_ip 2>&1)
    echo $output    
    # 如果连接成功，且输出包含 "succeeded"，则将结果保存到输出文件中
    if [[ $output == *"succeeded"* ]]; then
        # 使用 awk 提取 IP 地址和端口号对应的字符串，并保存到输出文件中
        echo "$output" | grep "succeeded" | awk -v ip="$ip" '{print ip}' >> "$only_good_ip"
    fi
done < "$ipfile"

echo "===============检索完成================="

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
    curl "$url" --connect-timeout 5 --max-time 12 -o /dev/null >zubo.tmp 2>&1
    a=$(head -n 3 zubo.tmp | awk '{print $NF}' | tail -n 1)

    echo "第 $i/$lines 个：$ip $a"
    echo "$ip $a" >> "speedtest_${city}_$time.log"
done < "$only_good_ip"

rm -f zubo.tmp
awk '/M|k/{print $2"  "$1}' "speedtest_${city}_$time.log" | sort -n -r >"result/result_fofa_${city}.txt"
cat "result/result_fofa_${city}.txt"
ip1=$(awk 'NR==1{print $2}' result/result_fofa_${city}.txt)
ip2=$(awk 'NR==2{print $2}' result/result_fofa_${city}.txt)
rm -f "speedtest_${city}_$time.log"

# 用 2 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"

sed "s/ipipip/$ip1/g" "$program" > tmp1.txt
sed "s/ipipip/$ip2/g" "$program" > tmp2.txt
cat tmp1.txt tmp2.txt > "txt/fofa_${city}.txt"

rm -rf tmp1.txt tmp2.txt tmp3.txt
rm -f $ipfile $only_good_ip

#--------------------合并所有城市的txt文件为:   zubo_fofa.txt-----------------------------------------

echo "网络电视,#genre#" >zubo_fofa.txt
cat iptv.txt >>zubo_fofa.txt
cat txt/上海电信.txt >>zubo_fofa.txt
echo "广东电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Guangdong_332.txt >>zubo_fofa.txt
echo "湖南电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Hunan_282.txt >>zubo_fofa.txt
echo "湖北电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Hubei_90.txt >>zubo_fofa.txt
echo "江苏电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Jiangsu.txt >>zubo_fofa.txt
echo "北京联通,#genre#" >>zubo_fofa.txt
cat txt/fofa_Beijing_liantong_145.txt >>zubo_fofa.txt
cat txt/北京联通.txt >>zubo_fofa.txt
cat txt/重庆电信.txt >>zubo_fofa.txt
cat txt/广西电信.txt >>zubo_fofa.txt
cat txt/河南联通.txt >>zubo_fofa.txt
echo "天津联通,#genre#" >>zubo_fofa.txt
cat txt/fofa_Tianjin_160.txt >>zubo_fofa.txt
echo "四川电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Sichuan_333.txt >>zubo_fofa.txt
echo "安徽电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Anhui_191.txt >>zubo_fofa.txt
echo "河北联通,#genre#" >>zubo_fofa.txt
cat txt/fofa_Hebei_313.txt >>zubo_fofa.txt
echo "山东电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Shandong_279.txt >>zubo_fofa.txt
echo "江西电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Jiangxi_105.txt >>zubo_fofa.txt
echo "山西电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Shanxi_117.txt >>zubo_fofa.txt
cat txt/山西电信.txt >>txt/zubo_fofa.txt
echo "浙江电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Zhejiang_120.txt >>zubo_fofa.txt
echo "陕西电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Shaanxi_123.txt >>zubo_fofa.txt
