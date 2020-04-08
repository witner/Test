#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 导入系统模块

# 第三方模块
import pandas as pd
# 导入自定义模块

# 设置环境变量

def handle_df_result(df):
    df_result = df['Result']
    df_standard = df['Standard']
    df_result_list = df_result.split(',')
    result = df_result_list[0]
    remark = 'sss'
    df['Result'] = result
    df['Remark'] = remark

    return df


if __name__ == '__main__':
    df = pd.read_excel('1.xlsx')
    print(df)

    rr = df.apply(lambda x: handle_df_result(x), axis=1)
    print(rr)
    df = rr
    print(df)

