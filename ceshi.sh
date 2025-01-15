pwd
time=$(date +%m%d%H%M)

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
        channel_key="河南"
        ;;
    2)
        city="湖南"
        channel_key="湖南"
        ;;
    3)
        city="河北"
	channel_key="河北"
        ;;
    4)
        city="湖北"
        channel_key="湖北"
        ;;
    5)
        city="山东"
        channel_key="山东"
        ;;
    6)
        city="山西"
        channel_key="山西"
        ;;
    7)
        city="广东"
        channel_key="广东"
        ;;
    8)
        city="广西"
	channel_key="广西"
        ;;
    9)
        city="吉林"
        channel_key="吉林"
        ;;
    10)
        city="内蒙古"
        channel_key="内蒙古"
        ;;
    11)
        city="辽宁"
        channel_key="辽宁"
        ;;
    12)
        city="陕西"
        channel_key="陕西"
        ;;
    13)
        city="江苏"
        channel_key="江苏"
        ;;
    14)
        city="浙江"
        channel_key="浙江"
        ;;
    15)
        city="上海"
        channel_key="上海"
        ;;
    16)
        city="云南"
        channel_key="云南"
        ;; 
    17)
        city="四川"
        channel_key="四川"
        ;;                      
    18)
        city="重庆"
        channel_key="重庆"
        ;;
    0)
        # 如果选择是“全部选项”，则逐个处理每个选项
        for option in {1..18}; do
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
ipfile="ip/${city}.ip"
# 筛选最新 IP
echo "$ipfile"
cat ip/${channel_key}.html | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+' > tmp_onlyip
sort tmp_onlyip | uniq | sed '/^\s*$/d' > "$ipfile"
cat "$ipfile" >> 测试_ip.txt
rm -f tmp_onlyip ip/${channel_key}.html
