#!/usr/bin/env python3
"""
JMX 生成脚本 - 基于模板和用户参数动态生成 JMeter 测试计划

功能:
1. 加载 Jinja2 模板
2. 解析用户参数
3. 渲染生成 JMX 文件
4. 验证输出格式

用法:
    python generate_jmx.py --template base.jmx --output test.jmx \
        --param target_host=example.com \
        --param concurrency=50
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Any

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


class JMXGenerator:
    """JMX 文件生成器类"""

    def __init__(self, template_dir: str = None):
        """
        初始化生成器

        Args:
            template_dir: 模板目录路径，默认为脚本所在目录的 ../assets/templates/
        """
        if template_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(
                os.path.dirname(script_dir),
                'assets',
                'templates'
            )
        self.template_dir = template_dir
        self.env = None

        if JINJA2_AVAILABLE:
            self.env = Environment(
                loader=FileSystemLoader(template_dir),
                trim_blocks=True,
                lstrip_blocks=True
            )

    def list_available_templates(self) -> List[str]:
        """
        列出可用的模板文件

        Returns:
            模板文件名列表
        """
        templates = []
        if os.path.exists(self.template_dir):
            for file in os.listdir(self.template_dir):
                if file.endswith('.jmx'):
                    templates.append(file)
        return sorted(templates)

    def parse_parameters(self, params_list: List[str]) -> Dict[str, Any]:
        """
        解析参数列表

        Args:
            params_list: 参数列表，格式为 ["key=value", ...]

        Returns:
            参数字典
        """
        params = {}
        for param in params_list:
            if '=' in param:
                key, value = param.split('=', 1)
                key = key.strip()
                value = value.strip()

                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif self._is_float(value):
                    value = float(value)

                params[key] = value
        return params

    def _is_float(self, value: str) -> bool:
        """检查字符串是否为浮点数"""
        try:
            float(value)
            return '.' in value or 'e' in value.lower()
        except ValueError:
            return False

    def _apply_defaults(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用默认参数值

        Args:
            params: 用户参数

        Returns:
            包含默认值的完整参数
        """
        defaults = {
            'concurrency': 10,
            'rampup': 10,
            'duration': 60,
            'target_port': 80,
            'protocol': 'http',
            'method': 'GET',
            'target_path': '/',
        }

        result = defaults.copy()
        result.update(params)
        return result

    def generate_with_jinja2(self, template_name: str, params: Dict[str, Any]) -> str:
        """
        使用 Jinja2 渲染模板

        Args:
            template_name: 模板文件名
            params: 参数字典

        Returns:
            渲染后的 JMX 内容
        """
        if not JINJA2_AVAILABLE:
            raise ImportError("Jinja2 未安装，请运行: pip install jinja2")

        full_params = self._apply_defaults(params)

        try:
            template = self.env.get_template(template_name)
            return template.render(**full_params)
        except TemplateNotFound:
            raise FileNotFoundError(f"模板文件不存在: {template_name}")

    def generate_simple(self, template_name: str, params: Dict[str, Any]) -> str:
        """
        简单的字符串替换方式（不依赖 Jinja2）

        Args:
            template_name: 模板文件名
            params: 参数字典

        Returns:
            渲染后的 JMX 内容
        """
        template_path = os.path.join(self.template_dir, template_name)

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"模板文件不存在: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        full_params = self._apply_defaults(params)

        for key, value in full_params.items():
            placeholder = f"{{{{" + key + "}}}}"
            content = content.replace(placeholder, str(value))

        return content

    def generate(self, template_name: str, params: Dict[str, Any], use_jinja2: bool = None) -> str:
        """
        生成 JMX 内容

        Args:
            template_name: 模板文件名
            params: 参数字典
            use_jinja2: 是否使用 Jinja2，None 时自动判断

        Returns:
            渲染后的 JMX 内容
        """
        if use_jinja2 is None:
            use_jinja2 = JINJA2_AVAILABLE

        if use_jinja2:
            return self.generate_with_jinja2(template_name, params)
        else:
            return self.generate_simple(template_name, params)

    def validate_jmx(self, content: str) -> bool:
        """
        验证 JMX 内容是否符合基本格式

        Args:
            content: JMX XML 内容

        Returns:
            是否有效
        """
        required_elements = [
            '<jmeterTestPlan',
            '</jmeterTestPlan>',
            '<hashTree>',
            '</hashTree>'
        ]

        for element in required_elements:
            if element not in content:
                print(f"警告: 缺少必要元素 {element}")
                return False

        return True

    def save_to_file(self, content: str, output_path: str) -> bool:
        """
        保存内容到文件

        Args:
            content: JMX 内容
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='JMeter JMX 测试计划生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python generate_jmx.py --template base.jmx --output test.jmx \
    --param target_host=api.example.com \
    --param target_port=8080 \
    --param concurrency=50 \
    --param duration=300

  python generate_jmx.py --list-templates
        '''
    )

    parser.add_argument(
        '--template', '-t',
        type=str,
        help='模板文件名（位于 assets/templates/ 目录）'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='输出 JMX 文件路径'
    )

    parser.add_argument(
        '--param', '-p',
        action='append',
        default=[],
        help='参数键值对，格式为 key=value，可多次使用'
    )

    parser.add_argument(
        '--template-dir',
        type=str,
        help='模板目录路径'
    )

    parser.add_argument(
        '--list-templates', '-l',
        action='store_true',
        help='列出所有可用的模板'
    )

    parser.add_argument(
        '--no-jinja2',
        action='store_true',
        help='不使用 Jinja2，使用简单字符串替换'
    )

    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='验证生成的 JMX 格式'
    )

    args = parser.parse_args()

    generator = JMXGenerator(args.template_dir)

    if args.list_templates:
        templates = generator.list_available_templates()
        print("可用模板:")
        for tmpl in templates:
            print(f"  - {tmpl}")
        return 0

    if not args.template:
        parser.error("需要指定 --template 参数")

    if not args.output:
        parser.error("需要指定 --output 参数")

    params = generator.parse_parameters(args.param)

    print("=" * 60)
    print("JMX 生成配置")
    print("=" * 60)
    print(f"模板: {args.template}")
    print(f"输出: {args.output}")
    print(f"参数: {params}")
    print(f"使用 Jinja2: {JINJA2_AVAILABLE and not args.no_jinja2}")
    print("-" * 60)

    try:
        content = generator.generate(
            args.template,
            params,
            use_jinja2=not args.no_jinja2
        )

        if args.validate:
            if generator.validate_jmx(content):
                print("[OK] JMX 格式验证通过")
            else:
                print("[WARNING] JMX 格式警告：缺少某些必要元素")

        generator.save_to_file(content, args.output)
        print(f"[OK] JMX 文件已生成: {args.output}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
