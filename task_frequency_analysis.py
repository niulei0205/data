#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高频任务分类分析
通过关键词匹配识别任务类型，并统计频次和平均时长
"""

import pandas as pd
import re
from collections import defaultdict
import numpy as np

# 读取数据
df = pd.read_excel('任务明细-语文其他.xlsx')

# 剔除年级为"未知"的数据
df_clean = df[df['学生年级'] != '未知'].copy()
print(f"原始数据: {len(df)} 条")
print(f"剔除年级未知后: {len(df_clean)} 条")
print()

# 任务分类关键词定义
# 按照优先级顺序匹配（更具体的放在前面）
task_categories = {
    '练字': [r'练字', r'写字', r'字帖', r'硬笔', r'软笔', r'书写练习'],
    '阅读': [r'阅读', r'读书', r'看书', r'读.*书', r'课外阅读', r'整本书'],
    '朗读': [r'朗读', r'朗诵', r'朗读课文'],
    '背诵': [r'背诵', r'背课文', r'背.*段落', r'必背'],
    '复习': [r'复习', r'复习.*知识点', r'单元复习'],
    '预习': [r'预习', r'预习课文'],
    '默写': [r'默写', r'听写'],
    '抄写': [r'抄写', r'抄.*词语', r'抄课文', r'抄.*生字'],
    '日记': [r'日记', r'写日记'],
    '周记': [r'周记'],
    '摘抄': [r'摘抄', r'摘录', r'好词好句'],
    '识字': [r'识字', r'认字', r'生字'],
    '拼音': [r'拼音'],
    '口语交际': [r'口语交际'],
    '手抄报': [r'手抄报'],
    '观察': [r'观察日记', r'观察.*记录'],
    '课文改写': [r'改写', r'仿写', r'缩写'],
    '资料搜集': [r'搜集.*资料', r'收集.*资料', r'查找.*资料'],
}

def classify_task(description):
    """
    根据任务描述分类任务类型
    返回匹配到的第一个类别
    """
    if pd.isna(description):
        return '其他'
    
    desc_str = str(description)
    
    # 按优先级匹配
    for category, patterns in task_categories.items():
        for pattern in patterns:
            if re.search(pattern, desc_str, re.IGNORECASE):
                return category
    
    return '其他'

# 对每个任务进行分类
print("正在对任务进行分类...")
df_clean['任务分类'] = df_clean['学校作业任务描述'].apply(classify_task)

print("\n" + "=" * 100)
print("高频任务统计分析")
print("=" * 100)

# 统计各类任务的频次
task_stats = df_clean.groupby('任务分类').agg({
    '学习任务ID': 'count',  # 任务数量
    '预计完成时间': ['mean', 'median', 'min', 'max']  # 时间统计
}).round(2)

task_stats.columns = ['任务数量', '平均时长(分钟)', '中位数时长(分钟)', '最短时长(分钟)', '最长时长(分钟)']
task_stats = task_stats.sort_values('任务数量', ascending=False)

# 计算占比
task_stats['占比(%)'] = (task_stats['任务数量'] / len(df_clean) * 100).round(2)

print("\n任务分类统计表:")
print(task_stats.to_string())

# 导出到Excel
task_stats.to_excel('高频任务统计.xlsx')
print("\n统计结果已保存到: 高频任务统计.xlsx")

# 显示TOP10任务类型
print("\n" + "=" * 100)
print("TOP10 高频任务类型")
print("=" * 100)
top10 = task_stats.head(10)
for idx, (category, row) in enumerate(top10.iterrows(), 1):
    print(f"\n{idx}. {category}")
    print(f"   任务数量: {int(row['任务数量'])} 条")
    print(f"   占比: {row['占比(%)']}%")
    print(f"   平均时长: {row['平均时长(分钟)']} 分钟")
    print(f"   中位数时长: {row['中位数时长(分钟)']} 分钟")
    print(f"   时长范围: {row['最短时长(分钟)']} - {row['最长时长(分钟)']} 分钟")

# 分年级统计
print("\n" + "=" * 100)
print("分年级任务分布")
print("=" * 100)

grade_task_dist = pd.crosstab(
    df_clean['学生年级'], 
    df_clean['任务分类'], 
    margins=True
)
grade_task_dist.to_excel('分年级任务分布.xlsx')
print("\n分年级任务分布已保存到: 分年级任务分布.xlsx")
print(grade_task_dist.to_string())

# 分地区统计
print("\n" + "=" * 100)
print("分地区任务分布")
print("=" * 100)

region_task_dist = pd.crosstab(
    df_clean['门店所属地区'], 
    df_clean['任务分类'], 
    margins=True
)
region_task_dist.to_excel('分地区任务分布.xlsx')
print("\n分地区任务分布已保存到: 分地区任务分布.xlsx")
print(region_task_dist.to_string())

# 提取每种任务类型的样本描述
print("\n" + "=" * 100)
print("各任务类型样本描述（每类显示10条）")
print("=" * 100)

sample_descriptions = {}
for category in task_stats.head(15).index:  # TOP15类型
    samples = df_clean[df_clean['任务分类'] == category]['学校作业任务描述'].value_counts().head(10)
    sample_descriptions[category] = samples
    
    print(f"\n【{category}】类任务样本（前10条高频描述）:")
    for desc, count in samples.items():
        print(f"  - {desc} ({count}次)")

# 保存详细样本
with pd.ExcelWriter('任务类型样本描述.xlsx', engine='openpyxl') as writer:
    for category, samples in sample_descriptions.items():
        df_samples = pd.DataFrame({
            '任务描述': samples.index,
            '出现次数': samples.values
        })
        # Excel的sheet名称有长度限制，截取前30个字符
        sheet_name = category[:30] if len(category) > 30 else category
        df_samples.to_excel(writer, sheet_name=sheet_name, index=False)

print("\n\n任务类型样本描述已保存到: 任务类型样本描述.xlsx")

# 分析"其他"类别的任务
print("\n" + "=" * 100)
print("未分类任务（其他类别）分析")
print("=" * 100)

other_tasks = df_clean[df_clean['任务分类'] == '其他']['学校作业任务描述'].value_counts().head(30)
print(f"\n未分类任务数量: {len(df_clean[df_clean['任务分类'] == '其他'])}")
print(f"\n未分类任务高频描述（前30条）:")
for desc, count in other_tasks.items():
    print(f"  - {desc} ({count}次)")

print("\n" + "=" * 100)
print("分析完成！")
print("=" * 100)
