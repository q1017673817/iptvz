# read -p "确定要运行脚本吗？(y/n): " choice
# 判断用户的选择，如果不是"y"则退出脚本
# if [ "$choice" != "y" ]; then
#     echo "脚本已取消."
#     exit 0
# fi
pwd
time=$(date +%m%d%H%M)
i=0

if [ $# -eq 0 ]; then
  echo "请选择城市："
  echo "1. 四川电信（Sichuan_333）"
  echo "2. 浙江电信（Zhejiang_120）"
  echo "3. 江苏（Jiangsu）"
  echo "4. 广东电信（Guangdong_332）"
  echo "5. 河南电信（Henan_327）"
  echo "6. 天津联通（Tianjin_160）"
  echo "7. 湖北电信（Hubei_90）"
  echo "8. 福建电信（Fujian_114）"
  echo "9. 湖南电信（Hunan_282）"
  echo "10. 河北联通（Hebei_313）"
  echo "0. 全部"
  read -t 3 -p "输入选择或在10秒内无输入将默认选择全部: " city_choice

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
        url_fofa=$(echo  '"udpxy" && city="Chengdu" && protocol="http" || "udpxy" && city="Mianyang" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    2)
        city="Zhejiang_120"
        stream="rtp/233.50.201.63:5140"
        channel_key="浙江电信"
        url_fofa=$(echo  '"udpxy" && city="Hangzhou" && protocol="http" || "udpxy" && city="Taizhou" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    3)
        city="Jiangsu"
        stream="udp/239.49.8.16:9602"
        channel_key="江苏"
        url_fofa=$(echo  '"udpxy" && city="Nantong" && protocol="http" || "udpxy" && city="Nanjing" && protocol="http" || "udpxy" && city="Suzhou" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    4)
        city="Guangdong_332"
        stream="udp/239.77.1.152:5146"
        channel_key="广东电信"
        url_fofa=$(echo  '"udpxy" && city="Shenzhen" && protocol="http" || "udpxy" && city="Guangzhou" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    5)
        city="Henan_327"
        stream="rtp/239.16.20.21:10210"
        channel_key="河南电信"
        url_fofa=$(echo  '"udpxy" && region="Henan" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    6)
        city="Tianjin_160"
        stream="udp/225.1.1.111:5002"
        channel_key="天津联通"
        url_fofa=$(echo  '"udpxy" && region="Tianjin" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    7)
        city="Hubei_90"
        stream="rtp/239.69.1.249:11136"
        channel_key="湖北电信"
        url_fofa=$(echo  '"udpxy" && region="Hubei" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    8)
        city="Fujian_114"
        stream="rtp/239.61.2.132:8708"
        channel_key="福建电信"
        url_fofa=$(echo  '"udpxy" && region="Fujian" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    9)
        city="Hunan_282"
        stream="udp/239.76.253.100:9000"
        channel_key="湖南电信"
        url_fofa=$(echo  '"udpxy" && city="Changsha" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    10)
        city="Hebei_313"
        stream="rtp/239.253.92.154:6011"
        channel_key="河北联通"
        url_fofa=$(echo '"udpxy" && region="Hebei" && org="CHINA UNICOM China169 Backbone" && protocol="http"' | base64 |tr -d '\n')
        url_fofa="https://fofa.info/result?qbase64="$url_fofa
        ;;
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..10}; do
          bash  ./fofa.sh $option  # 假定fofa.sh是当前脚本的文件名，$option将递归调用
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
rm -f $ipfile
echo "===============检索完成================="

# 检查文件是否存在
if [ ! -f "$only_good_ip" ]; then
    echo "错误：文件 $only_good_ip 不存在。"
    exit 1
fi

lines=$(cat "$only_good_ip" | wc -l)
echo "【$only_good_ip】内 ip 共计 $lines 个"

i=0
time=$(date +%Y%m%d%H%M%S) # 定义 time 变量
while read line; do
    i=$((i + 1))
    ip=$line
    url="http://$ip/$stream"
    echo $url
    curl $url --connect-timeout 3 --max-time 10 -o /dev/null >zubo.tmp 2>&1
    a=$(head -n 3 zubo.tmp | awk '{print $NF}' | tail -n 1)

    echo "第 $i/$lines 个：$ip $a"
    echo "$ip $a" >> "speedtest_${city}_$time.log"
done < "$only_good_ip"

rm -f zubo.tmp
cat "speedtest_${city}_$time.log" | grep -E 'M|k' | awk '{print $2"  "$1}' | sort -n -r >"result/result_fofa_${city}.txt"
cat "result/result_fofa_${city}.txt"
ip1=$(head -n 1 result/result_fofa_${city}.txt | awk '{print $2}')
ip2=$(head -n 2 result/result_fofa_${city}.txt | tail -n 1 | awk '{print $2}')
ip3=$(head -n 3 result/result_fofa_${city}.txt | tail -n 1 | awk '{print $2}')
ip4=$(head -n 4 result/result_fofa_${city}.txt | tail -n 1 | awk '{print $2}')
rm -f speedtest_${city}_$time.log

# 用 4 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"

sed "s/ipipip/$ip1/g" $program > tmp1.txt
sed "s/ipipip/$ip2/g" $program > tmp2.txt
sed "s/ipipip/$ip3/g" $program > tmp3.txt
sed "s/ipipip/$ip4/g" $program > tmp4.txt
cat tmp1.txt tmp2.txt tmp3.txt tmp4.txt > txt/fofa_${city}.txt

rm -rf tmp1.txt tmp2.txt tmp3.txt tmp4.txt
rm -f $only_good_ip
#--------------------合并所有城市的txt文件为:   zubo_fofa.txt-----------------------------------------

echo "广东电信,#genre#" >zubo_fofa.txt
cat txt/fofa_Guangdong_332.txt >>zubo_fofa.txt
echo "湖南电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Hunan_282.txt >>zubo_fofa.txt
echo "湖北电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Hubei_90.txt >>zubo_fofa.txt
echo "福建电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Fujian_114.txt >>zubo_fofa.txt
echo "江苏,#genre#" >>zubo_fofa.txt
cat txt/fofa_Jiangsu.txt >>zubo_fofa.txt
echo "天津联通,#genre#" >>zubo_fofa.txt
cat txt/fofa_Tianjin_160.txt >>zubo_fofa.txt
echo "四川电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Sichuan_333.txt >>zubo_fofa.txt
echo "浙江电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Zhejiang_120.txt >>zubo_fofa.txt
echo "河北联通,#genre#" >>zubo_fofa.txt
cat txt/fofa_Hebei_313.txt >>zubo_fofa.txt
echo "河南电信,#genre#" >>zubo_fofa.txt
cat txt/fofa_Henan_327.txt >>zubo_fofa.txt
