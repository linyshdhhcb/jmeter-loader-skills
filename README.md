# jmeter-loader-skills

JMeter 压测自动化工具集，提供从测试计划生成到性能优化建议的完整压测流程解决方案。

## 功能特性

- **JMX 测试计划生成**：基于模板动态生成符合 JMeter 5.4+ 规范的测试计划
- **压测执行管理**：支持本地和分布式压测，实时监控执行状态
- **结果解析分析**：支持 CSV/XML 格式 JTL 文件解析，生成多维度性能报告
- **优化建议生成**：基于性能指标自动评估系统瓶颈并提供优化建议
- **模板化设计**：内置多种场景模板，支持自定义扩展

## 目录结构

```
jmeter-loader-skills/
├── assets/
│   ├── samples/          # 示例数据文件
│   └── templates/        # JMX 模板文件
│       ├── base.jmx              # 基础 HTTP 模板
│       ├── csv_data.jmx          # CSV 数据源模板
│       └── auth_flow.jmx         # 鉴权流程模板
├── references/           # 参考文档
├── scripts/              # 核心脚本
│   ├── generate_jmx.py   # JMX 生成脚本
│   ├── run_jmeter.py     # JMeter 执行脚本
│   ├── parse_jtl.py      # JTL 结果解析脚本
│   └── requirements.txt  # Python 依赖
└── SKILL.md              # 技能描述文档
```

## 环境要求

- JMeter 5.4 或更高版本
- Python 3.7 或更高版本
- 操作系统：Windows、Linux、macOS

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/your-username/jmeter-loader-skills.git
cd jmeter-loader-skills
```

2. 安装 Python 依赖：
```bash
cd scripts
pip install -r requirements.txt
```

3. 确保 JMeter 已添加到系统 PATH，或通过 `--jmeter-path` 参数指定路径。

## 使用方法

### 1. 生成 JMX 测试计划

使用 `generate_jmx.py` 基于模板和参数生成测试计划：

```bash
python generate_jmx.py --template base.jmx --output test.jmx \
  --param target_host=example.com \
  --param target_port=80 \
  --param target_path=/api/users \
  --param method=GET \
  --param concurrency=50 \
  --param duration=300
```

查看可用模板：
```bash
python generate_jmx.py --list-templates
```

### 2. 执行压测

使用 `run_jmeter.py` 执行 JMeter 压测：

```bash
python run_jmeter.py --jmx test.jmx --result result.jtl --log jmeter.log
```

运行时参数覆盖：
```bash
python run_jmeter.py --jmx test.jmx --result result.jtl --log jmeter.log \
  --param concurrency=100 \
  --param duration=600
```

分布式压测：
```bash
python run_jmeter.py --jmx test.jmx --distributed --remote-hosts slave1,slave2
```

检查环境：
```bash
python run_jmeter.py --check-environment
```

### 3. 解析结果

使用 `parse_jtl.py` 解析 JTL 结果文件并生成报告：

生成 JSON 报告：
```bash
python parse_jtl.py --jtl result.jtl --output report.json --format json
```

生成 HTML 报告：
```bash
python parse_jtl.py --jtl result.jtl --output report.html --format html
```

生成 CSV 报告：
```bash
python parse_jtl.py --jtl result.jtl --output report.csv --format csv
```

## 模板说明

| 模板名称 | 适用场景 | 主要组件 |
|---------|---------|---------|
| base.jmx | 简单 HTTP 接口压测 | 标准线程组、HTTP 请求采样器、结果收集器 |
| csv_data.jmx | 数据驱动测试 | CSV 数据集配置、参数化 HTTP 请求、循环控制器 |
| auth_flow.jmx | 需鉴权的业务流程 | 登录请求、Token 提取器、带认证头的业务请求、Cookie 管理器 |

## 性能指标

解析器计算以下核心性能指标：

- **响应时间**：Min、Max、Average、Median、TP90、TP95、TP99
- **吞吐量**：请求/秒、接收 KB/秒、发送 KB/秒
- **错误分析**：错误率、错误类型统计
- **多维度**：按接口标签分组、时间趋势分析

## 性能评估标准

| 指标 | 优秀 | 良好 | 一般 | 需优化 |
|------|------|------|------|--------|
| 平均响应时间 | < 200ms | < 500ms | < 1s | >= 1s |
| TP90 响应时间 | < 500ms | < 1s | < 2s | >= 2s |
| 错误率 | < 0.1% | < 1% | < 5% | >= 5% |

## 示例工作流

完整的压测流程示例：

```bash
# 1. 生成测试计划
python generate_jmx.py --template base.jmx --output test.jmx \
  --param target_host=api.example.com \
  --param target_port=80 \
  --param target_path=/users \
  --param method=GET \
  --param concurrency=50 \
  --param duration=300

# 2. 执行压测
python run_jmeter.py --jmx test.jmx --result results.jtl --log jmeter.log

# 3. 解析结果并生成报告
python parse_jtl.py --jtl results.jtl --output report.html --format html --verbose
```

## 安全注意事项

- 密码、Token 等敏感信息使用 JMeter 内置加密或从外部传入
- 压测目标需获得授权，避免在生产环境进行未经授权的压测
- 压测数据应使用测试数据而非真实数据
- 结果文件和日志文件避免记录敏感信息

## 常见问题

**Q: JMX 文件生成后无法运行？**
A: 检查 JMeter 版本兼容性（5.4+），确认 XML 格式正确，验证所有引用的组件存在。

**Q: 压测执行时报内存不足？**
A: 调整 JMeter 堆大小：`HEAP="-Xms1g -Xmx4g"`，或使用分布式压测分散负载。

**Q: 结果文件解析失败？**
A: 检查 JTL 文件格式完整性，确认包含必要字段，使用 `--verbose` 参数查看详细错误信息。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。

## 更新日志

- v1.0.0: 初始版本，支持基础 HTTP 压测全流程
