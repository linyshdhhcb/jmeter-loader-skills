# jmeter-loader-skills

JMeter 压测自动化工具集，提供从测试计划生成到性能优化建议的完整压测流程解决方案。基于 Apache JMeter 5.x 官方文档构建，涵盖 129 个组件、49 个内置函数、分布式测试、HTML 报告生成等完整知识体系。

## 功能特性

- **JMX 测试计划生成**：支持模板模式和动态组装模式，动态模式支持 8 大类 24 种组件自由组合
- **压测执行管理**：支持本地和分布式压测，实时监控执行状态
- **结果解析分析**：支持 CSV/XML 格式 JTL 文件解析，生成多维度性能报告
- **优化建议生成**：基于性能指标自动评估系统瓶颈并提供优化建议
- **模板化设计**：内置 7 种场景模板，覆盖单接口、多接口、阶梯加压、数据库、业务流程等场景
- **完整参考文档**：8 份参考文档，涵盖组件参考、函数参考、最佳实践、分布式测试、属性配置等

## 目录结构

```
jmeter-loader-skills/
├── assets/
│   ├── samples/              # 示例数据文件
│   └── templates/            # JMX 模板文件
│       ├── base.jmx          # 基础 HTTP 模板
│       ├── csv_data.jmx      # CSV 数据源模板
│       ├── auth_flow.jmx     # 鉴权流程模板
│       ├── multi_api.jmx     # 多接口混合压测模板
│       ├── staged_load.jmx   # 阶梯加压模板
│       ├── jdbc_test.jmx     # JDBC 数据库压测模板
│       └── business_flow.jmx # 业务流程模板
├── references/               # 参考文档
│   ├── component_reference.md  # 全部 129 个组件参考（9 大类）
│   ├── functions_reference.md  # 全部 49 个内置函数参考（8 大类）
│   ├── best_practices.md       # 最佳实践、测试计划结构、术语表
│   ├── distributed_testing.md  # 分布式测试完整指南
│   ├── dashboard_report.md     # HTML 仪表板报告生成、JTL 格式
│   ├── properties_reference.md # 性能测试关键属性参考（20 大类）
│   ├── jmx_structure.md        # JMX XML 结构参考（16 节，45+ 组件片段）
│   └── sampler_types.md        # Sampler 类型配置说明
├── scripts/                  # 核心脚本
│   ├── generate_jmx.py       # JMX 生成脚本（模板 + 动态组装）
│   ├── run_jmeter.py         # JMeter 执行脚本
│   ├── parse_jtl.py          # JTL 结果解析脚本
│   └── requirements.txt      # Python 依赖
├── SKILL.md                  # 技能描述文档
└── README.md
```

## 环境要求

- JMeter 5.x 或更高版本
- Python 3.x 或更高版本
- 操作系统：Windows、Linux、macOS

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/your-username/jmeter-loader-skills.git
cd jmeter-loader-skills
```

1. 安装 Python 依赖：

```bash
cd scripts
pip install -r requirements.txt
```

1. 确保 JMeter 已添加到系统 PATH，或通过 `--jmeter-path` 参数指定路径。

## 使用方法

### 1. 生成 JMX 测试计划

支持两种生成模式：

#### 模板模式

选择预置模板，参数替换后输出：

```bash
python scripts/generate_jmx.py --template base.jmx --output test.jmx \
  --param target_host=example.com \
  --param target_port=80 \
  --param target_path=/api/users \
  --param method=GET \
  --param concurrency=50 \
  --param duration=300
```

#### 动态组装模式

根据组件列表从零构建 JMX，支持 8 大类 24 种组件自由组合：

```bash
python scripts/generate_jmx.py --build --output test.jmx \
  --param target_host=api.example.com \
  --http-sampler name=GetUsers,path=/api/users,method=GET \
  --http-sampler name=CreateOrder,path=/api/orders,method=POST,body='{"item":"test"}' \
  --timer timer_type=gaussian,delay_ms=300,range_ms=100 \
  --assertion type=response,patterns=200 \
  --backend-listener type=influxdb,influxdb_url=http://localhost:8086
```

动态组装支持的组件：

| 类别          | 组件                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------ |
| Samplers    | http\_sampler, debug\_sampler                                                                          |
| Controllers | if\_controller, transaction\_controller, once\_only\_controller, loop\_controller, foreach\_controller |
| Timers      | constant\_timer, gaussian\_timer, uniform\_timer, synchronizing\_timer                                 |
| Extractors  | json\_extractor, boundary\_extractor, regex\_extractor                                                 |
| Assertions  | response\_assertion, duration\_assertion, json\_assertion                                              |
| Config      | http\_defaults, header\_manager, cookie\_manager, cache\_manager, csv\_data\_set                       |
| Processors  | jsr223\_postprocessor, jsr223\_preprocessor                                                            |
| Listeners   | result\_collector, backend\_listener\_influxdb                                                         |

#### 查看可用模板和组件

```bash
python scripts/generate_jmx.py --list-templates
python scripts/generate_jmx.py --list-components
```

### 2. 执行压测

使用 `run_jmeter.py` 执行 JMeter 压测：

```bash
python scripts/run_jmeter.py --jmx test.jmx --result result.jtl --log jmeter.log
```

运行时参数覆盖：

```bash
python scripts/run_jmeter.py --jmx test.jmx --result result.jtl --log jmeter.log \
  --param concurrency=100 \
  --param duration=600
```

分布式压测：

```bash
python scripts/run_jmeter.py --jmx test.jmx --distributed --remote-hosts slave1,slave2
```

检查环境：

```bash
python scripts/run_jmeter.py --check-environment
```

### 3. 解析结果

使用 `parse_jtl.py` 解析 JTL 结果文件并生成报告：

生成 JSON 报告：

```bash
python scripts/parse_jtl.py --jtl result.jtl --output report.json --format json
```

生成 HTML 报告：

```bash
python scripts/parse_jtl.py --jtl result.jtl --output report.html --format html
```

### 4. 生成 JMeter HTML 仪表板报告

```bash
# 从已有 JTL 生成
jmeter -g result.jtl -o report/

# 测试后自动生成
jmeter -n -t test.jmx -l result.jtl -e -o report/
```

## 模板说明

| 模板名称                | 适用场景         | 主要组件                                                             |
| ------------------- | ------------ | ---------------------------------------------------------------- |
| base.jmx            | 简单 HTTP 接口压测 | 标准线程组、HTTP 请求采样器、结果收集器                                           |
| csv\_data.jmx       | 数据驱动测试       | CSV 数据集配置、参数化 HTTP 请求、循环控制器                                      |
| auth\_flow\.jmx     | 需鉴权的业务流程     | 登录请求、Token 提取器、带认证头的业务请求、Cookie 管理器                              |
| multi\_api.jmx      | 多接口混合压测      | 3 个 HTTP 采样器、JSON 提取器、接口间数据串联、InfluxDB 监听器                       |
| staged\_load.jmx    | 阶梯加压测试       | 3 个顺序线程组（低→中→高）、Duration 断言、InfluxDB 监听器                         |
| jdbc\_test.jmx      | 数据库性能测试      | JDBC 连接池、Select/Insert/Update 采样器、Prepared Statement             |
| business\_flow\.jmx | 完整业务流程       | Transaction Controller、Once Only Controller、If Controller、数据提取链路 |

## 性能指标

解析器计算以下核心性能指标：

- **响应时间**：Min、Max、Average、Median、TP90、TP95、TP99
- **吞吐量**：请求/秒、接收 KB/秒、发送 KB/秒
- **错误分析**：错误率、错误类型统计
- **多维度**：按接口标签分组、时间趋势分析

## 性能评估标准

| 指标        | 优秀      | 良好      | 一般   | 需优化   |
| --------- | ------- | ------- | ---- | ----- |
| 平均响应时间    | < 200ms | < 500ms | < 1s | >= 1s |
| TP90 响应时间 | < 500ms | < 1s    | < 2s | >= 2s |
| 错误率       | < 0.1%  | < 1%    | < 5% | >= 5% |

## 示例工作流

### 示例 1：简单 HTTP 接口压测

```bash
# 1. 生成测试计划
python scripts/generate_jmx.py --template base.jmx --output test.jmx \
  --param target_host=api.example.com \
  --param target_path=/users \
  --param method=GET \
  --param concurrency=50 \
  --param duration=300

# 2. 执行压测
python scripts/run_jmeter.py --jmx test.jmx --result results.jtl --log jmeter.log

# 3. 解析结果
python scripts/parse_jtl.py --jtl results.jtl --output report.html --format html
```

### 示例 2：动态组装多接口压测

```bash
python scripts/generate_jmx.py --build --output test.jmx \
  --param target_host=api.example.com \
  --http-sampler name=GetUsers,path=/api/users,method=GET \
  --http-sampler name=CreateOrder,path=/api/orders,method=POST,body='{"userId":"1"}' \
  --timer timer_type=gaussian,delay_ms=300,range_ms=100 \
  --assertion type=response,patterns=200
```

### 示例 3：阶梯加压测试

```bash
python scripts/generate_jmx.py --template staged_load.jmx --output staged.jmx \
  --param target_host=api.example.com \
  --param stage1_threads=10 --param stage1_duration=60 \
  --param stage2_threads=50 --param stage2_duration=120 \
  --param stage3_threads=100 --param stage3_duration=180
```

### 示例 4：分布式压测

```bash
# Slave 机器上启动
./jmeter-server

# Master 上执行
jmeter -n -t test.jmx -l result.jtl -r \
  -Gconcurrency=100 -Gduration=300 -X
```

## 安全注意事项

- 密码、Token 等敏感信息使用 JMeter 内置加密或从外部传入
- 压测目标需获得授权，避免在生产环境进行未经授权的压测
- 压测数据应使用测试数据而非真实数据
- 结果文件和日志文件避免记录敏感信息
- 分布式测试 RMI 默认使用 SSL，确保密钥库正确配置

## 常见问题

**Q: JMX 文件生成后无法运行？**
A: 检查 JMeter 版本兼容性（5.4+），确认 XML 格式正确，验证所有引用的组件存在。

**Q: 压测执行时报内存不足？**
A: 调整 JMeter 堆大小：`HEAP="-Xms1g -Xmx4g"`，使用 CLI 模式运行，减少监听器数量，或使用分布式压测分散负载。

**Q: 结果文件解析失败？**
A: 检查 JTL 文件格式完整性，确认包含必要字段，使用 `--verbose` 参数查看详细错误信息。

**Q: JSR223 脚本缓存后变量值不更新？**
A: 使用脚本缓存时，不要在脚本中使用 `${varName}` 引用变量（缓存只会取第一次的值），应改用 `vars.get("varName")`。

**Q: BeanShell 和 JSR223 + Groovy 如何选择？**
A: 始终选择 JSR223 + Groovy。Groovy 支持 Compilable 接口可缓存编译脚本，BeanShell 不支持真正编译性能差。自 JMeter 3.1 起官方推荐 JSR223 + Groovy。

**Q: 如何生成 HTML 报告？**
A: 两种方式：测试时自动生成 `jmeter -n -t test.jmx -l result.jtl -e -o report/`，或从已有 JTL 生成 `jmeter -g result.jtl -o report/`。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。

## 更新日志

- v2.0.0: 基于 JMeter 官方文档全面完善；新增 4 个场景模板（多接口/阶梯加压/JDBC/业务流程）；重构 generate\_jmx.py 支持动态组件组装（24 种组件）；新增 6 份参考文档（组件/函数/最佳实践/分布式/报告/属性）；补全 JMX XML 片段参考（45+ 组件）
- v1.0.0: 初始版本，支持基础 HTTP 压测全流程

