from zubo import multicast_province
config_files = ["ip/江苏电信_config.txt", "ip/上海电信_config.txt", "ip/浙江电信_config.txt", "ip/江西电信_config.txt", "ip/安徽电信_config.txt", "ip/四川电信_config.txt", "ip/贵州电信_config.txt", "ip/重庆电信_config.txt", "ip/陕西电信_config.txt", "ip/宁夏电信_config.txt"]
for config_file in config_files:
    multicast_province(config_file)
print(f"组播地址获取完成")
