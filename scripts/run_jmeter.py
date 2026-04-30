#!/usr/bin/env python3
"""
JMeter 执行脚本 - 管理 JMeter 压测执行流程

功能:
1. 检查 JMeter 环境和版本
2. 构建 JMeter CLI 命令
3. 执行压测并监控进度
4. 处理错误和异常
5. 支持分布式压测

用法:
    python run_jmeter.py --jmx test.jmx --result result.jtl \
        --log jmeter.log \
        --param concurrency=100 \
        --param duration=600
"""

import argparse
import os
import re
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple


class JMeterExecutor:
    """JMeter 执行器类"""

    REQUIRED_VERSION = (5, 4)

    def __init__(self, jmeter_path: str = None):
        """
        初始化执行器

        Args:
            jmeter_path: JMeter 可执行文件路径，默认为 'jmeter'（从 PATH 查找）
        """
        self.jmeter_path = jmeter_path or 'jmeter'
        self.version = None
        self.version_info = None

    def check_jmeter_version(self) -> Tuple[bool, str]:
        """
        检查 JMeter 版本

        Returns:
            (是否符合要求, 版本信息)
        """
        try:
            result = subprocess.run(
                [self.jmeter_path, '--version'],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr

            version_match = re.search(r'Version\s+(\d+)\.(\d+)', output, re.IGNORECASE)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                self.version = f"{major}.{minor}"
                self.version_info = (major, minor)

                if (major, minor) >= self.REQUIRED_VERSION:
                    return True, f"JMeter 版本 {self.version} 符合要求 (>= {self.REQUIRED_VERSION[0]}.{self.REQUIRED_VERSION[1]})"
                else:
                    return False, f"JMeter 版本 {self.version} 过低，需要 >= {self.REQUIRED_VERSION[0]}.{self.REQUIRED_VERSION[1]}"
            else:
                return False, f"无法解析 JMeter 版本信息: {output[:200]}"

        except FileNotFoundError:
            return False, f"未找到 JMeter 命令: {self.jmeter_path}，请确保已安装并添加到 PATH"
        except subprocess.TimeoutExpired:
            return False, "检查 JMeter 版本超时"
        except Exception as e:
            return False, f"检查 JMeter 版本时出错: {str(e)}"

    def validate_jmx_file(self, jmx_path: str) -> Tuple[bool, str]:
        """
        验证 JMX 文件

        Args:
            jmx_path: JMX 文件路径

        Returns:
            (是否有效, 错误信息)
        """
        if not os.path.exists(jmx_path):
            return False, f"JMX 文件不存在: {jmx_path}"

        if not os.path.isfile(jmx_path):
            return False, f"路径不是文件: {jmx_path}"

        try:
            with open(jmx_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)

            if '<jmeterTestPlan' not in content:
                return False, "JMX 文件格式无效，缺少 jmeterTestPlan 根元素"

            return True, "JMX 文件验证通过"
        except Exception as e:
            return False, f"读取 JMX 文件时出错: {str(e)}"

    def build_command(
        self,
        jmx_path: str,
        result_path: str,
        log_path: str,
        params: Dict[str, any] = None,
        distributed: bool = False,
        remote_hosts: List[str] = None,
        jmeter_home: str = None,
        additional_args: List[str] = None
    ) -> List[str]:
        """
        构建 JMeter 命令

        Args:
            jmx_path: JMX 文件路径
            result_path: 结果文件路径
            log_path: 日志文件路径
            params: 运行时参数字典
            distributed: 是否启用分布式压测
            remote_hosts: 远程服务器列表
            jmeter_home: JMeter 安装目录
            additional_args: 额外命令行参数

        Returns:
            命令参数列表
        """
        cmd = [self.jmeter_path, '-n', '-t', jmx_path, '-l', result_path, '-j', log_path]

        if params:
            for key, value in params.items():
                cmd.extend(['-J', f'{key}={value}'])

        if distributed:
            cmd.append('-r')
            if remote_hosts:
                cmd.extend(['-R', ','.join(remote_hosts)])

        if jmeter_home:
            env = os.environ.copy()
            env['JMETER_HOME'] = jmeter_home

        if additional_args:
            cmd.extend(additional_args)

        return cmd

    def ensure_output_dirs(self, result_path: str, log_path: str):
        """
        确保输出目录存在

        Args:
            result_path: 结果文件路径
            log_path: 日志文件路径
        """
        for path in [result_path, log_path]:
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

    def execute(
        self,
        jmx_path: str,
        result_path: str,
        log_path: str,
        params: Dict[str, any] = None,
        distributed: bool = False,
        remote_hosts: List[str] = None,
        timeout: int = None,
        show_progress: bool = True
    ) -> Dict:
        """
        执行 JMeter 压测

        Args:
            jmx_path: JMX 文件路径
            result_path: 结果文件路径
            log_path: 日志文件路径
            params: 运行时参数
            distributed: 是否分布式
            remote_hosts: 远程主机列表
            timeout: 超时时间（秒）
            show_progress: 是否显示进度

        Returns:
            执行结果字典
        """
        result = {
            'success': False,
            'return_code': None,
            'command': None,
            'output': '',
            'error': '',
            'duration': None,
            'start_time': None,
            'end_time': None
        }

        jmx_valid, jmx_msg = self.validate_jmx_file(jmx_path)
        if not jmx_valid:
            result['error'] = jmx_msg
            return result

        self.ensure_output_dirs(result_path, log_path)

        cmd = self.build_command(
            jmx_path=jmx_path,
            result_path=result_path,
            log_path=log_path,
            params=params,
            distributed=distributed,
            remote_hosts=remote_hosts
        )

        result['command'] = ' '.join(cmd)

        print("=" * 60)
        print("JMeter 执行配置")
        print("=" * 60)
        print(f"命令: {result['command']}")
        print(f"JMX 文件: {jmx_path}")
        print(f"结果文件: {result_path}")
        print(f"日志文件: {log_path}")
        if params:
            print(f"运行时参数: {params}")
        if distributed:
            print(f"分布式压测: 启用")
            if remote_hosts:
                print(f"远程主机: {remote_hosts}")
        print("-" * 60)
        print("开始执行压测...")
        print()

        start_time = time.time()
        result['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            output_lines = []

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if line:
                    line = line.rstrip()
                    output_lines.append(line)
                    if show_progress:
                        print(f"  [{time.strftime('%H:%M:%S')}] {line}")

            return_code = process.wait(timeout=timeout if timeout else None)
            result['return_code'] = return_code
            result['output'] = '\n'.join(output_lines)

            end_time = time.time()
            result['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
            result['duration'] = round(end_time - start_time, 2)

            if return_code == 0:
                result['success'] = True
                print()
                print("=" * 60)
                print("[OK] 压测执行完成")
                print("=" * 60)
                print(f"返回码: {return_code}")
                print(f"执行时间: {result['duration']} 秒")
                print(f"结果文件: {result_path}")
                print(f"日志文件: {log_path}")
            else:
                result['error'] = f"JMeter 执行失败，返回码: {return_code}"
                print()
                print("=" * 60)
                print("[ERROR] 压测执行失败")
                print("=" * 60)
                print(f"返回码: {return_code}")
                print(f"执行时间: {result['duration']} 秒")
                if result['output']:
                    print(f"输出: {result['output'][-1000:] if len(result['output']) > 1000 else result['output']}")

        except subprocess.TimeoutExpired:
            result['error'] = f"压测执行超时（设置的超时时间: {timeout} 秒）"
            process.kill()
            process.wait()

        except Exception as e:
            result['error'] = f"执行过程中出错: {str(e)}"
            import traceback
            traceback.print_exc()

        return result

    def parse_run_summary(self, output: str) -> Dict:
        """
        解析 JMeter 运行摘要

        Args:
            output: JMeter 输出内容

        Returns:
            摘要信息字典
        """
        summary = {
            'total_samples': None,
            'error_count': None,
            'error_rate': None,
            'throughput': None,
            'avg_response_time': None,
        }

        summary_match = re.search(
            r'summary\s*=\s*(\d+)\s+in\s+([\d:.]+)\s*=\s*([\d.]+)/s\s+Avg:\s*(\d+)\s+Min:\s*(\d+)\s+Max:\s*(\d+)\s+Err:\s*(\d+)\s*\(([\d.]+)%\)',
            output,
            re.IGNORECASE
        )

        if summary_match:
            summary['total_samples'] = int(summary_match.group(1))
            summary['throughput'] = float(summary_match.group(3))
            summary['avg_response_time'] = int(summary_match.group(4))
            summary['min_response_time'] = int(summary_match.group(5))
            summary['max_response_time'] = int(summary_match.group(6))
            summary['error_count'] = int(summary_match.group(7))
            summary['error_rate'] = float(summary_match.group(8))

        return summary


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='JMeter 压测执行器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python run_jmeter.py --jmx test.jmx --result result.jtl --log jmeter.log
  python run_jmeter.py --jmx test.jmx --result result.jtl --log jmeter.log \
    --param concurrency=100 --param duration=600
  python run_jmeter.py --jmx test.jmx --distributed --remote-hosts slave1,slave2
  python run_jmeter.py --check-environment
        '''
    )

    parser.add_argument(
        '--jmx', '-t',
        type=str,
        help='JMX 测试计划文件路径'
    )

    parser.add_argument(
        '--result', '-l',
        type=str,
        default='result.jtl',
        help='结果文件路径（JTL 格式），默认: result.jtl'
    )

    parser.add_argument(
        '--log', '-j',
        type=str,
        default='jmeter.log',
        help='日志文件路径，默认: jmeter.log'
    )

    parser.add_argument(
        '--param', '-p',
        action='append',
        default=[],
        help='运行时参数，格式为 key=value，可多次使用（使用 -J 参数传递给 JMeter）'
    )

    parser.add_argument(
        '--distributed', '-d',
        action='store_true',
        help='启用分布式压测'
    )

    parser.add_argument(
        '--remote-hosts', '-R',
        type=str,
        help='远程服务器列表，逗号分隔（如: slave1,slave2,slave3）'
    )

    parser.add_argument(
        '--jmeter-path',
        type=str,
        help='JMeter 可执行文件路径（默认从 PATH 查找）'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        help='超时时间（秒），默认无限制'
    )

    parser.add_argument(
        '--check-environment',
        action='store_true',
        help='仅检查 JMeter 环境，不执行压测'
    )

    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='不显示实时进度输出'
    )

    args = parser.parse_args()

    executor = JMeterExecutor(args.jmeter_path)

    print("=" * 60)
    print("JMeter 环境检查")
    print("=" * 60)
    version_ok, version_msg = executor.check_jmeter_version()
    print(version_msg)

    if args.check_environment:
        print("-" * 60)
        if version_ok:
            print("[OK] 环境检查通过")
            return 0
        else:
            print("[ERROR] 环境检查失败")
            return 1

    if not version_ok:
        print(f"\n错误: {version_msg}")
        return 1

    if not args.jmx:
        parser.error("需要指定 --jmx 参数")

    params = {}
    for param in args.param:
        if '=' in param:
            key, value = param.split('=', 1)
            params[key.strip()] = value.strip()

    remote_hosts = None
    if args.remote_hosts:
        remote_hosts = [h.strip() for h in args.remote_hosts.split(',')]

    result = executor.execute(
        jmx_path=args.jmx,
        result_path=args.result,
        log_path=args.log,
        params=params,
        distributed=args.distributed,
        remote_hosts=remote_hosts,
        timeout=args.timeout,
        show_progress=not args.no_progress
    )

    if result['success'] and result['output']:
        summary = executor.parse_run_summary(result['output'])
        if summary.get('total_samples') is not None:
            print()
            print("-" * 60)
            print("运行摘要:")
            print(f"  总请求数: {summary['total_samples']}")
            print(f"  平均响应时间: {summary.get('avg_response_time', 'N/A')} ms")
            print(f"  吞吐量: {summary.get('throughput', 'N/A')} 请求/秒")
            print(f"  错误数: {summary.get('error_count', 0)} ({summary.get('error_rate', 0)}%)")

    if result['success']:
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
