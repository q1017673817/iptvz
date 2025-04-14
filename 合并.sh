#--------合并所有城市的txt文件---------
cat iptv1.txt > iptv.txt
echo "广东电信-组播,#genre#" >>iptv.txt
cat txt/广东电信.txt >>iptv.txt
echo "北京联通-组播,#genre#" >>iptv.txt
cat txt/北京联通.txt >>iptv.txt
echo "湖南电信-组播,#genre#" >>iptv.txt
cat txt/湖南电信.txt >>iptv.txt
echo "广东联通-组播,#genre#" >>iptv.txt
cat txt/广东联通.txt >>iptv.txt
echo "湖北电信-组播,#genre#" >>iptv.txt
cat txt/湖北电信.txt >>iptv.txt
echo "浙江电信-组播,#genre#" >>iptv.txt
cat txt/浙江电信.txt >>iptv.txt
cat txt/浙江频道.txt >>iptv.txt
echo "江苏电信-组播,#genre#" >>iptv.txt
cat txt/江苏电信.txt >>iptv.txt
echo "四川电信-组播,#genre#" >>iptv.txt
cat txt/四川电信.txt >>iptv.txt
rm -f iptv1.txt
#rm -rf 广东电信.txt 北京联通.txt 湖南电信.txt 广东联通.txt
