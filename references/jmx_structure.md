# JMeter JMX XML 结构参考文档

## 概述

JMX 文件是 JMeter 测试计划的 XML 表示形式。了解其结构对于自定义和扩展测试计划至关重要。本文档详细说明 JMeter 5.4+ 版本中 JMX 文件的 XML 结构和各组件的配置方法。

## 基本结构

JMX 文件的基本结构如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.4.1">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="测试计划名称" enabled="true">
      <!-- TestPlan 配置 -->
    </TestPlan>
    <hashTree>
      <!-- ThreadGroup 及其他元素 -->
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

### 根元素说明

| 属性 | 说明 |
|------|------|
| `version` | JMX 文件格式版本，固定为 "1.2" |
| `properties` | 属性版本，JMeter 5.x 使用 "5.0" |
| `jmeter` | 创建此文件的 JMeter 版本 |

## 核心组件

### 1. TestPlan（测试计划）

测试计划是 JMX 文件的顶级容器，包含全局配置。

#### XML 结构

```xml
<TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="MyTestPlan" enabled="true">
  <stringProp name="TestPlan.comments">测试计划注释</stringProp>
  <boolProp name="TestPlan.functional_mode">false</boolProp>
  <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
  <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
  <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
    <collectionProp name="Arguments.arguments"/>
  </elementProp>
  <stringProp name="TestPlan.user_define_classpath"></stringProp>
</TestPlan>
```

#### 配置项说明

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `TestPlan.comments` | string | 测试计划注释 |
| `TestPlan.functional_mode` | bool | 功能测试模式（捕获完整响应数据） |
| `TestPlan.tearDown_on_shutdown` | bool | 关闭时执行 tearDown 线程组 |
| `TestPlan.serialize_threadgroups` | bool | 串行执行线程组 |
| `TestPlan.user_defined_variables` | element | 用户定义的全局变量 |
| `TestPlan.user_define_classpath` | string | 用户自定义 classpath |

---

### 2. ThreadGroup（线程组）

线程组定义了压测的并发策略，是测试执行的核心。

#### XML 结构

```xml
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="线程组" enabled="true">
  <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
  <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
    <boolProp name="LoopController.continue_forever">false</boolProp>
    <intProp name="LoopController.loops">-1</intProp>
  </elementProp>
  <stringProp name="ThreadGroup.num_threads">${__P(concurrency,10)}</stringProp>
  <stringProp name="ThreadGroup.ramp_time">${__P(rampup,10)}</stringProp>
  <boolProp name="ThreadGroup.scheduler">true</boolProp>
  <stringProp name="ThreadGroup.duration">${__P(duration,60)}</stringProp>
  <stringProp name="ThreadGroup.delay"></stringProp>
  <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
</ThreadGroup>
```

#### 配置项说明

| 配置项 | 类型 | 说明 | 参数化示例 |
|--------|------|------|------------|
| `ThreadGroup.on_sample_error` | string | 采样错误时的处理方式 | `continue`, `startnextloop`, `stopthread`, `stoptest`, `stoptestnow` |
| `ThreadGroup.num_threads` | string | 并发用户数（线程数） | `${__P(concurrency,10)}` |
| `ThreadGroup.ramp_time` | string | Ramp-up 时间（秒） | `${__P(rampup,10)}` |
| `ThreadGroup.scheduler` | bool | 是否启用调度器 | `true` |
| `ThreadGroup.duration` | string | 测试持续时间（秒） | `${__P(duration,60)}` |
| `ThreadGroup.delay` | string | 启动延迟（秒） | `${__P(delay,0)}` |
| `LoopController.loops` | int | 循环次数（-1 表示永久） | `-1` |

#### 错误处理策略

| 值 | 说明 |
|----|------|
| `continue` | 继续执行（忽略错误） |
| `startnextloop` | 开始下一循环 |
| `stopthread` | 停止当前线程 |
| `stoptest` | 停止整个测试（等待当前采样完成） |
| `stoptestnow` | 立即停止测试 |

---

### 3. ResultCollector（结果收集器）

结果收集器用于保存测试结果到 JTL 文件。

#### XML 结构

```xml
<ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="查看结果树" enabled="true">
  <boolProp name="ResultCollector.error_logging">false</boolProp>
  <objProp>
    <name>saveConfig</name>
    <value class="SampleSaveConfiguration">
      <time>true</time>
      <latency>true</latency>
      <timestamp>true</timestamp>
      <success>true</success>
      <label>true</label>
      <code>true</code>
      <message>true</message>
      <threadName>true</threadName>
      <dataType>true</dataType>
      <encoding>false</encoding>
      <assertions>true</assertions>
      <subresults>true</subresults>
      <responseData>false</responseData>
      <samplerData>false</samplerData>
      <xml>false</xml>
      <fieldNames>true</fieldNames>
      <responseHeaders>false</responseHeaders>
      <requestHeaders>false</requestHeaders>
      <responseDataOnError>false</responseDataOnError>
      <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
      <assertionsResultsToSave>0</assertionsResultsToSave>
      <bytes>true</bytes>
      <sentBytes>true</sentBytes>
      <url>true</url>
      <threadCounts>true</threadCounts>
      <idleTime>true</idleTime>
      <connectTime>true</connectTime>
    </value>
  </objProp>
  <stringProp name="filename">${__P(result_file,result.jtl)}</stringProp>
</ResultCollector>
```

#### 保存配置说明

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `time` | bool | 保存响应时间 |
| `latency` | bool | 保存延迟时间 |
| `timestamp` | bool | 保存时间戳 |
| `success` | bool | 保存成功状态 |
| `label` | bool | 保存标签 |
| `code` | bool | 保存响应码 |
| `message` | bool | 保存响应消息 |
| `threadName` | bool | 保存线程名 |
| `dataType` | bool | 保存数据类型 |
| `assertions` | bool | 保存断言结果 |
| `bytes` | bool | 保存字节数 |
| `sentBytes` | bool | 保存发送字节数 |
| `url` | bool | 保存 URL |
| `threadCounts` | bool | 保存线程数 |
| `idleTime` | bool | 保存空闲时间 |
| `connectTime` | bool | 保存连接时间 |
| `xml` | bool | 输出格式（false=CSV，true=XML） |
| `fieldNames` | bool | CSV 输出包含字段名 |

> **性能建议**：在高并发压测时，建议将 `responseData`、`samplerData`、`responseHeaders`、`requestHeaders` 设置为 `false`，以减少 I/O 开销。

---

### 4. Config Element（配置元件）

#### HTTP Request Defaults（HTTP 请求默认值）

```xml
<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP请求默认值" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
    <collectionProp name="Arguments.arguments"/>
  </elementProp>
  <stringProp name="HTTPSampler.domain">${__P(target_host,localhost)}</stringProp>
  <stringProp name="HTTPSampler.port">${__P(target_port,80)}</stringProp>
  <stringProp name="HTTPSampler.protocol">${__P(protocol,http)}</stringProp>
  <stringProp name="HTTPSampler.contentEncoding"></stringProp>
  <stringProp name="HTTPSampler.path">${__P(base_path,/)}</stringProp>
  <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
  <boolProp name="HTTPSampler.embedded_url_re">false</boolProp>
</ConfigTestElement>
```

#### HTTP Header Manager（HTTP 头管理器）

```xml
<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP信息头管理器" enabled="true">
  <collectionProp name="HeaderManager.headers">
    <elementProp name="" elementType="Header">
      <stringProp name="Header.name">Content-Type</stringProp>
      <stringProp name="Header.value">application/json</stringProp>
    </elementProp>
    <elementProp name="" elementType="Header">
      <stringProp name="Header.name">Authorization</stringProp>
      <stringProp name="Header.value">Bearer ${auth_token}</stringProp>
    </elementProp>
  </collectionProp>
</HeaderManager>
```

#### CSV Data Set Config（CSV 数据集配置）

```xml
<CSVDataSet guiclass="TestBeanGUI" testclass="CSVDataSet" testname="CSV数据文件设置" enabled="true">
  <stringProp name="delimiter">,</stringProp>
  <stringProp name="fileEncoding"></stringProp>
  <stringProp name="filename">${__P(csv_file,testdata.csv)}</stringProp>
  <boolProp name="ignoreFirstLine">true</boolProp>
  <boolProp name="quotedData">false</boolProp>
  <boolProp name="recycle">true</boolProp>
  <stringProp name="shareMode">shareMode.all</stringProp>
  <boolProp name="stopThread">false</boolProp>
  <stringProp name="variableNames">username,password</stringProp>
</CSVDataSet>
```

---

### 5. Timer（定时器）

#### Constant Timer（固定定时器）

```xml
<ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="固定定时器" enabled="true">
  <stringProp name="ConstantTimer.delay">${__P(think_time,1000)}</stringProp>
</ConstantTimer>
```

#### Uniform Random Timer（均匀随机定时器）

```xml
<UniformRandomTimer guiclass="UniformRandomTimerGui" testclass="UniformRandomTimer" testname="均匀随机定时器" enabled="true">
  <stringProp name="ConstantTimer.delay">1000</stringProp>
  <stringProp name="RandomTimer.range">500</stringProp>
</UniformRandomTimer>
```

#### Gaussian Random Timer（高斯随机定时器）

```xml
<GaussianRandomTimer guiclass="GaussianRandomTimerGui" testclass="GaussianRandomTimer" testname="高斯随机定时器" enabled="true">
  <stringProp name="ConstantTimer.delay">1000</stringProp>
  <stringProp name="RandomTimer.range">300</stringProp>
</GaussianRandomTimer>
```

---

### 6. Assertion（断言）

#### Response Assertion（响应断言）

```xml
<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="响应断言" enabled="true">
  <collectionProp name="Asserter.testStrings">
    <elementProp name="" elementType="string">
      <stringProp name="Argument.value">200</stringProp>
      <stringProp name="Argument.metadata">=</stringProp>
    </elementProp>
  </collectionProp>
  <stringProp name="Assertion.custom_message"></stringProp>
  <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
  <boolProp name="Assertion.assume_success">false</boolProp>
  <intProp name="Assertion.test_type">2</intProp>
</ResponseAssertion>
```

#### JSON Assertion（JSON 断言）

```xml
<JSONPathAssertion guiclass="JSONPathAssertionGui" testclass="JSONPathAssertion" testname="JSON断言" enabled="true">
  <stringProp name="JSON_PATH">$.code</stringProp>
  <stringProp name="EXPECTED_VALUE">200</stringProp>
  <boolProp name="JSONVALIDATION">true</boolProp>
  <boolProp name="EXPECT_NULL">false</boolProp>
  <boolProp name="INVERT">false</boolProp>
  <boolProp name="ISREGEX">false</boolProp>
</JSONPathAssertion>
```

---

### 7. Post Processor（后置处理器）

#### JSON Extractor（JSON 提取器）

```xml
<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="JSON提取器" enabled="true">
  <stringProp name="JSONPostProcessor.referenceNames">auth_token</stringProp>
  <stringProp name="JSONPostProcessor.jsonPathExprs">$.data.token</stringProp>
  <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
  <stringProp name="JSONPostProcessor.default_values">NOT_FOUND</stringProp>
</JSONPostProcessor>
```

#### Regular Expression Extractor（正则表达式提取器）

```xml
<RegexExtractor guiclass="RegexExtractorGui" testclass="RegexExtractor" testname="正则表达式提取器" enabled="true">
  <stringProp name="RegexExtractor.useHeaders">false</stringProp>
  <stringProp name="RegexExtractor.refname">session_id</stringProp>
  <stringProp name="RegexExtractor.regex">"sessionId":"(.+?)"</stringProp>
  <stringProp name="RegexExtractor.template">$1$</stringProp>
  <stringProp name="RegexExtractor.match_number">1</stringProp>
  <stringProp name="RegexExtractor.default">NOT_FOUND</stringProp>
</RegexExtractor>
```

## 完整示例结构

以下是一个完整的 JMX 文件结构示例：

```
jmeterTestPlan (根元素)
└── hashTree
    ├── TestPlan (测试计划)
    └── hashTree
        ├── ThreadGroup (线程组)
        └── hashTree
            ├── ConfigTestElement (HTTP 请求默认值)
            ├── HeaderManager (HTTP 头管理器)
            ├── hashTree (子配置元件的容器)
            ├── HTTPSamplerProxy (HTTP 请求采样器)
            └── hashTree
                ├── ResponseAssertion (响应断言)
                ├── JSONPostProcessor (JSON 提取器)
                └── ResultCollector (结果收集器)
```

## 命名约定

为保持一致性，建议遵循以下命名约定：

### 组件命名

| 组件类型 | 命名前缀 | 示例 |
|----------|----------|------|
| ThreadGroup | TG_ | `TG_API_LoadTest` |
| HTTP Request | HTTP_ | `HTTP_Get_UserInfo` |
| Header Manager | HM_ | `HM_Common_Headers` |
| CSV Data Set | CSV_ | `CSV_User_Credentials` |
| JSON Extractor | JE_ | `JE_Auth_Token` |
| Response Assertion | RA_ | `RA_Status_Code` |
| Timer | TM_ | `TM_Think_Time` |

### 参数命名

| 参数用途 | 命名规范 | 示例 |
|----------|----------|------|
| 目标主机 | `target_host` | `${__P(target_host,api.example.com)}` |
| 目标端口 | `target_port` | `${__P(target_port,8080)}` |
| 协议 | `protocol` | `${__P(protocol,https)}` |
| 并发数 | `concurrency` | `${__P(concurrency,50)}` |
| Ramp-up | `rampup` | `${__P(rampup,60)}` |
| 持续时间 | `duration` | `${__P(duration,300)}` |
| 思考时间 | `think_time` | `${__P(think_time,1000)}` |

## 参数化最佳实践

### 使用 `__P` 函数

所有外部可配置的参数都应使用 `${__P(propertyName,defaultValue)}` 形式：

```xml
<!-- 不推荐：硬编码 -->
<stringProp name="ThreadGroup.num_threads">100</stringProp>

<!-- 推荐：参数化 -->
<stringProp name="ThreadGroup.num_threads">${__P(concurrency,10)}</stringProp>
```

### 使用 `__property` 函数

与 `__P` 类似，但语法更完整：

```xml
${__property(concurrency,var_name,10)}
```

### 使用 `__P` 覆盖默认值

运行时通过 `-J` 参数覆盖：

```bash
jmeter -n -t test.jmx -l result.jtl -Jconcurrency=200 -Jduration=600
```

## 版本兼容性

### JMeter 3.x → 5.x 变化

1. **属性版本**：从 `3.2` 升级到 `5.0`
2. **新组件**：
   - JSON Extractor（替代正则表达式提取器）
   - JSON Assertion
3. **性能优化**：
   - 改进的 CSV 数据集处理
   - 更好的内存管理

### 确保向后兼容

- 使用标准组件，避免过时组件
- 使用通用的属性函数
- 避免依赖特定版本的 GUI 配置

## 参考资源

- [Apache JMeter 官方文档](https://jmeter.apache.org/usermanual/index.html)
- [JMeter 组件参考](https://jmeter.apache.org/usermanual/component_reference.html)
- [JMeter 最佳实践](https://jmeter.apache.org/usermanual/best-practices.html)
