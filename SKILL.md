---
name: "jmeter-loader-skills"
description: "Automates JMeter load testing: JMX generation (template + dynamic build), test execution, result parsing, and optimization. Invoke when user needs JMeter/performance/load testing."
---

# JMeter 压测自动化技能

🚀 版本: 2.0.0

## 技能概述

本技能提供企业级 JMeter 压测全流程自动化能力，实现从测试计划生成到性能优化建议的完整闭环。基于 Apache JMeter 官方文档（5.x）构建，涵盖 129 个组件、49 个内置函数、分布式测试、HTML 报告生成等完整知识体系。

## 触发条件

当用户提到以下关键词时触发此技能：

- JMeter 压测、JMeter 测试
- 性能测试、负载测试、压力测试
- JMX 文件生成
- 压测结果分析
- 性能优化建议
- 分布式压测
- HTML 报告生成
- JMeter 函数、组件配置
- JMeter 属性调优

## 参考文档索引

| 文档                                   | 说明                         |
| ------------------------------------ | -------------------------- |
| `references/component_reference.md`  | JMeter 全部 129 个组件参考（9 大类）  |
| `references/functions_reference.md`  | JMeter 全部 49 个内置函数参考（8 大类） |
| `references/best_practices.md`       | 最佳实践、测试计划结构、术语表            |
| `references/distributed_testing.md`  | 分布式测试完整指南                  |
| `references/dashboard_report.md`     | HTML 仪表板报告生成、JTL 格式        |
| `references/properties_reference.md` | 性能测试关键属性参考（20 大类）          |
| `references/jmx_structure.md`        | JMX XML 结构参考               |
| `references/sampler_types.md`        | Sampler 类型配置说明             |

## 工作流程

### 步骤 1：需求收集与分析

**输入**：用户提供的压测需求描述
**处理**：

1. 提取目标服务信息（主机、端口、协议）
2. 确认并发策略（并发数、ramp-up 时间、持续时间）
3. 识别请求类型（HTTP、JDBC、TCP 等）
4. 收集请求参数和业务流程
   **输出**：标准化的压测参数配置

**关键参数提取**：

- `target_host`: 目标主机地址
- `target_port`: 目标端口
- `protocol`: 协议类型（http/https）
- `concurrency`: 并发用户数
- `rampup`: ramp-up 时间（秒）
- `duration`: 压测持续时间（秒）
- `request_path`: 请求路径
- `method`: HTTP 方法（GET/POST/PUT/DELETE）
- `headers`: 请求头
- `body`: 请求体

### 步骤 2：JMX 测试计划生成

**输入**：标准化的压测参数
**处理**：
1. 根据需求选择生成模式（模板模式或动态组装模式）
2. 模板模式：选择合适的预置模板，参数替换后输出
3. 动态组装模式：根据组件列表从零构建 JMX（推荐用于复杂场景）
4. 验证 JMX 结构完整性
**输出**：完整可执行的 JMX 测试计划文件

**两种生成模式**：

| 模式 | 适用场景 | 命令示例 |
|------|----------|----------|
| 模板模式 | 需求匹配预置模板 | `python generate_jmx.py --template base.jmx --output test.jmx --param ...` |
| 动态组装 | 多接口、自定义组件组合 | `python generate_jmx.py --build --output test.jmx --http-sampler ...` |

**动态组装模式支持的组件**（8 大类 24 种）：

| 类别 | 组件 |
|------|------|
| Samplers | http_sampler, debug_sampler |
| Controllers | if_controller, transaction_controller, once_only_controller, loop_controller, foreach_controller |
| Timers | constant_timer, gaussian_timer, uniform_timer, synchronizing_timer |
| Extractors | json_extractor, boundary_extractor, regex_extractor |
| Assertions | response_assertion, duration_assertion, json_assertion |
| Config | http_defaults, header_manager, cookie_manager, cache_manager, csv_data_set |
| Processors | jsr223_postprocessor, jsr223_preprocessor |
| Listeners | result_collector, backend_listener_influxdb |

**动态组装示例**：
```bash
python generate_jmx.py --build --output test.jmx \
  --param target_host=api.example.com \
  --http-sampler name=GetUsers,path=/api/users,method=GET \
  --http-sampler name=CreateOrder,path=/api/orders,method=POST,body='{"item":"test"}' \
  --timer timer_type=gaussian,delay_ms=300,range_ms=100 \
  --assertion type=response,patterns=200 \
  --backend-listener type=influxdb,influxdb_url=http://localhost:8086
```

**JMX 生成规范**：

1. **参数化要求**：
   - 所有可变参数使用 `${__P(propname,default)}` 形式
   - 标准参数名：
     - `concurrency`: 并发用户数（默认值根据需求）
     - `rampup`: ramp-up 时间（秒，默认：10）
     - `duration`: 压测持续时间（秒，默认：60）
     - `target_host`: 目标主机
     - `target_port`: 目标端口
     - `target_path`: 请求路径
     - `method`: HTTP 方法
2. **必需组件**：
   - **ThreadGroup（线程组）**：
     - `num_threads`: `${__P(concurrency,10)}`
     - `ramp_time`: `${__P(rampup,10)}`
     - `scheduler`: `true`
     - `duration`: `${__P(duration,60)}`
     - `on_sample_error`: `continue`
   - **ResultCollector（结果收集器）**：
     - 配置为保存 .jtl 格式结果
     - 启用所有必需字段：timeStamp, elapsed, label, responseCode, responseMessage, threadName, dataType, success, failureMessage, bytes, sentBytes, grpThreads, allThreads, URL, Latency, IdleTime, Connect
3. **支持的 Sampler 类型**：
   - HTTP Request Sampler（默认）
   - JDBC Request Sampler
   - TCP Sampler
   - Java Request Sampler
   - FTP Request Sampler
   - SMTP Sampler
   - LDAP Request Sampler
   - JMS Publisher/Subscriber/Point-to-Point
   - OS Process Sampler
   - JSR223 Sampler
   - Bolt Request（Neo4j）
4. **组件选择指南**：
   | 需求场景     | 推荐组件                                                               |
   | -------- | ------------------------------------------------------------------ |
   | API 接口压测 | HTTP Request + HTTP Header Manager                                 |
   | 数据库压测    | JDBC Request + JDBC Connection Configuration                       |
   | 需要鉴权的接口  | HTTP Request + HTTP Cookie Manager + JSON Extractor                |
   | 数据驱动测试   | HTTP Request + CSV Data Set Config                                 |
   | 业务流程压测   | Transaction Controller + Once Only Controller                      |
   | 条件分支     | If Controller（使用 `${__jexl3()}`）                                   |
   | 循环遍历     | ForEach Controller + Regular Expression Extractor                  |
   | 并发同步     | Synchronizing Timer                                                |
   | 思考时间     | Gaussian Random Timer / Uniform Random Timer                       |
   | 吞吐量控制    | Precise Throughput Timer                                           |
   | 响应验证     | Response Assertion / JSON Assertion / Duration Assertion           |
   | 数据提取     | JSON Extractor / Boundary Extractor / Regular Expression Extractor |
   | 实时监控     | Backend Listener（Graphite/InfluxDB）                                |

### 步骤 3：压测执行与监控

**输入**：生成的 JMX 文件路径、可选的运行时参数
**处理**：

1. 检查 JMeter 环境（版本 5.4+）
2. 构建 JMeter CLI 命令
3. 执行压测（支持分布式压测）
4. 实时监控执行状态
5. 处理执行错误和异常
   **输出**：JTL 结果文件、JMeter 日志文件

**JMeter 执行命令规范**：

1. **基础命令格式**：
   ```bash
   jmeter -n -t ${jmx_file_path} -l ${result_jtl_path} -j ${jmeter_log_path}
   ```
2. **参数覆写格式**：
   ```bash
   jmeter -n -t test.jmx -l result.jtl -j jmeter.log \
     -Jconcurrency=50 \
     -Jrampup=60 \
     -Jduration=300
   ```
3. **分布式压测配置**：
   ```bash
   jmeter -n -t test.jmx -l result.jtl -r -R slave1,slave2,slave3
   ```
4. **命令参数说明**：
   - `-n`: 非 GUI 模式运行
   - `-t`: 指定 JMX 文件路径
   - `-l`: 指定结果文件（JTL）路径
   - `-j`: 指定日志文件路径
   - `-J`: 设置 JMeter 属性（覆盖 JMX 中的参数）
   - `-G`: 在所有服务器上定义属性（分布式模式）
   - `-r`: 启动远程服务器
   - `-R`: 指定远程服务器列表
   - `-X`: 测试结束后退出远程服务器
   - `-q`: 加载额外属性文件
   - `-e`: 测试结束后生成 HTML 报告
   - `-o`: HTML 报告输出目录
5. **环境检查**：
   - 执行前检查 `jmeter --version` 确认版本 >= 5.4
   - 验证 JMX 文件存在且格式正确
   - 确认输出目录有写入权限
6. **HTML 报告生成**：
   ```bash
   # 测试后自动生成
   jmeter -n -t test.jmx -l result.jtl -e -o report/

   # 从已有 JTL 生成
   jmeter -g result.jtl -o report/
   ```

### 步骤 4：结果解析与报告生成

**输入**：JTL 结果文件路径
**处理**：

1. 读取并解析 JTL 文件（CSV 或 XML 格式）
2. 计算核心性能指标
3. 生成多维度分析报告
4. 检测性能异常
   **输出**：结构化的性能报告、异常检测结果

**结果解析规范**：

1. **核心聚合指标**：
   - **Average（平均响应时间）**: 所有请求的平均响应时间（毫秒）
   - **TP90（90% 响应时间）**: 90% 的请求在此时间内完成（毫秒）
   - **TP95（95% 响应时间）**: 95% 的请求在此时间内完成（毫秒）
   - **TP99（99% 响应时间）**: 99% 的请求在此时间内完成（毫秒）
   - **Min（最小响应时间）**: 最快的请求响应时间（毫秒）
   - **Max（最大响应时间）**: 最慢的请求响应时间（毫秒）
   - **Error%（错误率）**: 失败请求占总请求的百分比
   - **Throughput（吞吐量）**: 每秒处理的请求数（requests/sec）
   - **Received KB/sec**: 每秒接收的数据量
   - **Sent KB/sec**: 每秒发送的数据量
2. **多维度分析**：
   - **按请求标签分组**: 分析每个接口的性能表现
   - **时间趋势分析**: 响应时间和吞吐量随时间的变化趋势
   - **错误类型统计**: 统计不同错误类型的分布
   - **并发与响应时间关系**: 分析并发数对响应时间的影响
3. **JTL 文件格式**：
   - 默认使用 CSV 格式，字段顺序：
     timeStamp,elapsed,label,responseCode,responseMessage,
     threadName,dataType,success,failureMessage,bytes,
     sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
4. **JMeter 术语说明**：
   - **Elapsed Time**: 从发送请求前到接收最后一个响应后的时间（不含渲染和 JS 执行）
   - **Latency**: 从发送请求前到接收第一个响应后的时间
   - **Connect Time**: 建立连接所需时间（含 SSL 握手），不会从 Latency 中减去
   - **Throughput**: 请求数 / 总时间（从第一个样本到最后一个样本）

### 步骤 5：优化建议提供

**输入**：性能报告、异常检测结果
**处理**：

1. 评估系统性能瓶颈
2. 分析根本原因
3. 提供针对性优化建议
4. 制定迭代优化方案
   **输出**：详细的优化建议报告

**性能评估标准**：

| 指标        | 优秀      | 良好      | 一般   | 需优化   |
| --------- | ------- | ------- | ---- | ----- |
| 平均响应时间    | < 200ms | < 500ms | < 1s | >= 1s |
| TP90 响应时间 | < 500ms | < 1s    | < 2s | >= 2s |
| 错误率       | < 0.1%  | < 1%    | < 5% | >= 5% |
| 吞吐量       | 达到目标    | 接近目标    | 低于目标 | 远低于目标 |

**优化建议分类**：

1. **服务器配置优化**：
   - 增加服务器 CPU/内存资源
   - 优化数据库连接池配置
   - 调整 JVM 参数（堆大小、垃圾回收）
   - 启用缓存机制（Redis、Memcached）
2. **接口性能优化**：
   - SQL 语句优化（添加索引、避免全表扫描）
   - 减少不必要的数据库查询
   - 接口合并减少网络往返
   - 异步处理非核心业务逻辑
3. **并发策略优化**：
   - 调整 ramp-up 时间避免瞬时压力
   - 实施阶梯式并发递增
   - 识别系统瓶颈并设置合理并发上限
   - 考虑使用分布式压测
4. **架构级优化**：
   - 引入负载均衡
   - 实施读写分离
   - 考虑微服务拆分
   - 引入 CDN 加速静态资源
5. **JMeter 测试计划优化**：
   - 使用 CLI 模式运行
   - 减少监听器数量（负载测试时禁用 View Results Tree）
   - 使用 CSV 格式而非 XML 格式存储结果
   - 使用 Groovy 脚本（JSR223）替代 BeanShell
   - 勾选"Cache compiled script if available"
   - 脚本中使用 `vars.get()` 而非 `${varName}` 以确保缓存有效
   - 使用 CSV Data Set 替代大量相似采样器
   - 只保存需要的数据字段

## 脚本使用指南

### generate\_jmx.py

用于根据参数动态生成 JMX 文件。

**用法**：

```bash
python generate_jmx.py --template base.jmx --output test.jmx \
  --param target_host=example.com \
  --param target_port=80 \
  --param concurrency=50 \
  --param duration=300
```

**参数**：

- `--template`: 模板文件名（位于 assets/templates/）
- `--output`: 输出 JMX 文件路径
- `--param`: 参数键值对，可多次使用

### run\_jmeter.py

用于执行 JMeter 压测并管理进程。

**用法**：

```bash
python run_jmeter.py --jmx test.jmx --result result.jtl \
  --log jmeter.log \
  --param concurrency=100 \
  --param duration=600
```

**参数**：

- `--jmx`: JMX 文件路径
- `--result`: 结果文件路径
- `--log`: 日志文件路径
- `--param`: 运行时参数
- `--distributed`: 启用分布式压测
- `--remote-hosts`: 远程服务器列表

### parse\_jtl.py

用于解析 JTL 结果文件并生成报告。

**用法**：

```bash
python parse_jtl.py --jtl result.jtl --output report.json \
  --format json --charts
```

**参数**：

- `--jtl`: JTL 文件路径
- `--output`: 输出报告路径
- `--format`: 输出格式（json, html, csv）
- `--charts`: 生成图表（需要 matplotlib）

## 模板使用说明

### base.jmx（基础 HTTP 模板）

适用于简单的 HTTP 接口压测，包含：
- 标准线程组配置
- HTTP 请求采样器
- 结果收集器
- 简单的定时器配置

**适用场景**：单接口压测、简单负载测试

### csv_data.jmx（CSV 数据源模板）

适用于需要从 CSV 读取测试数据的场景，包含：
- CSV 数据集配置
- 参数化 HTTP 请求
- 循环控制器

**适用场景**：多用户登录、参数化请求、数据驱动测试

### auth_flow.jmx（带鉴权的业务流程模板）

适用于需要鉴权的业务流程压测，包含：
- 登录请求（获取 Token）
- Token 提取器
- 带认证头的业务请求
- Cookie 管理器

**适用场景**：需要登录的接口、Token 刷新流程、完整业务链路

### multi_api.jmx（多接口混合压测模板）

适用于多个 API 端点的混合压测，包含：
- 3 个 HTTP 请求采样器（GET/POST 混合）
- 每个请求的 JSON 数据提取器
- 接口间数据串联（user_id → order_id）
- Response Assertion 断言
- InfluxDB Backend Listener（默认禁用）

**适用场景**：多接口混合压测、接口间数据依赖、API 链路测试

### staged_load.jmx（阶梯加压模板）

适用于阶梯式负载测试，包含：
- 3 个顺序执行的 Thread Group（低→中→高负载）
- 每阶段独立的并发数和持续时间配置
- Duration Assertion 响应时间断言
- InfluxDB Backend Listener 实时监控

**适用场景**：性能拐点探测、容量规划、阶梯加压测试

### jdbc_test.jmx（JDBC 数据库压测模板）

适用于数据库性能测试，包含：
- JDBC Connection Configuration 连接池配置
- 3 个 JDBC 采样器（Select/Insert/Update）
- Prepared Statement 参数绑定
- MySQL 驱动默认配置

**适用场景**：数据库性能测试、SQL 压力测试、连接池调优

### business_flow.jmx（业务流程模板）

适用于完整业务流程的事务级压测，包含：
- Once Only Controller（登录仅执行一次）
- 4 个 Transaction Controller（浏览→加购→结算→支付）
- 接口间数据提取与传递（auth_token → product_id → cart_id → order_id）
- If Controller 条件判断
- Debug Sampler 调试

**适用场景**：电商下单流程、多步骤事务、端到端业务链路压测

## JMeter 内置函数速查

### 常用函数

| 函数               | 语法                                    | 用途                          |
| ---------------- | ------------------------------------- | --------------------------- |
| `__P`            | `${__P(prop,default)}`                | 读取属性（命令行覆盖）                 |
| `__property`     | `${__property(prop,var,default)}`     | 读取属性（完整版）                   |
| `__setProperty`  | `${__setProperty(prop,value,)}`       | 设置属性（线程间通信）                 |
| `__time`         | `${__time(format,)}`                  | 获取当前时间                      |
| `__timeShift`    | `${__timeShift(format,date,shift,,)}` | 时间偏移                        |
| `__Random`       | `${__Random(min,max,)}`               | 随机整数                        |
| `__RandomString` | `${__RandomString(len,chars,)}`       | 随机字符串                       |
| `__UUID`         | `${__UUID()}`                         | 生成 UUID                     |
| `__counter`      | `${__counter(TRUE,)}`                 | 递增计数器                       |
| `__V`            | `${__V(Var${N},)}`                    | 嵌套变量引用                      |
| `__groovy`       | `${__groovy(expr,)}`                  | Groovy 脚本                   |
| `__jexl3`        | `${__jexl3(expr,)}`                   | JEXL3 表达式（If Controller 推荐） |
| `__digest`       | `${__digest(algo,str,,,)}`            | 哈希摘要                        |
| `__split`        | `${__split(str,var,delim)}`           | 字符串拆分                       |
| `__eval`         | `${__eval(${var})}`                   | 表达式求值                       |
| `__log`          | `${__log(msg,level,,)}`               | 日志记录                        |
| `__threadNum`    | `${__threadNum}`                      | 当前线程号                       |
| `__machineIP`    | `${__machineIP}`                      | 本机 IP                       |

### 脚本语言性能排序

**Groovy（JSR223 + 缓存）> JEXL3 > JavaScript > BeanShell**

关键：使用 JSR223 元素时务必勾选 "Cache compiled script if available"，且脚本内使用 `vars.get("varName")` 而非 `${varName}`。

## JMeter 组件速查

### 执行顺序

1. Configuration elements → 2. Pre-Processors → 3. Timers → 4. Sampler → 5. Post-Processors → 6. Assertions → 7. Listeners

### 作用域规则

- 层次型元素（Listeners、Config、Post/Pre-Processors、Assertions、Timers）：应用于其父元素及所有后代
- 有序型元素（Controllers、Samplers）：按树中出现的顺序处理
- Manager 类元素（Header/Cookie/Authorization Manager）不合并，只使用一个

### 常用控制器

| 控制器                         | 用途                          |
| --------------------------- | --------------------------- |
| If Controller               | 条件分支（推荐 `${__jexl3()}` 表达式） |
| While Controller            | 循环直到条件为 false               |
| ForEach Controller          | 遍历变量组                       |
| Transaction Controller      | 测量事务总耗时                     |
| Once Only Controller        | 仅执行一次（如登录）                  |
| Loop Controller             | 循环执行                        |
| Throughput Controller       | 控制执行频率                      |
| Critical Section Controller | 线程互斥锁                       |
| Module Controller           | 引用测试片段                      |
| Include Controller          | 引用外部 JMX                    |

### 常用提取器

| 提取器                          | 适用场景                   |
| ---------------------------- | ---------------------- |
| JSON Extractor               | JSON 响应提取（JSON Path）   |
| JSON JMESPath Extractor      | JSON 响应提取（JMESPath）    |
| Boundary Extractor           | 简单边界提取（无需正则）           |
| Regular Expression Extractor | 通用正则提取                 |
| CSS Selector Extractor       | HTML 提取（CSS 选择器）       |
| XPath2 Extractor             | XML/HTML 提取（XPath2，推荐） |

### 常用断言

| 断言                      | 用途           |
| ----------------------- | ------------ |
| Response Assertion      | 响应码/消息/文本断言  |
| JSON Assertion          | JSON Path 断言 |
| JSON JMESPath Assertion | JMESPath 断言  |
| Duration Assertion      | 响应时间断言       |
| Size Assertion          | 响应大小断言       |
| XPath2 Assertion        | XML 断言（推荐）   |

### 常用定时器

| 定时器                      | 特点        |
| ------------------------ | --------- |
| Constant Timer           | 固定延迟      |
| Gaussian Random Timer    | 高斯分布随机延迟  |
| Uniform Random Timer     | 均匀分布随机延迟  |
| Precise Throughput Timer | 精确吞吐量控制   |
| Synchronizing Timer      | 并发同步（集合点） |
| Poisson Random Timer     | 泊松分布随机延迟  |

## 分布式压测指南

### 配置步骤

1. 所有节点运行**相同版本**的 JMeter 和 Java
2. 在每台 Slave 上启动 `jmeter-server`
3. 在 Master 的 `jmeter.properties` 配置 `remote_hosts`
4. 使用 `-r` 或 `-R` 参数执行分布式测试

### 重要提示

- 所有服务器运行相同的测试计划，JMeter **不会**分配负载
- N 台服务器 × M 线程 = N×M 总线程数
- 数据文件不会自动分发，需手动复制到每台服务器
- 推荐使用 `StrippedBatch` 模式减少网络开销

### 命令示例

```bash
# 启动所有远程服务器
jmeter -n -t test.jmx -l result.jtl -r

# 指定服务器
jmeter -n -t test.jmx -l result.jtl -R slave1,slave2

# 传递属性到所有服务器
jmeter -n -t test.jmx -l result.jtl -r \
  -Gconcurrency=100 -Gduration=300

# 测试后退出远程服务器
jmeter -n -t test.jmx -l result.jtl -r -X
```

## HTML 报告生成

### 生成方式

```bash
# 从已有 JTL 生成
jmeter -g result.jtl -o report/

# 测试后自动生成
jmeter -n -t test.jmx -l result.jtl -e -o report/
```

### 关键配置

```properties
# APDEX 阈值
jmeter.reportgenerator.apdex_satisfied_threshold=500
jmeter.reportgenerator.apdex_tolerated_threshold=1500

# 时间粒度
jmeter.reportgenerator.overall_granularity=60000

# 百分位数
aggregate_rpt_pct1=90
aggregate_rpt_pct2=95
aggregate_rpt_pct3=99
```

### JTL 必需字段

为生成完整报告，CSV 文件必须包含：
bytes, label, latency, response\_code, response\_message, successful, thread\_counts, thread\_name, time, connect\_time, assertion\_results\_failure\_message, timestamp\_format=ms

## 安全注意事项

1. **敏感信息处理**：
   - 密码、Token 等敏感信息使用 JMeter 内置加密
   - 使用 `${__property(variable)}` 从外部传入敏感数据
   - 避免在 JMX 文件中硬编码密码
2. **访问控制**：
   - 压测目标需获得授权
   - 避免在生产环境进行未经授权的压测
   - 控制压测强度避免影响正常业务
3. **数据保护**：
   - 压测数据应使用测试数据而非真实数据
   - 结果文件包含敏感信息需妥善处理
   - 日志文件避免记录敏感信息
4. **分布式安全**：
   - RMI 默认使用 SSL，确保密钥库正确配置
   - 不在应用服务器上运行 JMeterEngine
   - 可通过 Java 安全管理器限制远程操作

## 环境要求

- **JMeter 版本**: 5.4 或更高
- **Python 版本**: 3.7 或更高
- **Python 依赖**:
  - jinja2（用于模板渲染）
  - pandas（用于数据处理，可选）
  - matplotlib（用于图表生成，可选）
- **操作系统**: Windows、Linux、macOS

## 常见问题

### Q1: JMX 文件生成后无法运行？

A: 检查以下几点：

- 确认 JMeter 版本兼容性（5.4+）
- 检查 XML 格式是否正确
- 验证所有引用的组件是否存在

### Q2: 压测执行时报内存不足？

A: 优化方案：

- 调整 JMeter 堆大小：`HEAP="-Xms1g -Xmx4g -XX:MaxMetaspaceSize=256m"`
- 使用分布式压测分散负载
- 减少监听器数量
- 使用 CLI 模式运行

### Q3: 结果文件解析失败？

A: 可能原因：

- JTL 文件格式不完整（压测异常中断）
- 缺少必要字段
- 文件编码问题
- 使用 `parse_jtl.py --verbose` 查看详细错误信息

### Q4: 如何进行分布式压测？

A: 配置步骤：

1. 在所有 slave 机器启动 `jmeter-server`
2. 在 master 机器的 `jmeter.properties` 配置 `remote_hosts`
3. 使用 `run_jmeter.py --distributed` 执行
4. 确保所有机器时钟同步
5. 确保所有节点运行相同版本的 JMeter 和 Java
6. 数据文件需手动复制到每台服务器

### Q5: JSR223 脚本缓存后变量值不更新？

A: 使用脚本缓存时，不要在脚本中使用 `${varName}` 方式引用变量（缓存只会取第一次的值），应改用 `vars.get("varName")`。

### Q6: 如何生成 HTML 报告？

A: 两种方式：

- 测试时自动生成：`jmeter -n -t test.jmx -l result.jtl -e -o report/`
- 从已有 JTL 生成：`jmeter -g result.jtl -o report/`
- 确保 JTL 包含所有必需字段（参见 dashboard\_report.md）

### Q7: BeanShell 和 JSR223 + Groovy 如何选择？

A: 始终选择 JSR223 + Groovy：

- Groovy 支持 Compilable 接口，可缓存编译脚本
- BeanShell 不支持真正的编译，性能差
- 自 JMeter 3.1 起官方推荐 JSR223 + Groovy

## 示例工作流

### 示例 1：简单 HTTP 接口压测

1. **用户需求**：压测 `http://api.example.com/users` 接口，50 并发，持续 5 分钟
2. **生成 JMX**：
   ```bash
   python generate_jmx.py --template base.jmx --output test_api.jmx \
     --param target_host=api.example.com \
     --param target_port=80 \
     --param target_path=/users \
     --param method=GET \
     --param concurrency=50 \
     --param duration=300
   ```
3. **执行压测**：
   ```bash
   python run_jmeter.py --jmx test_api.jmx --result results.jtl --log jmeter.log
   ```
4. **解析结果**：
   ```bash
   python parse_jtl.py --jtl results.jtl --output report.json --format json
   ```
5. **生成 HTML 报告**：
   ```bash
   jmeter -g results.jtl -o html_report/
   ```
6. **优化建议**：根据报告中的 TP90、错误率、吞吐量指标，提供针对性优化建议

### 示例 2：带鉴权的业务流程压测

1. **用户需求**：压测完整下单流程，需要先登录获取 Token，然后创建订单
2. **生成 JMX**：使用 `auth_flow.jmx` 模板，配置登录和下单接口参数
3. **执行并分析**：同上流程

### 示例 3：分布式压测

1. **用户需求**：1000 并发，3 台 JMeter 服务器
2. **配置**：
   ```bash
   # Slave1/2/3 上启动
   ./jmeter-server

   # Master 上执行
   jmeter -n -t test.jmx -l result.jtl -r \
     -Gconcurrency=334 -Gduration=300 \
     -X
   ```
3. **注意**：每台服务器 334 线程，总计约 1002 线程

## 迭代优化机制

当性能测试结果显示需要优化时，按照以下流程进行迭代：

1. **分析瓶颈**：确定是 CPU、内存、IO 还是应用层问题
2. **实施优化**：根据建议选择 1-2 个优化项实施
3. **重新压测**：使用相同的压测配置重新执行
4. **对比结果**：分析优化前后的性能指标变化
5. **持续迭代**：直到达到预期性能目标

## 版本历史

- v2.0.0 (2026-05-17): 基于 JMeter 官方文档全面完善，新增组件参考（129个）、函数参考（49个）、最佳实践、分布式测试指南、HTML 报告生成、属性参考
- v1.0.0 (2026-01-01): 初始版本，支持基础 HTTP 压测全流程

