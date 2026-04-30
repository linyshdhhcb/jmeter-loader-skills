#!/usr/bin/env python3
"""
JTL 结果解析脚本 - 解析 JMeter 结果文件并生成性能报告

功能:
1. 支持 CSV 和 XML 格式的 JTL 文件
2. 计算核心性能指标（Avg, TP90, TP95, TP99, 错误率, 吞吐量）
3. 生成多维度分析报告
4. 支持 JSON, HTML, CSV 多种输出格式
5. 可选的图表生成

用法:
    python parse_jtl.py --jtl result.jtl --output report.json --format json
"""

import argparse
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from statistics import mean, median


class JTLParser:
    """JTL 文件解析器类"""

    CSV_FIELDS = [
        'timeStamp', 'elapsed', 'label', 'responseCode', 'responseMessage',
        'threadName', 'dataType', 'success', 'failureMessage', 'bytes',
        'sentBytes', 'grpThreads', 'allThreads', 'URL', 'Latency', 'IdleTime', 'Connect'
    ]

    def __init__(self):
        """初始化解析器"""
        self.samples = []
        self.by_label = defaultdict(list)
        self.time_series = []

    def _parse_csv(self, jtl_path: str) -> List[Dict]:
        """
        解析 CSV 格式的 JTL 文件

        Args:
            jtl_path: JTL 文件路径

        Returns:
            样本列表
        """
        samples = []

        with open(jtl_path, 'r', encoding='utf-8-sig', newline='') as f:
            first_line = f.readline().strip()

            if first_line.startswith('<?xml') or first_line.startswith('<testResults'):
                return self._parse_xml(jtl_path)

            f.seek(0)

            dialect = csv.Sniffer().sniff(first_line) if first_line else csv.excel
            f.seek(0)

            reader = csv.DictReader(f, dialect=dialect)

            for row_num, row in enumerate(reader, 2):
                try:
                    sample = self._normalize_sample(row)
                    samples.append(sample)
                except Exception as e:
                    print(f"警告: 第 {row_num} 行解析失败: {e}")
                    continue

        return samples

    def _parse_xml(self, jtl_path: str) -> List[Dict]:
        """
        解析 XML 格式的 JTL 文件

        Args:
            jtl_path: JTL 文件路径

        Returns:
            样本列表
        """
        samples = []
        tree = ET.parse(jtl_path)
        root = tree.getroot()

        if root.tag != 'testResults':
            raise ValueError(f"无效的 XML JTL 文件，根元素应为 'testResults'，实际为 '{root.tag}'")

        for sample_elem in root.findall('.//httpSample') + root.findall('.//sample'):
            try:
                sample = {
                    'timeStamp': int(sample_elem.get('t', 0)),
                    'elapsed': int(sample_elem.get('t', 0)),
                    'label': sample_elem.get('lb', ''),
                    'responseCode': sample_elem.get('rc', ''),
                    'responseMessage': sample_elem.get('rm', ''),
                    'threadName': sample_elem.get('tn', ''),
                    'success': sample_elem.get('s', 'true').lower() == 'true',
                    'bytes': int(sample_elem.get('by', 0)),
                    'sentBytes': int(sample_elem.get('sby', 0)),
                    'grpThreads': int(sample_elem.get('ng', 0)),
                    'allThreads': int(sample_elem.get('na', 0)),
                    'Latency': int(sample_elem.get('lt', 0)),
                    'Connect': int(sample_elem.get('ct', 0)),
                }
                samples.append(sample)
            except Exception as e:
                print(f"警告: 解析 sample 元素失败: {e}")
                continue

        return samples

    def _normalize_sample(self, row: Dict) -> Dict:
        """
        标准化样本数据

        Args:
            row: 原始行数据

        Returns:
            标准化的样本数据
        """
        return {
            'timeStamp': self._to_int(row.get('timeStamp', row.get('ts', 0))),
            'elapsed': self._to_int(row.get('elapsed', row.get('t', 0))),
            'label': str(row.get('label', row.get('lb', ''))),
            'responseCode': str(row.get('responseCode', row.get('rc', ''))),
            'responseMessage': str(row.get('responseMessage', row.get('rm', ''))),
            'threadName': str(row.get('threadName', row.get('tn', ''))),
            'dataType': str(row.get('dataType', row.get('dt', ''))),
            'success': self._parse_boolean(row.get('success', row.get('s', 'true'))),
            'failureMessage': str(row.get('failureMessage', '')),
            'bytes': self._to_int(row.get('bytes', row.get('by', 0))),
            'sentBytes': self._to_int(row.get('sentBytes', row.get('sby', 0))),
            'grpThreads': self._to_int(row.get('grpThreads', row.get('ng', 0))),
            'allThreads': self._to_int(row.get('allThreads', row.get('na', 0))),
            'URL': str(row.get('URL', '')),
            'Latency': self._to_int(row.get('Latency', row.get('lt', 0))),
            'IdleTime': self._to_int(row.get('IdleTime', row.get('it', 0))),
            'Connect': self._to_int(row.get('Connect', row.get('ct', 0))),
        }

    def _to_int(self, value) -> int:
        """安全转换为整数"""
        if value is None or value == '':
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    def _parse_boolean(self, value) -> bool:
        """解析布尔值"""
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes')

    def parse(self, jtl_path: str) -> bool:
        """
        解析 JTL 文件

        Args:
            jtl_path: JTL 文件路径

        Returns:
            是否成功
        """
        if not os.path.exists(jtl_path):
            raise FileNotFoundError(f"JTL 文件不存在: {jtl_path}")

        if not os.path.isfile(jtl_path):
            raise ValueError(f"路径不是文件: {jtl_path}")

        with open(jtl_path, 'r', encoding='utf-8-sig') as f:
            first_char = f.read(1)

        if first_char == '<':
            self.samples = self._parse_xml(jtl_path)
        else:
            self.samples = self._parse_csv(jtl_path)

        if not self.samples:
            print("警告: 未找到任何样本数据")
            return False

        for sample in self.samples:
            self.by_label[sample['label']].append(sample)

        self._build_time_series()

        return True

    def _build_time_series(self, interval_seconds: int = 10):
        """
        构建时间序列数据

        Args:
            interval_seconds: 时间间隔（秒）
        """
        if not self.samples:
            return

        sorted_samples = sorted(self.samples, key=lambda x: x['timeStamp'])
        start_time = sorted_samples[0]['timeStamp']
        end_time = sorted_samples[-1]['timeStamp']

        interval_ms = interval_seconds * 1000
        buckets = defaultdict(lambda: {
            'count': 0,
            'elapsed_sum': 0,
            'errors': 0,
            'bytes_sum': 0,
            'timestamp': 0
        })

        for sample in sorted_samples:
            bucket_time = (sample['timeStamp'] // interval_ms) * interval_ms
            bucket = buckets[bucket_time]
            bucket['count'] += 1
            bucket['elapsed_sum'] += sample['elapsed']
            bucket['bytes_sum'] += sample['bytes']
            if not sample['success']:
                bucket['errors'] += 1
            bucket['timestamp'] = bucket_time

        self.time_series = [
            {
                'timestamp': ts,
                'time_iso': self._ms_to_iso(ts),
                'count': bucket['count'],
                'throughput': bucket['count'] / interval_seconds,
                'avg_response_time': bucket['elapsed_sum'] / bucket['count'] if bucket['count'] > 0 else 0,
                'error_rate': bucket['errors'] / bucket['count'] if bucket['count'] > 0 else 0,
                'bytes_per_sec': bucket['bytes_sum'] / interval_seconds
            }
            for ts, bucket in sorted(buckets.items())
        ]

    def _ms_to_iso(self, ms: int) -> str:
        """毫秒时间戳转 ISO 格式"""
        dt = datetime.fromtimestamp(ms / 1000)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        计算整体性能指标

        Returns:
            指标字典
        """
        if not self.samples:
            return {}

        elapsed_times = [s['elapsed'] for s in self.samples]
        success_samples = [s for s in self.samples if s['success']]
        error_samples = [s for s in self.samples if not s['success']]

        start_time = min(s['timeStamp'] for s in self.samples)
        end_time = max(s['timeStamp'] for s in self.samples)
        duration_sec = (end_time - start_time) / 1000 if start_time != end_time else 1

        total_bytes = sum(s['bytes'] for s in self.samples)
        total_sent_bytes = sum(s['sentBytes'] for s in self.samples)

        sorted_elapsed = sorted(elapsed_times)
        n = len(sorted_elapsed)

        metrics = {
            'summary': {
                'total_samples': len(self.samples),
                'success_samples': len(success_samples),
                'error_samples': len(error_samples),
                'error_rate': len(error_samples) / len(self.samples) * 100 if self.samples else 0,
                'start_time': self._ms_to_iso(start_time),
                'end_time': self._ms_to_iso(end_time),
                'duration_seconds': round(duration_sec, 2),
                'total_labels': len(self.by_label),
            },
            'response_time': {
                'min': min(elapsed_times) if elapsed_times else 0,
                'max': max(elapsed_times) if elapsed_times else 0,
                'average': round(mean(elapsed_times), 2) if elapsed_times else 0,
                'median': round(median(elapsed_times), 2) if elapsed_times else 0,
                'tp90': self._percentile(sorted_elapsed, 90),
                'tp95': self._percentile(sorted_elapsed, 95),
                'tp99': self._percentile(sorted_elapsed, 99),
            },
            'throughput': {
                'total_requests_per_sec': round(len(self.samples) / duration_sec, 2),
                'success_requests_per_sec': round(len(success_samples) / duration_sec, 2) if duration_sec > 0 else 0,
                'received_kb_per_sec': round(total_bytes / 1024 / duration_sec, 2) if duration_sec > 0 else 0,
                'sent_kb_per_sec': round(total_sent_bytes / 1024 / duration_sec, 2) if duration_sec > 0 else 0,
            },
            'by_label': {},
            'time_series': self.time_series,
        }

        for label, samples in self.by_label.items():
            label_elapsed = [s['elapsed'] for s in samples]
            label_sorted = sorted(label_elapsed)
            label_success = [s for s in samples if s['success']]
            label_errors = [s for s in samples if not s['success']]

            metrics['by_label'][label] = {
                'count': len(samples),
                'success_count': len(label_success),
                'error_count': len(label_errors),
                'error_rate': len(label_errors) / len(samples) * 100 if samples else 0,
                'response_time': {
                    'min': min(label_elapsed) if label_elapsed else 0,
                    'max': max(label_elapsed) if label_elapsed else 0,
                    'average': round(mean(label_elapsed), 2) if label_elapsed else 0,
                    'tp90': self._percentile(label_sorted, 90),
                    'tp95': self._percentile(label_sorted, 95),
                    'tp99': self._percentile(label_sorted, 99),
                }
            }

        return metrics

    def _percentile(self, sorted_list: List, p: int) -> float:
        """
        计算百分位数

        Args:
            sorted_list: 已排序的列表
            p: 百分位数（0-100）

        Returns:
            百分位数值
        """
        if not sorted_list:
            return 0

        n = len(sorted_list)
        if n == 1:
            return float(sorted_list[0])

        index = (n - 1) * p / 100
        floor = int(index)
        ceil = min(floor + 1, n - 1)

        if floor == ceil:
            return float(sorted_list[floor])

        fraction = index - floor
        result = sorted_list[floor] + (sorted_list[ceil] - sorted_list[floor]) * fraction
        return round(result, 2)

    def generate_optimization_suggestions(self, metrics: Dict) -> List[Dict]:
        """
        生成优化建议

        Args:
            metrics: 性能指标

        Returns:
            建议列表
        """
        suggestions = []

        summary = metrics.get('summary', {})
        rt = metrics.get('response_time', {})
        tp = metrics.get('throughput', {})

        error_rate = summary.get('error_rate', 0)
        if error_rate > 5:
            suggestions.append({
                'category': '错误率',
                'severity': '高',
                'issue': f'错误率过高: {error_rate:.2f}%',
                'suggestions': [
                    '检查服务端日志定位错误原因',
                    '验证测试数据的正确性',
                    '确认服务容量是否足够',
                    '检查网络连接稳定性'
                ]
            })
        elif error_rate > 1:
            suggestions.append({
                'category': '错误率',
                'severity': '中',
                'issue': f'存在少量错误: {error_rate:.2f}%',
                'suggestions': [
                    '关注错误类型和发生时机',
                    '排查是否为偶发问题'
                ]
            })

        avg_rt = rt.get('average', 0)
        tp90 = rt.get('tp90', 0)

        if tp90 > 2000:
            suggestions.append({
                'category': '响应时间',
                'severity': '高',
                'issue': f'TP90 响应时间过高: {tp90} ms',
                'suggestions': [
                    '分析慢查询日志',
                    '检查数据库索引是否合理',
                    '考虑引入缓存层',
                    '优化关键路径代码'
                ]
            })
        elif tp90 > 1000:
            suggestions.append({
                'category': '响应时间',
                'severity': '中',
                'issue': f'TP90 响应时间偏高: {tp90} ms',
                'suggestions': [
                    '监控服务端资源使用率',
                    '检查是否存在性能瓶颈'
                ]
            })

        if avg_rt > 500:
            suggestions.append({
                'category': '响应时间',
                'severity': '中',
                'issue': f'平均响应时间偏高: {avg_rt:.2f} ms',
                'suggestions': [
                    '排查是否存在资源竞争',
                    '考虑使用连接池优化'
                ]
            })

        by_label = metrics.get('by_label', {})
        for label, label_metrics in by_label.items():
            label_error_rate = label_metrics.get('error_rate', 0)
            label_tp90 = label_metrics.get('response_time', {}).get('tp90', 0)

            if label_error_rate > 10:
                suggestions.append({
                    'category': '接口异常',
                    'severity': '高',
                    'issue': f'接口 "{label}" 错误率过高: {label_error_rate:.2f}%',
                    'suggestions': [
                        '重点排查该接口的实现逻辑',
                        '检查该接口依赖的下游服务',
                        '验证该接口的测试参数'
                    ]
                })

            if label_tp90 > 3000:
                suggestions.append({
                    'category': '接口性能',
                    'severity': '高',
                    'issue': f'接口 "{label}" TP90 过慢: {label_tp90} ms',
                    'suggestions': [
                        '对该接口进行专项性能分析',
                        '检查数据库查询性能',
                        '考虑异步处理非核心逻辑'
                    ]
                })

        if not suggestions:
            suggestions.append({
                'category': '总体评估',
                'severity': '低',
                'issue': '性能指标良好',
                'suggestions': [
                    '继续保持当前配置',
                    '可考虑增加并发量进一步探底',
                    '定期回归测试确保性能稳定'
                ]
            })

        return suggestions

    def generate_report(
        self,
        output_path: str,
        format: str = 'json',
        include_charts: bool = False
    ) -> bool:
        """
        生成报告文件

        Args:
            output_path: 输出文件路径
            format: 输出格式（json, html, csv）
            include_charts: 是否包含图表

        Returns:
            是否成功
        """
        metrics = self.calculate_metrics()
        suggestions = self.generate_optimization_suggestions(metrics)

        report = {
            'generated_at': datetime.now().isoformat(),
            'metrics': metrics,
            'suggestions': suggestions
        }

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return True

        elif format.lower() == 'csv':
            self._generate_csv_report(report, output_path)
            return True

        elif format.lower() == 'html':
            self._generate_html_report(report, output_path, include_charts)
            return True

        else:
            raise ValueError(f"不支持的输出格式: {format}")

    def _generate_csv_report(self, report: Dict, output_path: str):
        """生成 CSV 格式报告"""
        metrics = report['metrics']
        summary = metrics.get('summary', {})
        rt = metrics.get('response_time', {})
        tp = metrics.get('throughput', {})

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)

            writer.writerow(['指标类别', '指标名称', '值'])
            writer.writerow([])

            writer.writerow(['总体', '总请求数', summary.get('total_samples', 0)])
            writer.writerow(['总体', '成功请求数', summary.get('success_samples', 0)])
            writer.writerow(['总体', '错误请求数', summary.get('error_samples', 0)])
            writer.writerow(['总体', '错误率(%)', f"{summary.get('error_rate', 0):.2f}"])
            writer.writerow(['总体', '测试时长(秒)', summary.get('duration_seconds', 0)])
            writer.writerow([])

            writer.writerow(['响应时间', '最小值(ms)', rt.get('min', 0)])
            writer.writerow(['响应时间', '最大值(ms)', rt.get('max', 0)])
            writer.writerow(['响应时间', '平均值(ms)', rt.get('average', 0)])
            writer.writerow(['响应时间', '中位数(ms)', rt.get('median', 0)])
            writer.writerow(['响应时间', 'TP90(ms)', rt.get('tp90', 0)])
            writer.writerow(['响应时间', 'TP95(ms)', rt.get('tp95', 0)])
            writer.writerow(['响应时间', 'TP99(ms)', rt.get('tp99', 0)])
            writer.writerow([])

            writer.writerow(['吞吐量', '总请求/秒', tp.get('total_requests_per_sec', 0)])
            writer.writerow(['吞吐量', '成功请求/秒', tp.get('success_requests_per_sec', 0)])
            writer.writerow(['吞吐量', '接收 KB/秒', tp.get('received_kb_per_sec', 0)])
            writer.writerow(['吞吐量', '发送 KB/秒', tp.get('sent_kb_per_sec', 0)])

    def _generate_html_report(self, report: Dict, output_path: str, include_charts: bool):
        """生成 HTML 格式报告"""
        metrics = report['metrics']
        summary = metrics.get('summary', {})
        rt = metrics.get('response_time', {})
        tp = metrics.get('throughput', {})
        by_label = metrics.get('by_label', {})
        suggestions = report.get('suggestions', [])

        def get_status_color(value, thresholds):
            if value >= thresholds[2]:
                return 'danger'
            elif value >= thresholds[1]:
                return 'warning'
            else:
                return 'success'

        error_status = get_status_color(summary.get('error_rate', 0), [1, 5, 10])
        tp90_status = get_status_color(rt.get('tp90', 0), [500, 1000, 2000])

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JMeter 性能测试报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f7fa; padding: 20px; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; overflow: hidden; }}
        .card-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }}
        .card-header h1 {{ font-size: 24px; font-weight: 600; }}
        .card-header p {{ opacity: 0.9; margin-top: 8px; font-size: 14px; }}
        .card-body {{ padding: 20px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric {{ background: #f8f9fa; border-radius: 8px; padding: 15px; border-left: 4px solid #667eea; }}
        .metric.danger {{ border-left-color: #ef4444; background: #fef2f2; }}
        .metric.warning {{ border-left-color: #f59e0b; background: #fffbeb; }}
        .metric.success {{ border-left-color: #10b981; background: #ecfdf5; }}
        .metric-label {{ font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 28px; font-weight: 700; margin-top: 5px; color: #1f2937; }}
        .metric-unit {{ font-size: 12px; color: #6b7280; font-weight: normal; }}
        h2 {{ font-size: 18px; margin-bottom: 15px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; color: #374151; }}
        tr:hover {{ background: #f9fafb; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        .badge-success {{ background: #d1fae5; color: #065f46; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        .suggestion {{ margin-bottom: 15px; padding: 15px; border-radius: 8px; border-left: 4px solid; }}
        .suggestion.danger {{ border-color: #ef4444; background: #fef2f2; }}
        .suggestion.warning {{ border-color: #f59e0b; background: #fffbeb; }}
        .suggestion.success {{ border-color: #10b981; background: #ecfdf5; }}
        .suggestion-title {{ font-weight: 600; margin-bottom: 8px; }}
        .suggestion-list {{ margin-left: 20px; color: #4b5563; }}
        .suggestion-list li {{ margin: 4px 0; }}
        .summary-box {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .summary-item {{ flex: 1; min-width: 150px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h1>🚀 JMeter 性能测试报告</h1>
                <p>生成时间: {report['generated_at']}</p>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <h2>📊 执行概览</h2>
                <div class="summary-box">
                    <div class="summary-item">
                        <div class="metric-label">总请求数</div>
                        <div class="metric-value">{summary.get('total_samples', 0)}</div>
                    </div>
                    <div class="summary-item">
                        <div class="metric-label">错误率</div>
                        <div class="metric-value">{summary.get('error_rate', 0):.2f}<span class="metric-unit">%</span></div>
                    </div>
                    <div class="summary-item">
                        <div class="metric-label">测试时长</div>
                        <div class="metric-value">{summary.get('duration_seconds', 0)}<span class="metric-unit">秒</span></div>
                    </div>
                    <div class="summary-item">
                        <div class="metric-label">接口数量</div>
                        <div class="metric-value">{len(by_label)}<span class="metric-unit">个</span></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <h2>⏱️ 响应时间指标</h2>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-label">最小值</div>
                        <div class="metric-value">{rt.get('min', 0)}<span class="metric-unit">ms</span></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">最大值</div>
                        <div class="metric-value">{rt.get('max', 0)}<span class="metric-unit">ms</span></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">平均值</div>
                        <div class="metric-value">{rt.get('average', 0)}<span class="metric-unit">ms</span></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">中位数</div>
                        <div class="metric-value">{rt.get('median', 0)}<span class="metric-unit">ms</span></div>
                    </div>
                    <div class="metric {tp90_status}">
                        <div class="metric-label">TP90</div>
                        <div class="metric-value">{rt.get('tp90', 0)}<span class="metric-unit">ms</span></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">TP95</div>
                        <div class="metric-value">{rt.get('tp95', 0)}<span class="metric-unit">ms</span></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">TP99</div>
                        <div class="metric-value">{rt.get('tp99', 0)}<span class="metric-unit">ms</span></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <h2>📈 吞吐量指标</h2>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-label">总吞吐量</div>
                        <div class="metric-value">{tp.get('total_requests_per_sec', 0)}<span class="metric-unit">req/s</span></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">成功吞吐量</div>
                        <div class="metric-value">{tp.get('success_requests_per_sec', 0)}<span class="metric-unit">req/s</span></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">接收数据</div>
                        <div class="metric-value">{tp.get('received_kb_per_sec', 0)}<span class="metric-unit">KB/s</span></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">发送数据</div>
                        <div class="metric-value">{tp.get('sent_kb_per_sec', 0)}<span class="metric-unit">KB/s</span></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <h2>📋 各接口详情</h2>
                <table>
                    <thead>
                        <tr>
                            <th>接口标签</th>
                            <th>请求数</th>
                            <th>错误率</th>
                            <th>平均响应时间</th>
                            <th>TP90</th>
                            <th>TP95</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
'''

        for label, data in by_label.items():
            error_rate = data.get('error_rate', 0)
            avg_rt = data.get('response_time', {}).get('average', 0)
            tp90 = data.get('response_time', {}).get('tp90', 0)
            tp95 = data.get('response_time', {}).get('tp95', 0)

            if error_rate > 5 or tp90 > 2000:
                status_badge = '<span class="badge badge-danger">需优化</span>'
            elif error_rate > 1 or tp90 > 1000:
                status_badge = '<span class="badge badge-warning">关注</span>'
            else:
                status_badge = '<span class="badge badge-success">良好</span>'

            html += f'''                        <tr>
                            <td><strong>{label}</strong></td>
                            <td>{data.get('count', 0)}</td>
                            <td>{error_rate:.2f}%</td>
                            <td>{avg_rt} ms</td>
                            <td>{tp90} ms</td>
                            <td>{tp95} ms</td>
                            <td>{status_badge}</td>
                        </tr>
'''

        html += f'''                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <h2>💡 优化建议</h2>
'''

        for sugg in suggestions:
            severity = sugg.get('severity', '低')
            severity_class = 'success' if severity == '低' else ('warning' if severity == '中' else 'danger')

            html += f'''                <div class="suggestion {severity_class}">
                    <div class="suggestion-title">[{sugg.get('category', '其他')}] {sugg.get('issue', '')}</div>
                    <ul class="suggestion-list">
'''

            for item in sugg.get('suggestions', []):
                html += f'''                        <li>{item}</li>
'''

            html += f'''                    </ul>
                </div>
'''

        html += f'''            </div>
        </div>
    </div>
</body>
</html>'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='JMeter JTL 结果解析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python parse_jtl.py --jtl result.jtl --output report.json --format json
  python parse_jtl.py --jtl result.jtl --output report.html --format html
  python parse_jtl.py --jtl result.jtl --output report.csv --format csv
        '''
    )

    parser.add_argument(
        '--jtl', '-j',
        type=str,
        required=True,
        help='JTL 结果文件路径'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default='report.json',
        help='输出报告路径，默认: report.json'
    )

    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['json', 'html', 'csv'],
        default='json',
        help='输出格式: json, html, csv，默认: json'
    )

    parser.add_argument(
        '--charts',
        action='store_true',
        help='生成图表（需要 matplotlib）'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("JTL 结果解析器")
    print("=" * 60)
    print(f"输入文件: {args.jtl}")
    print(f"输出文件: {args.output}")
    print(f"输出格式: {args.format}")
    print("-" * 60)

    try:
        parser = JTLParser()

        print("正在解析 JTL 文件...")
        if not parser.parse(args.jtl):
            print("错误: 解析失败")
            return 1

        print(f"[OK] 解析完成，共 {len(parser.samples)} 个样本")

        metrics = parser.calculate_metrics()
        summary = metrics.get('summary', {})
        rt = metrics.get('response_time', {})
        tp = metrics.get('throughput', {})

        if args.verbose:
            print()
            print("-" * 60)
            print("关键指标:")
            print(f"  总请求数: {summary.get('total_samples', 0)}")
            print(f"  错误率: {summary.get('error_rate', 0):.2f}%")
            print(f"  平均响应时间: {rt.get('average', 0)} ms")
            print(f"  TP90: {rt.get('tp90', 0)} ms")
            print(f"  吞吐量: {tp.get('total_requests_per_sec', 0)} req/s")

        print()
        print("正在生成报告...")
        parser.generate_report(args.output, args.format, args.charts)
        print(f"[OK] 报告已生成: {args.output}")

        suggestions = parser.generate_optimization_suggestions(metrics)
        if args.verbose:
            print()
            print("-" * 60)
            print("优化建议:")
            for sugg in suggestions[:3]:
                print(f"  [{sugg.get('severity')}] {sugg.get('issue')}")
                for item in sugg.get('suggestions', [])[:2]:
                    print(f"    - {item}")

        print()
        print("=" * 60)
        print("解析完成")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
