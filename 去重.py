import re
import os
file_contents = []
file_paths = ["zubo1.txt","zubo2.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)
# 写入合并后的文件
with open("zubo0.txt", "w", encoding="utf-8") as file:
    file.write('\n'.join(file_contents))

# 打开文档并读取所有行 
with open('zubo0.txt', 'r', encoding="utf-8") as file:
 lines = file.readlines()
# 使用列表来存储唯一的行的顺序 
 unique_lines = [] 
 seen_lines = set() 
# 遍历每一行，如果是新的就加入unique_lines 
for line in lines:
 if line not in seen_lines:
  unique_lines.append(line)
  seen_lines.add(line)
# 将唯一的行写入新的文档 
with open('zubo.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)
os.remove("zubo0.txt")
os.remove("zubo1.txt")
os.remove("zubo2.txt")
