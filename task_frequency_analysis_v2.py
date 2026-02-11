#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高频任务分类分析 V2 - 优化版
基于第一轮分析结果，优化分类规则
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

# 任务分类关键词定义（优化版）
# 按照优先级顺序匹配（更具体的放在前面）
task_categories = {
    # 核心高频任务
    '练字/字帖': [r'练字', r'写字', r'字帖', r'硬笔', r'软笔', r'书写练习', r'写字课堂'],
    '阅读': [r'^阅读', r'阅读打卡', r'读书', r'看书', r'课外阅读', r'整本书', r'阅读吧'],
    '朗读': [r'^朗读', r'朗诵'],
    '背诵': [r'背诵', r'背课文', r'背.*段落', r'必背', r'三字经背诵'],
    '复习': [r'^复习', r'单元复习', r'复习.*知识点'],
    '预习': [r'^预习', r'预习课文', r'预习.*课', r'预习.*单元', r'预习园地', r'预习习作'],
    '默写/听写': [r'默写', r'听写'],
    
    # 写作相关
    '作文': [r'^作文', r'抄正作文', r'订正作文', r'作文本'],
    '小练笔': [r'小练笔', r'练笔'],
    '写话': [r'写话', r'看图写话'],
    '日记': [r'日记', r'写日记', r'绘画日记'],
    '周记': [r'周记'],
    
    # 抄写相关
    '抄写': [r'抄写', r'抄.*词语', r'抄课文', r'抄.*生字', r'^抄词', r'抄.*词'],
    
    # 订正相关
    '订正': [r'订正', r'订卷'],
    
    # 基础学习
    '识字/生字': [r'识字', r'认字', r'生字', r'生字本', r'生字簿'],
    '拼音': [r'拼音'],
    
    # 练习
    '练习/习题': [r'^练习', r'练习单', r'练习纸', r'小练习', r'精准练', r'优化设计'],
    
    # 其他分类
    '口语交际': [r'口语交际'],
    '手抄报': [r'手抄报'],
    '观察记录': [r'观察日记', r'观察.*记录'],
    '课文改写': [r'改写', r'仿写', r'缩写'],
    '摘抄': [r'摘抄', r'摘录', r'好词好句'],
    '资料搜集': [r'搜集.*资料', r'收集.*资料', r'查找.*资料'],
    
    # 打卡
    '打卡任务': [r'^打卡', r'途途打卡'],
    
    # 提纲
    '提纲': [r'提纲'],
}

def classify_task(description):
    """
    根据任务描述分类任务类型
    返回匹配到的第一个类别
    """
    if pd.isna(description):
        return '未知'
    
    desc_str = str(description).strip()
    
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
print("高频任务统计分析 (优化版)")
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
task_stats.to_excel('高频任务统计_优化版.xlsx')
print("\n统计结果已保存到: 高频任务统计_优化版.xlsx")

# 显示所有任务类型（按数量排序）
print("\n" + "=" * 100)
print("所有任务类型详情（按频次排序）")
print("=" * 100)
for idx, (category, row) in enumerate(task_stats.iterrows(), 1):
    print(f"\n{idx}. {category}")
    print(f"   任务数量: {int(row['任务数量'])} 条")
    print(f"   占比: {row['占比(%)']}%")
    print(f"   平均时长: {row['平均时长(分钟)']} 分钟")
    print(f"   中位数时长: {row['中位数时长(分钟)']} 分钟")
    print(f"   时长范围: {row['最短时长(分钟)']} - {row['最长时长(分钟)']} 分钟")

# 识别高频且耗时较长的任务
print("\n" + "=" * 100)
print("重点关注：高频且耗时较长的任务类型")
print("=" * 100)
print("\n筛选条件：任务数量>=500 且 平均时长>=20分钟\n")

high_freq_long_time = task_stats[
    (task_stats['任务数量'] >= 500) & 
    (task_stats['平均时长(分钟)'] >= 20)
].sort_values('任务数量', ascending=False)

for idx, (category, row) in enumerate(high_freq_long_time.iterrows(), 1):
    print(f"{idx}. {category}")
    print(f"   任务数量: {int(row['任务数量'])} 条 | 占比: {row['占比(%)']}%")
    print(f"   平均时长: {row['平均时长(分钟)']} 分钟 | 中位数: {row['中位数时长(分钟)']} 分钟")
    print()

# 分年级统计（优化版）
print("\n" + "=" * 100)
print("分年级任务分布（优化版）")
print("=" * 100)

grade_task_dist = pd.crosstab(
    df_clean['学生年级'], 
    df_clean['任务分类']
)

# 只显示任务数量>100的类别
important_categories = task_stats[task_stats['任务数量'] > 100].index.tolist()
grade_task_dist_filtered = grade_task_dist[important_categories]
grade_task_dist_filtered['总计'] = grade_task_dist_filtered.sum(axis=1)

grade_task_dist_filtered.to_excel('分年级任务分布_优化版.xlsx')
print("\n分年级任务分布已保存到: 分年级任务分布_优化版.xlsx")
print(grade_task_dist_filtered.to_string())

# 提取每种任务类型的样本描述（TOP10类型）
print("\n" + "=" * 100)
print("各任务类型样本描述（TOP10类型，每类显示15条）")
print("=" * 100)

sample_descriptions = {}
for category in task_stats.head(10).index:  # TOP10类型
    samples = df_clean[df_clean['任务分类'] == category]['学校作业任务描述'].value_counts().head(15)
    sample_descriptions[category] = samples
    
    print(f"\n【{category}】类任务样本（前15条高频描述）:")
    for desc, count in samples.items():
        print(f"  - {desc} ({count}次)")

# 保存详细样本
with pd.ExcelWriter('任务类型样本描述_优化版.xlsx', engine='openpyxl') as writer:
    for category in task_stats.index:
        samples = df_clean[df_clean['任务分类'] == category]['学校作业任务描述'].value_counts().head(50)
        df_samples = pd.DataFrame({
            '任务描述': samples.index,
            '出现次数': samples.values
        })
        # Excel的sheet名称有长度限制，且不能包含特殊字符
        sheet_name = category[:30] if len(category) > 30 else category
        # 替换非法字符
        sheet_name = sheet_name.replace('/', '-').replace('\\', '-').replace('*', '').replace('?', '').replace('[', '').replace(']', '').replace(':', '-')
        df_samples.to_excel(writer, sheet_name=sheet_name, index=False)

print("\n\n任务类型样本描述已保存到: 任务类型样本描述_优化版.xlsx")

# 分析"其他"类别的任务（更详细）
print("\n" + "=" * 100)
print("未分类任务（其他类别）详细分析")
print("=" * 100)

other_tasks = df_clean[df_clean['任务分类'] == '其他']
print(f"\n未分类任务数量: {len(other_tasks)} ({len(other_tasks)/len(df_clean)*100:.2f}%)")

other_tasks_freq = other_tasks['学校作业任务描述'].value_counts().head(50)
print(f"\n未分类任务高频描述（前50条）:")
for desc, count in other_tasks_freq.items():
    print(f"  - {desc} ({count}次)")

# 保存未分类任务详情
other_tasks_detail = other_tasks[['学校作业任务描述', '预计完成时间', '学生年级', '门店所属地区']].copy()
other_tasks_detail.to_excel('未分类任务详情.xlsx', index=False)
print("\n未分类任务详情已保存到: 未分类任务详情.xlsx")

print("\n" + "=" * 100)
print("分析完成！")
print("=" * 100)
