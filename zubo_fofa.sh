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
    1)
        city="Zhejiang_120"
        stream="rtp/233.50.201.63:5140"
        channel_key="浙江电信"
        ;;
    2)
        city="Jiangsu"
        stream="udp/239.49.8.19:9614"
        channel_key="江苏电信"
        ;;
    3)
        city="Shanghai_103"
        stream="udp/239.45.1.4:5140"
	    channel_key="上海电信"
        ;;
    4)
        city="Beijing_liantong_145"
        stream="rtp/239.3.1.236:2000"
        channel_key="北京联通"
        ;;
    5)
        city="Hubei_90"
        stream="rtp/239.254.96.96:8550"
        channel_key="湖北电信"
        ;;
    6)
        city="Sichuan_333"
        stream="udp/239.93.0.184:5140"
        channel_key="四川电信"
        ;;
    7)
        city="Beijing_dianxin_186"
        stream="/udp/225.1.8.1:8008"
        channel_key="北京电信"
        ;;
    8)
        city="Hebei_313"
        stream="rtp/239.253.92.154:6011"
	    channel_key="河北联通"
        ;;
    9)
        city="Shanxi_117"
        stream="udp/239.1.1.7:8007"
        channel_key="山西电信"
        ;;
    10)
        city="Tianjin_160"
        stream="udp/225.1.1.120:5002"
        channel_key="天津联通"
        ;;
    11)
        city="Guangdong_332"
        stream="udp/239.77.1.19:5146"
        channel_key="广东电信"
	;;
    12)
        city="Anhui_191"
        stream="rtp/238.1.79.27:4328"
        channel_key="安徽电信"
	;;
    13)
        city="Chongqing_161"
        stream="rtp/235.254.196.249:1268"
        channel_key="重庆电信"
	;;
    14)
        city="Fujian_114"
        stream="rtp/239.61.2.132:8708"
        channel_key="福建电信"
	;;
    15)
        city="Henan_327"
        stream="rtp/239.16.20.21:10210"
        channel_key="河南电信"
	;;
 
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..15}; do
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
only_good_ip="${city}.onlygood.ip"
# 搜索最新 IP
cat ip/${channel_key}.ip | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_onlyip
cat ip/${channel_key}有效.ip | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' >> tmp_onlyip
sort tmp_onlyip | uniq | sed '/^\s*$/d' > "$only_good_ip"
rm -f tmp_onlyip

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
awk '/M|k/{print $2"  "$1}' "speedtest_${city}_$time.log" | sort -n -r > "result/fofa_${channel_key}.ip"
awk '{print $2}' "result/fofa_${channel_key}.ip" > "ip/${channel_key}有效.ip"
cat "result/fofa_${channel_key}.ip"
ip1=$(awk 'NR==1{print $2}' result/fofa_${channel_key}.ip)
ip2=$(awk 'NR==2{print $2}' result/fofa_${channel_key}.ip)
ip3=$(awk 'NR==3{print $2}' result/fofa_${channel_key}.ip)
ip4=$(awk 'NR==4{print $2}' result/fofa_${channel_key}.ip)
ip5=$(awk 'NR==5{print $2}' result/fofa_${channel_key}.ip)
ip6=$(awk 'NR==6{print $2}' result/fofa_${channel_key}.ip)
ip7=$(awk 'NR==7{print $2}' result/fofa_${channel_key}.ip)
ip8=$(awk 'NR==8{print $2}' result/fofa_${channel_key}.ip)
rm -f "speedtest_${city}_$time.log"

# 用 8 个最快 ip 生成对应城市的 txt 文件
program="template/template_${city}.txt"

sed "s/ipipip/$ip1/g" "$program" > tmp1.txt
sed "s/ipipip/$ip2/g" "$program" > tmp2.txt
sed "s/ipipip/$ip3/g" "$program" > tmp3.txt
sed "s/ipipip/$ip4/g" "$program" > tmp4.txt
sed "s/ipipip/$ip5/g" "$program" > tmp5.txt
sed "s/ipipip/$ip6/g" "$program" > tmp6.txt
sed "s/ipipip/$ip7/g" "$program" > tmp7.txt
sed "s/ipipip/$ip8/g" "$program" > tmp8.txt
cat tmp1.txt tmp2.txt tmp3.txt tmp4.txt tmp5.txt tmp6.txt tmp7.txt tmp8.txt > tmp_all.txt
grep -vE '/{3}' tmp_all.txt > "txt/${channel_key}.txt"
rm -rf tmp1.txt tmp2.txt tmp3.txt tmp4.txt tmp5.txt tmp6.txt tmp7.txt tmp8.txt tmp_all.txt $only_good_ip

#--------------------合并所有城市的txt文件为:   zubo.txt-----------------------------------------

echo $(TZ=UTC-8 date +%Y-%m-%d" "%H:%M:%S) >zubo.txt
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
echo "北京电信,#genre#" >>zubo.txt
cat txt/北京电信.txt >>zubo.txt
echo "四川电信,#genre#" >>zubo.txt
cat txt/四川电信.txt >>zubo.txt
echo "天津联通,#genre#" >>zubo.txt
cat txt/天津联通.txt >>zubo.txt
echo "河北联通,#genre#" >>zubo.txt
cat txt/河北联通.txt >>zubo.txt
echo "山西电信,#genre#" >>zubo.txt
cat txt/山西电信.txt >>zubo.txt
echo "广东电信,#genre#" >>zubo.txt
cat txt/广东电信.txt >>zubo.txt
echo "福建电信,#genre#" >>zubo.txt
cat txt/福建电信.txt >>zubo.txt
echo "安徽电信,#genre#" >>zubo.txt
cat txt/安徽电信.txt >>zubo.txt
echo "重庆电信,#genre#" >>zubo.txt
cat txt/重庆电信.txt >>zubo.txt
echo "河南电信,#genre#" >>zubo.txt
cat txt/河南电信.txt >>zubo.txt

echo $(TZ=UTC-8 date +%Y-%m-%d" "%H:%M:%S) >iptvall.txt
cat iptv.txt zubo.txt >>iptvall.txt
