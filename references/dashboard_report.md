# JMeter HTML 仪表板报告生成

基于 Apache JMeter 官方文档（xdocs/usermanual/generating-dashboard.xml、listeners.xml）整理。

---

## 一、概述

JMeter 支持仪表板报告生成，从测试计划中获取图表和统计数据。默认行为是读取和处理 CSV 文件中的样本，生成包含图表视图的 HTML 文件。可在负载测试结束后生成或按需生成。

### 报告提供的指标

- **APDEX 表**：根据可配置的满意和容忍阈值计算每个事务的 APDEX
- **请求摘要图**：成功和失败请求百分比
- **统计表**：每个事务的所有指标摘要，包括 3 个可配置百分位数
- **错误表**：所有错误及其在总请求中的比例
- **Top 5 错误表**：每个采样器的 Top 5 错误
- **可缩放图表**（可勾选/取消显示每个事务）：
  - 响应时间随时间变化
  - 响应时间百分位数随时间变化
  - 活跃线程随时间变化
  - 字节吞吐量随时间变化
  - 延迟随时间变化
  - 连接时间随时间变化
  - 每秒点击数
  - 每秒响应码
  - 每秒事务数
  - 响应时间 vs 每秒请求数
  - 延迟 vs 每秒请求数
  - 响应时间概览
  - 响应时间百分位数
  - 时间 vs 线程
  - 响应时间分布

---

## 二、配置要求

### Save Service 配置

CSV 文件必须包含以下数据（在 `user.properties` 中配置）：

```properties
jmeter.save.saveservice.bytes = true
jmeter.save.saveservice.label = true
jmeter.save.saveservice.latency = true
jmeter.save.saveservice.response_code = true
jmeter.save.saveservice.response_message = true
jmeter.save.saveservice.successful = true
jmeter.save.saveservice.thread_counts = true
jmeter.save.saveservice.thread_name = true
jmeter.save.saveservice.time = true
jmeter.save.saveservice.connect_time = true
jmeter.save.saveservice.assertion_results_failure_message = true
jmeter.save.saveservice.timestamp_format = ms
```

### Transaction Controller 配置

- 取消勾选 "Generate parent sample"（默认配置）
- 若只想在报告中显示 Transaction Controller，右键节点并 Apply Naming Policy

### 过滤配置

```properties
jmeter.reportgenerator.exporter.html.series_filter=^(Search|Order)(-success|-failure)?$
```

---

## 三、报告生成方式

### 从现有 CSV 日志文件生成

```bash
jmeter -g <log file> -o <Path to output folder>
```

### 负载测试后自动生成

```bash
jmeter -n -t <test JMX file> -l <test log file> -e -o <Path to output folder>
```

### 通过 GUI 工具菜单

Tools -> Generate HTML report，需指定结果文件、user.properties 文件和输出目录。

超时时间由 `generate_report_ui.generation_timeout` 控制（默认 300000ms）。

---

## 四、通用设置

前缀：`jmeter.reportgenerator.`

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `report_title` | "Apache JMeter Dashboard" | 报告标题 |
| `date_format` | `yyyyMMddHHmmss` | 日期格式（SimpleDateFormat） |
| `start_date` | 无 | 数据起始日期 |
| `end_date` | 无 | 数据结束日期 |
| `overall_granularity` | `60000` | 时间图表粒度（毫秒），必须 > 1000 |
| `apdex_satisfied_threshold` | `500` | APDEX 满意阈值（毫秒） |
| `apdex_tolerated_threshold` | `1500` | APDEX 容忍阈值（毫秒） |
| `apdex_per_transaction` | 无 | 为特定样本设置 APDEX 阈值 |
| `sample_filter` | "" | 样本过滤正则表达式 |
| `temp_dir` | `temp` | 临时目录 |
| `statistic_window` | `20000` | 百分位数评估滑动窗口大小 |

### APDEX 事务级配置

格式：`sample_name:satisfaction|tolerance[;]`

```properties
jmeter.reportgenerator.apdex_per_transaction=sample1:100|500;sample2:200|800
```

### 百分位数属性

| 属性 | 默认值 |
|------|--------|
| `aggregate_rpt_pct1` | 90 |
| `aggregate_rpt_pct2` | 95 |
| `aggregate_rpt_pct3` | 99 |

### 百分位数估算器

仪表板使用与聚合报告不同的公式。若需一致，设置：

```properties
backend_metrics_percentile_estimator=R_3
```

---

## 五、图表设置

前缀：`jmeter.reportgenerator.graph.<graph_id>.`

### 通用属性

| 属性 | 说明 |
|------|------|
| `classname`（必填） | 图表类的完全限定名，必须继承 AbstractGraphConsumer |
| `exclude_controllers` | 是否丢弃控制器样本（默认 false） |
| `title` | 图表标题 |

### 特定属性

前缀 `jmeter.reportgenerator.graph.<graph_id>.property`，属性名通过驼峰转换映射到方法调用。

例如 `set_granularity=150` 会调用 `setGranularity(150)`。

### 默认图表类

| 图表类 | 说明 | 支持控制器区分 |
|--------|------|----------------|
| ActiveThreadsGraphConsumer | 活跃线程数随时间变化 | 否 |
| BytesThroughputGraphConsumer | 收发数据吞吐量随时间变化 | 否 |
| CodesPerSecondGraphConsumer | 响应码速率随时间变化 | 否 |
| HitsPerSecondGraphConsumer | 完成请求速率随时间变化 | 否 |
| LatencyOverTimeGraphConsumer | 平均延迟随时间变化 | 是 |
| ConnectTimeOverTimeGraphConsumer | 连接时间随时间变化 | 是 |
| LatencyVSRequestGraphConsumer | 中位数和平均延迟 vs 请求数 | 否 |
| ResponseTimeDistributionGraphConsumer | 响应时间分布 | 是 |
| ResponseTimeOverTimeGraphConsumer | 平均响应时间随时间变化 | 是 |
| ResponseTimePercentilesGraphConsumer | 响应时间百分位数 | 是 |
| ResponseTimePercentilesOverTimeGraphConsumer | Min/Max 和 3 个百分位数响应时间随时间变化 | 是 |
| ResponseTimeVSRequestGraphConsumer | 中位数和平均响应时间 vs 请求数 | 否 |
| TimeVSThreadGraphConsumer | 平均响应时间 vs 活跃线程数 | 是 |
| TransactionsPerSecondGraphConsumer | 每秒事务速率 | 是 |

### 自定义图表

在 `user.properties` 中配置自定义图表，使用 `custom_` 前缀：

```properties
jmeter.reportgenerator.graph.custom_<your_graph_name_id>.classname=org.apache.jmeter.report.processor.graph.impl.CustomGraphConsumer
```

必填属性：
- `set_X_Axis`：X 轴名称
- `set_Y_Axis`：Y 轴名称
- `set_Content_Message`：悬停提示消息
- `set_Sample_Variable_Name`：CSV 中要绘制的列名

---

## 六、导出设置

前缀：`jmeter.reportgenerator.exporter.<exporter_id>.`

### 通用属性

| 属性 | 说明 |
|------|------|
| `classname`（必填） | 必须实现 DataExporter 接口 |
| `filters_only_sample_series` | series_filter 是否仅应用于样本系列（默认 true） |
| `series_filter` | 系列过滤正则表达式，应以 `(-success\|-failure)?$` 结尾 |
| `show_controllers_only` | 是否仅显示控制器系列（默认 false） |

### HTML 导出特定属性

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `output_dir` | `report-output` | 输出目录 |
| `template_dir` | `report-template` | 模板目录 |

### 图表属性

前缀：`jmeter.reportgenerator.exporter.<exporter_id>.graph_options.<graph_id>`

| 属性 | 说明 |
|------|------|
| `minX`/`maxX` | 横轴最小/最大值 |
| `minY`/`maxY` | 纵轴最小/最大值 |

---

## 七、JTL 文件格式

### CSV 格式

列的固定顺序：

| 序号 | 字段名 | 说明 |
|------|--------|------|
| 1 | timeStamp | 毫秒时间戳 |
| 2 | elapsed | 经过时间（毫秒） |
| 3 | label | 采样器标签 |
| 4 | responseCode | 响应码 |
| 5 | responseMessage | 响应消息 |
| 6 | threadName | 线程名 |
| 7 | dataType | 数据类型 |
| 8 | success | 成功标志 |
| 9 | failureMessage | 失败消息 |
| 10 | bytes | 字节数 |
| 11 | sentBytes | 发送字节数 |
| 12 | grpThreads | 本线程组活跃线程数 |
| 13 | allThreads | 所有组总活跃线程数 |
| 14 | URL | 请求 URL |
| 15 | Filename | Save Response to File 使用的文件名 |
| 16 | latency | 延迟 |
| 17 | connect | 连接时间 |
| 18 | encoding | 编码 |
| 19 | SampleCount | 样本数 |
| 20 | ErrorCount | 错误数 |
| 21 | Hostname | 生成样本的主机名 |
| 22 | IdleTime | 空闲时间 |
| 23 | Variables | 指定的变量 |

### XML 格式

样本节点名为 `sample`（非 HTTP）或 `httpSample`（HTTP）。

| XML 属性 | 含义 |
|----------|------|
| `by` | 字节数 |
| `sby` | 发送字节数 |
| `de` | 数据编码 |
| `dt` | 数据类型 |
| `ec` | 错误计数 |
| `hn` | 主机名 |
| `it` | 空闲时间 |
| `lb` | 标签 |
| `lt` | 延迟 |
| `ct` | 连接时间 |
| `na` | 所有线程组活跃线程数 |
| `ng` | 本组活跃线程数 |
| `rc` | 响应码 |
| `rm` | 响应消息 |
| `s` | 成功标志 |
| `sc` | 样本计数 |
| `t` | 经过时间 |
| `tn` | 线程名 |
| `ts` | 时间戳 |

---

## 八、监听器保存配置

### 默认保存项

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `output_format` | csv | 输出格式 |
| `assertion_results_failure_message` | true | 保存断言失败消息 |
| `assertion_results` | none | 断言结果（none/first/all） |
| `data_type` | true | 保存数据类型 |
| `label` | true | 保存标签 |
| `response_code` | true | 保存响应码 |
| `response_data` | false | 保存响应数据 |
| `response_data.on_error` | false | 保存失败样本的响应数据 |
| `response_message` | true | 保存响应消息 |
| `successful` | true | 保存成功标志 |
| `thread_name` | true | 保存线程名 |
| `time` | true | 保存响应时间 |
| `latency` | true | 保存延迟 |
| `connect_time` | false | 保存连接时间 |
| `bytes` | true | 保存字节数 |
| `sent_bytes` | true | 保存发送字节数 |
| `url` | false | 保存 URL |
| `thread_counts` | true | 保存线程计数 |
| `idle_time` | true | 保存空闲时间 |
| `timestamp_format` | ms | 时间戳格式 |
| `default_delimiter` | `,` | CSV 分隔符 |
| `print_field_names` | true | CSV 首行打印字段名 |
| `sample_variables` | - | 额外保存的 JMeter 变量列表 |
| `autoflush` | false | 每行写入后自动刷新（影响性能） |

### 时间戳格式

设为 `ms` 时，若列无法解析为长整数，JMeter 2.9+ 会尝试以下格式：
- `yyyy/MM/dd HH:mm:ss.SSS`
- `yyyy/MM/dd HH:mm:ss`
- `yyyy-MM-dd HH:mm:ss.SSS`
- `yyyy-MM-dd HH:mm:ss`
- `MM/dd/yy HH:mm:ss`

### 资源使用建议

**最小化内存建议**：使用 Simple Data Writer + CSV 格式。

保留每个样本副本的监听器（大量样本时消耗大量内存）：
- View Results Tree
- View Results in Table
- Assertion Results
- Graph Results

不保留副本的监听器（推荐用于负载测试）：
- Simple Data Writer
- BeanShell/JSR223 Listener
- Mailer Visualizer
- Summary Report

聚合后不保留每个样本的监听器：
- Aggregate Report
- Aggregate Graph
