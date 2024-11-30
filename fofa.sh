pwd
time=$(date +%m%d%H%M)
i=0

if [ $# -eq 0 ]; then
  echo "请选择城市："
  echo "1. 湖南（Hunan_100）"
  echo "2. 浙江电信（Zhejiang_120）"
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
        city="Hunan_100"
        stream="udp/239.76.245.51:1234"
        channel_key="湖南"
        ;;
    2)
        city="Zhejiang_120"
        stream="rtp/233.50.201.63:5140"
        channel_key="浙江电信"
        ;;

    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..2}; do
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
onlyport="${city}.port"
# 搜索最新 IP
echo "$ipfile"
cat ip.txt
grep -E '^\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' ip.txt | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' > "$only_good_ip"
rm -f $ipfile $onlyport
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
ip3=$(awk 'NR==3{print $2}' result/result_fofa_${city}.txt)
ip4=$(awk 'NR==4{print $2}' result/result_fofa_${city}.txt)
ip5=$(awk 'NR==5{print $2}' result/result_fofa_${city}.txt)
rm -f "speedtest_${city}_$time.log"

# 用 3 个最快 ip 生成对应城市的 txt 文件
program="template_${city}.txt"

sed "s/ipipip/$ip1/g" "$program" > tmp1.txt
sed "s/ipipip/$ip2/g" "$program" > tmp2.txt
sed "s/ipipip/$ip3/g" "$program" > tmp3.txt
sed "s/ipipip/$ip4/g" "$program" > tmp4.txt
sed "s/ipipip/$ip5/g" "$program" > tmp5.txt
cat tmp1.txt tmp2.txt tmp3.txt tmp4.txt tmp5.txt > "fofa_${city}.txt"

rm -rf tmp1.txt tmp2.txt tmp3.txt tmp4.txt tmp5.txt
rm -f $ipfile $only_good_ip

#--------------------合并所有城市的txt文件为:   zubo_fofa.txt-----------------------------------------


cat fofa_Hunan_100.txt >zubo_fofa.txt

