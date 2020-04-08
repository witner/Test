#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 导入系统模块
import os
import sys
# 第三方模块

# 导入自定义模块

# 设置环境变量
if __name__ == '__main__':
    try:
        file, file_name, file_context, file_size = sys.argv
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        file_size = int(file_size) * 1024 * 1024
        print(file_path, file_size)

    except Exception as e:
        print('$python getfile.py file_name file_context file_size(M)')
        print('eg:生成10M的文件 $python getfile.py 1.txt "I Love You" "10"')

    with open(file_path, 'w', encoding='UTF-8') as f:
        f.seek(file_size)
        f.write(str(file_context))
    print('成功生文件：', file_path)



