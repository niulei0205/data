#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成高频任务分析报告和可视化图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from datetime import datetime

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 尝试设置更好的中文支持
try:
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'DejaVu Sans']
except:
    pass

# 读取统计数据
task_stats = pd.read_excel('高频任务统计_优化版.xlsx', index_col=0)
grade_dist = pd.read_excel('分年级任务分布_优化版.xlsx', index_col=0)

print("正在生成可视化图表...")

# 创建图表
fig = plt.figure(figsize=(20, 12))

# 1. 任务数量TOP15柱状图
ax1 = plt.subplot(2, 3, 1)
top15 = task_stats.head(15).sort_values('任务数量')
colors = plt.cm.viridis(range(len(top15)))
top15['任务数量'].plot(kind='barh', ax=ax1, color=colors)
ax1.set_xlabel('Task Count', fontsize=10)
ax1.set_title('TOP15 Task Types by Frequency', fontsize=12, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)

# 在柱状图上添加数值
for i, v in enumerate(top15['任务数量']):
    ax1.text(v, i, f' {int(v)}', va='center', fontsize=8)

# 2. 任务占比饼图（TOP10）
ax2 = plt.subplot(2, 3, 2)
top10_pie = task_stats.head(10)
colors_pie = plt.cm.Set3(range(len(top10_pie)))
wedges, texts, autotexts = ax2.pie(
    top10_pie['任务数量'], 
    labels=top10_pie.index,
    autopct='%1.1f%%',
    colors=colors_pie,
    startangle=90
)
ax2.set_title('TOP10 Task Distribution', fontsize=12, fontweight='bold')
# 调整文字大小
for text in texts:
    text.set_fontsize(8)
for autotext in autotexts:
    autotext.set_fontsize(7)
    autotext.set_color('white')
    autotext.set_weight('bold')

# 3. 平均时长对比（TOP15）
ax3 = plt.subplot(2, 3, 3)
top15_time = task_stats.head(15).sort_values('平均时长(分钟)')
colors_time = ['#ff6b6b' if x >= 24 else '#4ecdc4' for x in top15_time['平均时长(分钟)']]
top15_time['平均时长(分钟)'].plot(kind='barh', ax=ax3, color=colors_time)
ax3.set_xlabel('Average Time (minutes)', fontsize=10)
ax3.set_title('TOP15 Tasks by Average Duration', fontsize=12, fontweight='bold')
ax3.axvline(x=22, color='red', linestyle='--', alpha=0.5, label='Overall Avg')
ax3.legend()
ax3.grid(axis='x', alpha=0.3)

# 在柱状图上添加数值
for i, v in enumerate(top15_time['平均时长(分钟)']):
    ax3.text(v, i, f' {v:.1f}', va='center', fontsize=8)

# 4. 任务数量与平均时长散点图
ax4 = plt.subplot(2, 3, 4)
# 只显示任务数量>100的
significant_tasks = task_stats[task_stats['任务数量'] > 100].copy()
scatter = ax4.scatter(
    significant_tasks['任务数量'], 
    significant_tasks['平均时长(分钟)'],
    s=significant_tasks['任务数量']/5,  # 气泡大小
    alpha=0.6,
    c=range(len(significant_tasks)),
    cmap='viridis'
)

# 标注任务类型
for idx, row in significant_tasks.iterrows():
    if row['任务数量'] > 1000 or row['平均时长(分钟)'] > 26:
        ax4.annotate(
            idx, 
            (row['任务数量'], row['平均时长(分钟)']),
            fontsize=7,
            alpha=0.7
        )

ax4.set_xlabel('Task Count', fontsize=10)
ax4.set_ylabel('Average Time (minutes)', fontsize=10)
ax4.set_title('Task Frequency vs Duration (tasks>100)', fontsize=12, fontweight='bold')
ax4.grid(alpha=0.3)

# 添加参考线
ax4.axhline(y=24, color='red', linestyle='--', alpha=0.3, label='High Duration (24min)')
ax4.axvline(x=1000, color='blue', linestyle='--', alpha=0.3, label='High Frequency (1000)')
ax4.legend(fontsize=8)

# 5. 分年级任务分布热力图（TOP10任务类型）
ax5 = plt.subplot(2, 3, 5)
top10_categories = task_stats.head(10).index.tolist()
# 过滤出存在的列
existing_categories = [cat for cat in top10_categories if cat in grade_dist.columns]
heatmap_data = grade_dist[existing_categories].T

sns.heatmap(
    heatmap_data, 
    annot=True, 
    fmt='d', 
    cmap='YlOrRd',
    ax=ax5,
    cbar_kws={'label': 'Task Count'},
    annot_kws={'fontsize': 7}
)
ax5.set_title('Task Distribution by Grade (TOP10)', fontsize=12, fontweight='bold')
ax5.set_xlabel('Grade', fontsize=10)
ax5.set_ylabel('Task Type', fontsize=10)

# 6. 高频且耗时任务（重点关注）
ax6 = plt.subplot(2, 3, 6)
# 筛选：任务数量>=500 且 平均时长>=20分钟
high_priority = task_stats[
    (task_stats['任务数量'] >= 500) & 
    (task_stats['平均时长(分钟)'] >= 20)
].copy()

# 计算总耗时 = 任务数量 × 平均时长
high_priority['总耗时'] = high_priority['任务数量'] * high_priority['平均时长(分钟)']
high_priority = high_priority.sort_values('总耗时', ascending=True).tail(12)

colors_priority = plt.cm.Reds(range(len(high_priority)))
high_priority['总耗时'].plot(kind='barh', ax=ax6, color=colors_priority)
ax6.set_xlabel('Total Time (minutes)', fontsize=10)
ax6.set_title('High-Priority Tasks (Freq>=500 & Time>=20min)', fontsize=12, fontweight='bold')
ax6.grid(axis='x', alpha=0.3)

# 在柱状图上添加数值
for i, v in enumerate(high_priority['总耗时']):
    ax6.text(v, i, f' {int(v)}', va='center', fontsize=7)

plt.tight_layout()
plt.savefig('高频任务分析图表.png', dpi=300, bbox_inches='tight')
print("图表已保存: 高频任务分析图表.png")
plt.close()

# 生成文字报告
print("\n正在生成分析报告...")

report = []
report.append("=" * 100)
report.append("语文学科'其他'类型任务高频分析报告")
report.append("=" * 100)
report.append(f"\n报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"\n数据范围: 2025年9月-2026年1月（25年秋季学期）")
report.append(f"数据说明: 学校作业 + 任务类型为'其他' + 学科为'语文'")
report.append(f"数据总量: {task_stats['任务数量'].sum()} 条任务记录（已剔除年级未知数据）")

# 一、整体概览
report.append("\n\n" + "=" * 100)
report.append("一、整体数据概览")
report.append("=" * 100)
report.append(f"\n识别出的任务分类总数: {len(task_stats)} 种")
report.append(f"平均任务时长: {task_stats['平均时长(分钟)'].mean():.2f} 分钟")
report.append(f"任务时长中位数: {task_stats['中位数时长(分钟)'].median():.2f} 分钟")

# 二、TOP15高频任务
report.append("\n\n" + "=" * 100)
report.append("二、TOP15 高频任务类型")
report.append("=" * 100)
report.append("\n排名  任务类型        数量    占比     平均时长  中位数时长")
report.append("-" * 100)

for idx, (category, row) in enumerate(task_stats.head(15).iterrows(), 1):
    report.append(
        f"{idx:2d}.  {category:12s}  {int(row['任务数量']):5d}   {row['占比(%)']:5.2f}%   "
        f"{row['平均时长(分钟)']:5.1f}分钟   {row['中位数时长(分钟)']:5.1f}分钟"
    )

# 三、高频且耗时较长的任务（重点关注）
report.append("\n\n" + "=" * 100)
report.append("三、高频且耗时较长的任务（重点关注）")
report.append("=" * 100)
report.append("\n筛选条件: 任务数量 >= 500 且 平均时长 >= 20分钟")
report.append("\n这些任务具有【高频次】+【耗时长】的特点，是AI提效的重点目标")
report.append("\n排名  任务类型        数量    占比     平均时长  总耗时(小时)")
report.append("-" * 100)

high_freq_long_time = task_stats[
    (task_stats['任务数量'] >= 500) & 
    (task_stats['平均时长(分钟)'] >= 20)
].copy()
high_freq_long_time['总耗时(小时)'] = (high_freq_long_time['任务数量'] * high_freq_long_time['平均时长(分钟)']) / 60
high_freq_long_time = high_freq_long_time.sort_values('总耗时(小时)', ascending=False)

for idx, (category, row) in enumerate(high_freq_long_time.iterrows(), 1):
    report.append(
        f"{idx:2d}.  {category:12s}  {int(row['任务数量']):5d}   {row['占比(%)']:5.2f}%   "
        f"{row['平均时长(分钟)']:5.1f}分钟   {row['总耗时(小时)']:8.1f}小时"
    )

# 四、分年级分析
report.append("\n\n" + "=" * 100)
report.append("四、分年级任务分布特征")
report.append("=" * 100)

# 各年级TOP5任务
for grade in ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级']:
    if grade in grade_dist.index:
        grade_data = grade_dist.loc[grade].sort_values(ascending=False).head(5)
        report.append(f"\n{grade} TOP5任务:")
        for task_type, count in grade_data.items():
            if count > 0:
                report.append(f"  - {task_type}: {int(count)}次")

# 五、分析结论和建议
report.append("\n\n" + "=" * 100)
report.append("五、分析结论")
report.append("=" * 100)

report.append("\n【核心发现】")
report.append("\n1. 高频任务TOP3:")
top3 = task_stats.head(3)
for idx, (category, row) in enumerate(top3.iterrows(), 1):
    report.append(f"   {idx}. {category}: {int(row['任务数量'])}次 ({row['占比(%)']:.2f}%), 平均{row['平均时长(分钟)']:.1f}分钟")

report.append("\n2. 最耗时任务TOP3 (按总耗时计算):")
time_consuming = task_stats.copy()
time_consuming['总耗时'] = time_consuming['任务数量'] * time_consuming['平均时长(分钟)']
top3_time = time_consuming.sort_values('总耗时', ascending=False).head(3)
for idx, (category, row) in enumerate(top3_time.iterrows(), 1):
    total_hours = row['总耗时'] / 60
    report.append(f"   {idx}. {category}: 总计{total_hours:.1f}小时 ({int(row['任务数量'])}次 × {row['平均时长(分钟)']:.1f}分钟)")

report.append("\n3. 未分类任务占比: {:.2f}%".format(
    task_stats.loc['其他', '占比(%)'] if '其他' in task_stats.index else 0
))
report.append("   说明: 仍有部分任务描述较为模糊或特殊，需要进一步细化分类")

report.append("\n\n【年级特征】")
report.append("- 低年级(1-2年级): 以拼音、识字/生字、练字为主")
report.append("- 中年级(3-4年级): 订正、默写/听写、阅读任务增加")
report.append("- 高年级(5-6年级): 复习、作文、小练笔比重提升")

# 保存报告
report_text = '\n'.join(report)
with open('高频任务分析报告.txt', 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n报告已保存: 高频任务分析报告.txt")
print("\n" + report_text)

# 生成Excel汇总表
print("\n\n正在生成Excel汇总表...")
with pd.ExcelWriter('高频任务分析汇总.xlsx', engine='openpyxl') as writer:
    # 1. 总体统计
    task_stats.to_excel(writer, sheet_name='任务统计总表')
    
    # 2. 高频且耗时任务
    high_freq_long_time.to_excel(writer, sheet_name='高频耗时任务')
    
    # 3. 分年级分布
    grade_dist.to_excel(writer, sheet_name='分年级分布')
    
    # 4. TOP10任务详情
    top10_detail = task_stats.head(10).copy()
    top10_detail.to_excel(writer, sheet_name='TOP10任务详情')

print("Excel汇总表已保存: 高频任务分析汇总.xlsx")

print("\n" + "=" * 100)
print("所有分析文件生成完成！")
print("=" * 100)
print("\n生成的文件列表:")
print("1. 高频任务分析图表.png - 可视化图表")
print("2. 高频任务分析报告.txt - 文字报告")
print("3. 高频任务分析汇总.xlsx - Excel汇总表")
print("4. 高频任务统计_优化版.xlsx - 详细统计数据")
print("5. 任务类型样本描述_优化版.xlsx - 各类任务样本")
print("6. 分年级任务分布_优化版.xlsx - 分年级数据")
print("7. 未分类任务详情.xlsx - 未分类任务明细")
