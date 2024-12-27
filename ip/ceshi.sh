pwd
time=$(date +%m%d%H%M)
i=0

if [ $# -eq 0 ]; then
  echo "请选择城市："
  read -t 1 -p "输入选择或在1秒内无输入将默认选择全部: " city_choice

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
        city="河南"
        stream="rtp/233.50.201.63:5140"
        channel_key="河南"
        ;;
    2)
        city="湖南"
        stream="udp/239.49.8.19:9614"
        channel_key="湖南"
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

    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..2}; do
          bash  ./ceshi.sh $option  # 假定fofa.sh是当前脚本的文件名，$option将递归调用
        done
        exit 0
        ;;

    *)
        echo "错误：无效的选择。"
        exit 1
        ;;
esac

# 使用城市名作为默认文件名，格式为 CityName.ip
ipfile="ip/${city}_ip.txt"
# 搜索最新 IP
echo "$ipfile"
cat ip/${channel_key}.html | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_onlyip
sort tmp_onlyip | uniq | sed '/^\s*$/d' > "$ipfile"
rm -f tmp_onlyip ip/${channel_key}.html
cat ip/河南_ip.txt ip/湖南_ip.txt >酒店源_ip.txt