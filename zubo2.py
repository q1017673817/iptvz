from zubo import multicast_province
config_files = ["ip/江苏_电信_config.txt", "ip/上海_电信_config.txt", "ip/浙江_电信_config.txt", "ip/江西_电信_config.txt", "ip/安徽_电信_config.txt", "ip/四川_电信_config.txt", "ip/贵州_电信_config.txt", "ip/重庆_电信_config.txt", "ip/陕西_电信_config.txt", "ip/宁夏_电信_config.txt"]
for config_file in config_files:
    multicast_province(config_file)
print(f"组播地址获取完成")
