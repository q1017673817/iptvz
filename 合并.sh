cat 广东电信.txt >zubo.txt
cat 北京联通.txt >>zubo.txt
cat 广东联通.txt >>zubo.txt
cat 湖南电信.txt >>zubo.txt
echo "湖北电信_组播,#genre#" >>zubo.txt
cat txt/湖北电信.txt >>zubo.txt
echo "浙江电信_组播,#genre#" >>zubo.txt
cat txt/浙江电信.txt >>zubo.txt
echo "江苏电信_组播,#genre#" >>zubo.txt
cat txt/江苏电信.txt >>zubo.txt
mv -f ./广东电信.txt ./txt/广东电信.txt
mv -f ./广东联通_good_ip ./ip/广东联通_good_ip
mv -f ./北京联通.txt ./txt/北京联通.txt
mv -f ./北京联通_good_ip ./ip/北京联通_good_ip
mv -f ./广东联通.txt ./txt/广东联通.txt
mv -f ./广东联通_good_ip ./ip/广东联通_good_ip
mv -f ./湖南电信.txt ./txt/湖南电信.txt
mv -f ./湖南电信_good_ip ./ip/湖南电信_good_ip