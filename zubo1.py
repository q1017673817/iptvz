from zubo import multicast_province
config_files = ["ip/广东_电信_config.txt", "ip/广东_联通_config.txt", "ip/广西_电信_config.txt",
                "ip/湖南_电信_config.txt", "ip/湖北_电信_config.txt", "ip/福建_电信_config.txt",
                "ip/山东_电信_config.txt", "ip/山西_联通_config.txt", "ip/河南_电信_config.txt",
                "ip/河北_联通_config.txt", "ip/北京_联通_config.txt", "ip/天津_联通_config.txt"]
for config_file in config_files:
    multicast_province(config_file)
print(f"组播地址获取完成")
