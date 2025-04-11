time=$(date +%Y/%m/%d)
#-------旧文件备份------
cat iptv.txt >iptv_备份.txt
cat zubo.txt >zubo_备份.txt
#--------合并所有城市的txt文件---------
cat 广东电信.txt 北京联通.txt 湖南电信.txt 广东联通.txt >zubo2.txt
echo "湖北电信-组播,#genre#" >>zubo2.txt
cat txt/湖北电信.txt >>zubo2.txt
echo "浙江电信-组播,#genre#" >>zubo2.txt
cat txt/浙江电信.txt >>zubo2.txt
echo "江苏电信-组播,#genre#" >>zubo2.txt
cat txt/江苏电信.txt >>zubo2.txt
echo "四川电信-组播,#genre#" >>zubo2.txt
cat txt/四川电信.txt >>zubo2.txt

echo "广东电信-组播1 $time 更新,#genre#" >zubo.txt
cat txt/广东电信1.txt >>zubo.txt
echo "广东电信-组播2,#genre#" >>zubo.txt
cat txt/广东电信2.txt >>zubo.txt
echo "广东电信-组播3,#genre#" >>zubo.txt
cat txt/广东电信3.txt >>zubo.txt
echo "北京联通-组播1,#genre#" >>zubo.txt
cat txt/北京联通1.txt >>zubo.txt
echo "北京联通-组播2,#genre#" >>zubo.txt
cat txt/北京联通2.txt >>zubo.txt
echo "北京联通-组播3,#genre#" >>zubo.txt
cat txt/北京联通3.txt >>zubo.txt
echo "湖南电信-组播1,#genre#" >>zubo.txt
cat txt/湖南电信1.txt >>zubo.txt
echo "湖南电信-组播2,#genre#" >>zubo.txt
cat txt/湖南电信2.txt >>zubo.txt
cat 广东联通.txt >>zubo.txt
echo "湖北电信-组播1,#genre#" >>zubo.txt
cat txt/湖北电信1.txt >>zubo.txt
echo "湖北电信-组播2,#genre#" >>zubo.txt
cat txt/湖北电信2.txt >>zubo.txt
echo "湖北电信-组播3,#genre#" >>zubo.txt
cat txt/湖北电信3.txt >>zubo.txt
echo "浙江电信-组播1,#genre#" >>zubo.txt
cat txt/浙江电信1.txt >>zubo.txt
echo "浙江电信-组播2,#genre#" >>zubo.txt
cat txt/浙江电信2.txt >>zubo.txt
echo "浙江电信-组播3,#genre#" >>zubo.txt
cat txt/浙江电信3.txt >>zubo.txt
echo "江苏电信-组播1,#genre#" >>zubo.txt
cat txt/江苏电信1.txt >>zubo.txt
echo "江苏电信-组播2,#genre#" >>zubo.txt
cat txt/江苏电信2.txt >>zubo.txt
echo "江苏电信-组播3,#genre#" >>zubo.txt
cat txt/江苏电信3.txt >>zubo.txt
echo "四川电信-组播1,#genre#" >>zubo.txt
cat txt/四川电信1.txt >>zubo.txt
echo "四川电信-组播2,#genre#" >>zubo.txt
cat txt/四川电信2.txt >>zubo.txt
echo "四川电信-组播3,#genre#" >>zubo.txt
cat txt/四川电信3.txt >>zubo.txt

rm -f 广东电信.txt 北京联通.txt 湖南电信.txt 广东联通.txt
