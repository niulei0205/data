#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语文学科"其他"类型任务的高频分析
"""

import pandas as pd
import re
from collections import Counter
import numpy as np

# 读取数据
print("正在读取数据...")
df = pd.read_excel('任务明细-语文其他.xlsx')

print(f"数据总量: {len(df)} 条任务记录")
print(f"数据列: {df.columns.tolist()}\n")

# 显示数据基本信息
print("=" * 80)
print("数据概览")
print("=" * 80)
print(df.head())
print("\n")

# 检查关键字段
print("=" * 80)
print("关键字段统计")
print("=" * 80)

# 地区分布
if '门店所属地区' in df.columns:
    print("\n门店所属地区分布:")
    print(df['门店所属地区'].value_counts())

# 年级分布
if '学生年级' in df.columns:
    print("\n学生年级分布:")
    print(df['学生年级'].value_counts())

# 计划日期范围
if '计划日期' in df.columns:
    print(f"\n计划日期范围: {df['计划日期'].min()} 至 {df['计划日期'].max()}")

# 预计完成时间统计
if '预计完成时间' in df.columns:
    print(f"\n预计完成时间统计:")
    print(f"  平均时长: {df['预计完成时间'].mean():.2f} 分钟")
    print(f"  中位数: {df['预计完成时间'].median():.2f} 分钟")
    print(f"  最大值: {df['预计完成时间'].max():.2f} 分钟")
    print(f"  最小值: {df['预计完成时间'].min():.2f} 分钟")

print("\n" + "=" * 80)
print("任务描述分析 - 准备进行高频任务提取")
print("=" * 80)

# 获取任务描述列
task_desc_column = None
for col in df.columns:
    if '任务描述' in col or '描述' in col:
        task_desc_column = col
        break

if task_desc_column is None:
    print("错误: 未找到任务描述列")
    exit(1)

print(f"\n使用列: {task_desc_column}")
print(f"非空任务描述数量: {df[task_desc_column].notna().sum()}")

# 清理数据，移除空值
df_clean = df[df[task_desc_column].notna()].copy()

# 显示一些样本任务描述
print("\n任务描述样本（前20条）:")
for i, desc in enumerate(df_clean[task_desc_column].head(20), 1):
    print(f"{i}. {desc}")

print("\n正在分析任务描述，识别高频任务类型...")
