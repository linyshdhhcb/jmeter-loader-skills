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

## 8. Controllers（控制器）

### 8.1 If Controller
```xml
<IfController guiclass="IfControllerPanel" testclass="IfController" testname="If Controller" enabled="true">
  <stringProp name="IfController.condition">${__jexl3("${status}" == "OK",)}</stringProp>
  <boolProp name="IfController.evaluateAll">false</boolProp>
  <boolProp name="IfController.useExpression">true</boolProp>
</IfController>
```

### 8.2 While Controller
```xml
<WhileController guiclass="WhileControllerGui" testclass="WhileController" testname="While Controller" enabled="true">
  <stringProp name="WhileController.condition">${__jexl3("${has_more}" == "true",)}</stringProp>
</WhileController>
```

### 8.3 ForEach Controller
```xml
<ForeachController guiclass="ForeachControlPanel" testclass="ForeachController" testname="ForEach Controller" enabled="true">
  <stringProp name="ForeachController.inputVal">item_</stringProp>
  <stringProp name="ForeachController.startIndex">0</stringProp>
  <stringProp name="ForeachController.endIndex">-1</stringProp>
  <stringProp name="ForeachController.returnVal">current_item</stringProp>
  <boolProp name="ForeachController.useSeparator">true</boolProp>
</ForeachController>
```

### 8.4 Transaction Controller
```xml
<TransactionController guiclass="TransactionControllerGui" testclass="TransactionController" testname="Transaction Controller" enabled="true">
  <boolProp name="TransactionController.include_timers">false</boolProp>
  <boolProp name="TransactionController.parent">true</boolProp>
</TransactionController>
```

### 8.5 Once Only Controller
```xml
<OnceOnlyController guiclass="OnceOnlyControllerGui" testclass="OnceOnlyController" testname="Once Only Controller" enabled="true"/>
```

### 8.6 Loop Controller
```xml
<LoopController guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
  <boolProp name="LoopController.continue_forever">false</boolProp>
  <stringProp name="LoopController.loops">5</stringProp>
</LoopController>
```

### 8.7 Throughput Controller
```xml
<ThroughputController guiclass="ThroughputControllerGui" testclass="ThroughputController" testname="Throughput Controller" enabled="true">
  <intProp name="ThroughputController.style">1</intProp>
  <boolProp name="ThroughputController.perThread">true</boolProp>
  <intProp name="ThroughputController.percentThroughput">50</intProp>
</ThroughputController>
```

### 8.8 Critical Section Controller
```xml
<CriticalSectionController guiclass="CriticalSectionControllerGui" testclass="CriticalSectionController" testname="Critical Section Controller" enabled="true">
  <stringProp name="CriticalSectionController.lockName">global_lock</stringProp>
</CriticalSectionController>
```

### 8.9 Include Controller
```xml
<IncludeController guiclass="IncludeControllerGui" testclass="IncludeController" testname="Include Controller" enabled="true">
  <stringProp name="IncludeController.includepath">fragment.jmx</stringProp>
</IncludeController>
```

### 8.10 Module Controller
```xml
<ModuleController guiclass="ModuleControllerGui" testclass="ModuleController" testname="Module Controller" enabled="true">
  <collectionProp name="ModuleController.node_path">
    <stringProp name="0">Test Plan</stringProp>
    <stringProp name="1">Thread Group</stringProp>
    <stringProp name="2">My Fragment</stringProp>
  </collectionProp>
</ModuleController>
```

---

## 9. Post Processors（后置处理器）- 补充

### 9.1 Boundary Extractor
```xml
<BoundaryExtractor guiclass="BoundaryExtractorGui" testclass="BoundaryExtractor" testname="Boundary Extractor" enabled="true">
  <stringProp name="BoundaryExtractor.refname">token</stringProp>
  <stringProp name="BoundaryExtractor.boundaries">"token":"</stringProp>
  <stringProp name="BoundaryExtractor.rightBoundary">"</stringProp>
  <stringProp name="BoundaryExtractor.defaultValue">NOT_FOUND</stringProp>
  <stringProp name="BoundaryExtractor.matchNumber">1</stringProp>
  <stringProp name="BoundaryExtractor.useHeaders">false</stringProp>
</BoundaryExtractor>
```

### 9.2 CSS Selector Extractor
```xml
<HtmlExtractor guiclass="HtmlExtractorGui" testclass="HtmlExtractor" testname="CSS Selector Extractor" enabled="true">
  <stringProp name="HtmlExtractor.refname">title</stringProp>
  <stringProp name="HtmlExtractor.expr">h1.title</stringProp>
  <stringProp name="HtmlExtractor.attribute"></stringProp>
  <stringProp name="HtmlExtractor.default">NOT_FOUND</stringProp>
  <stringProp name="HtmlExtractor.match_number">1</stringProp>
  <stringProp name="HtmlExtractor.extractor_impl">JSOUP</stringProp>
</HtmlExtractor>
```

### 9.3 XPath2 Extractor
```xml
<XPath2Extractor guiclass="XPath2ExtractorGui" testclass="XPath2Extractor" testname="XPath2 Extractor" enabled="true">
  <stringProp name="XPath2Extractor.refname">value</stringProp>
  <stringProp name="XPath2Extractor.xpathQuery">//root/element/@attr</stringProp>
  <stringProp name="XPath2Extractor.default">NOT_FOUND</stringProp>
  <stringProp name="XPath2Extractor.matchNumber">1</stringProp>
  <boolProp name="XPath2Extractor.fragment">false</boolProp>
  <stringProp name="XPath2Extractor.namespaces"></stringProp>
</XPath2Extractor>
```

### 9.4 JSON JMESPath Extractor
```xml
<JSONPathJMESPathExtractor guiclass="JSONPathJMESPathExtractorGui" testclass="JSONPathJMESPathExtractor" testname="JMESPath Extractor" enabled="true">
  <stringProp name="JSONPathJMESPathExtractor.refname">items</stringProp>
  <stringProp name="JSONPathJMESPathExtractor.expression">data.items[*].name</stringProp>
  <stringProp name="JSONPathJMESPathExtractor.default">NOT_FOUND</stringProp>
  <stringProp name="JSONPathJMESPathExtractor.matchNumber">1</stringProp>
</JSONPathJMESPathExtractor>
```

---

## 10. Assertions（断言）- 补充

### 10.1 Duration Assertion
```xml
<DurationAssertion guiclass="DurationAssertionGui" testclass="DurationAssertion" testname="Duration Assertion" enabled="true">
  <stringProp name="DurationAssertion.duration">5000</stringProp>
</DurationAssertion>
```

### 10.2 Size Assertion
```xml
<SizeAssertion guiclass="SizeAssertionGui" testclass="SizeAssertion" testname="Size Assertion" enabled="true">
  <stringProp name="SizeAssertion.size">1024</stringProp>
  <intProp name="SizeAssertion.operator">2</intProp>
</SizeAssertion>
```
Operator: 1=equal, 2=greater than, 3=less than, 4=greater or equal, 5=less or equal, 6=not equal

### 10.3 JSON JMESPath Assertion
```xml
<JSONPathJMESPathAssertion guiclass="JSONPathJMESPathAssertionGui" testclass="JSONPathJMESPathAssertion" testname="JMESPath Assertion" enabled="true">
  <stringProp name="JSONPathJMESPathAssertion.expression">data.status</stringProp>
  <stringProp name="JSONPathJMESPathAssertion.expectedValue">success</stringProp>
  <boolProp name="JSONPathJMESPathAssertion.isRegex">false</boolProp>
</JSONPathJMESPathAssertion>
```

### 10.4 XPath2 Assertion
```xml
<XPath2Assertion guiclass="XPath2AssertionGui" testclass="XPath2Assertion" testname="XPath2 Assertion" enabled="true">
  <stringProp name="XPath2Assertion.xpath">//root/status[text()='OK']</stringProp>
  <stringProp name="XPath2Assertion.namespaces"></stringProp>
</XPath2Assertion>
```

### 10.5 MD5Hex Assertion
```xml
<MD5HexAssertion guiclass="MD5HexAssertionGUI" testclass="MD5HexAssertion" testname="MD5Hex Assertion" enabled="true">
  <stringProp name="MD5HexAssertion.size">d41d8cd98f00b204e9800998ecf8427e</stringProp>
</MD5HexAssertion>
```

---

## 11. Timers（定时器）- 补充

### 11.1 Gaussian Random Timer
```xml
<GaussianRandomTimer guiclass="GaussianRandomTimerGui" testclass="GaussianRandomTimer" testname="Gaussian Random Timer" enabled="true">
  <stringProp name="ConstantTimer.delay">1000</stringProp>
  <stringProp name="RandomTimer.range">300</stringProp>
</GaussianRandomTimer>
```

### 11.2 Constant Throughput Timer
```xml
<ConstantThroughputTimer guiclass="ConstantThroughputTimerGui" testclass="ConstantThroughputTimer" testname="Constant Throughput Timer" enabled="true">
  <stringProp name="ConstantThroughputTimer.throughput">60.0</stringProp>
  <intProp name="ConstantThroughputTimer.calcMode">1</intProp>
</ConstantThroughputTimer>
```
calcMode: 0=this thread only, 1=all active threads, 2=all active threads in current thread group, 3=all active threads (shared)

### 11.3 Precise Throughput Timer
```xml
<PreciseThroughputTimer guiclass="PreciseThroughputTimerGui" testclass="PreciseThroughputTimer" testname="Precise Throughput Timer" enabled="true">
  <stringProp name="throughput">60.0</stringProp>
  <stringProp name="throughputPeriod">60</stringProp>
  <intProp name="exactLimit">100</intProp>
  <intProp name="allowedTimers">5</intProp>
  <stringProp name="randomSeed">0</stringProp>
</PreciseThroughputTimer>
```

### 11.4 Synchronizing Timer
```xml
<Synchronizer guiclass="SynchronizerGui" testclass="Synchronizer" testname="Synchronizing Timer" enabled="true">
  <stringProp name="groupSize">10</stringProp>
  <stringProp name="timeoutInMs">0</stringProp>
</Synchronizer>
```

### 11.5 Poisson Random Timer
```xml
<PoissonRandomTimer guiclass="PoissonRandomTimerGui" testclass="PoissonRandomTimer" testname="Poisson Random Timer" enabled="true">
  <stringProp name="ConstantTimer.delay">1000</stringProp>
  <stringProp name="RandomTimer.range">100</stringProp>
</PoissonRandomTimer>
```

---

## 12. JSR223 Elements（JSR223 脚本元素）

### 12.1 JSR223 Sampler
```xml
<JSR223Sampler guiclass="TestBeanGUI" testclass="JSR223Sampler" testname="JSR223 Sampler" enabled="true">
  <stringProp name="scriptLanguage">groovy</stringProp>
  <stringProp name="parameters"></stringProp>
  <stringProp name="filename"></stringProp>
  <boolProp name="cacheKey">true</boolProp>
  <stringProp name="script">def response = "Hello from Groovy";
SampleResult.setResponseData(response, "UTF-8");
SampleResult.setSuccessful(true);</stringProp>
</JSR223Sampler>
```

### 12.2 JSR223 PreProcessor
```xml
<JSR223PreProcessor guiclass="TestBeanGUI" testclass="JSR223PreProcessor" testname="JSR223 PreProcessor" enabled="true">
  <stringProp name="scriptLanguage">groovy</stringProp>
  <stringProp name="parameters"></stringProp>
  <stringProp name="filename"></stringProp>
  <boolProp name="cacheKey">true</boolProp>
  <stringProp name="script">vars.put("timestamp", String.valueOf(System.currentTimeMillis()));</stringProp>
</JSR223PreProcessor>
```

### 12.3 JSR223 PostProcessor
```xml
<JSR223PostProcessor guiclass="TestBeanGUI" testclass="JSR223PostProcessor" testname="JSR223 PostProcessor" enabled="true">
  <stringProp name="scriptLanguage">groovy</stringProp>
  <stringProp name="parameters"></stringProp>
  <stringProp name="filename"></stringProp>
  <boolProp name="cacheKey">true</boolProp>
  <stringProp name="script">def response = prev.getResponseDataAsString();
log.info("Response length: " + response.length());</stringProp>
</JSR223PostProcessor>
```

### 12.4 JSR223 Assertion
```xml
<JSR223Assertion guiclass="TestBeanGUI" testclass="JSR223Assertion" testname="JSR223 Assertion" enabled="true">
  <stringProp name="scriptLanguage">groovy</stringProp>
  <stringProp name="parameters"></stringProp>
  <stringProp name="filename"></stringProp>
  <boolProp name="cacheKey">true</boolProp>
  <stringProp name="script">if (!prev.isSuccessful()) {
    AssertionResult.setFailure(true);
    AssertionResult.setFailureMessage("Request failed: " + prev.getResponseCode());
}</stringProp>
</JSR223Assertion>
```

### 12.5 JSR223 Timer
```xml
<JSR223Timer guiclass="TestBeanGUI" testclass="JSR223Timer" testname="JSR223 Timer" enabled="true">
  <stringProp name="scriptLanguage">groovy</stringProp>
  <stringProp name="parameters"></stringProp>
  <stringProp name="filename"></stringProp>
  <boolProp name="cacheKey">true</boolProp>
  <stringProp name="script">return (int)(Math.random() * 2000) + 1000;</stringProp>
</JSR223Timer>
```

### 12.6 JSR223 Listener
```xml
<JSR223Listener guiclass="TestBeanGUI" testclass="JSR223Listener" testname="JSR223 Listener" enabled="true">
  <stringProp name="scriptLanguage">groovy</stringProp>
  <stringProp name="parameters"></stringProp>
  <stringProp name="filename"></stringProp>
  <boolProp name="cacheKey">true</boolProp>
  <stringProp name="script">if (!sampleEvent.getResult().isSuccessful()) {
    log.error("Failed: " + sampleEvent.getResult().getSampleLabel());
}</stringProp>
</JSR223Listener>
```

---

## 13. Special Thread Groups（特殊线程组）

### 13.1 setUp Thread Group
```xml
<SetupThreadGroup guiclass="SetupThreadGroupGui" testclass="SetupThreadGroup" testname="setUp Thread Group" enabled="true">
  <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
  <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
    <boolProp name="LoopController.continue_forever">false</boolProp>
    <stringProp name="LoopController.loops">1</stringProp>
  </elementProp>
  <stringProp name="ThreadGroup.num_threads">1</stringProp>
  <stringProp name="ThreadGroup.ramp_time">1</stringProp>
  <boolProp name="ThreadGroup.scheduler">false</boolProp>
  <stringProp name="ThreadGroup.duration"></stringProp>
  <stringProp name="ThreadGroup.delay"></stringProp>
  <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
</SetupThreadGroup>
```

### 13.2 tearDown Thread Group
```xml
<PostThreadGroup guiclass="PostThreadGroupGui" testclass="PostThreadGroup" testname="tearDown Thread Group" enabled="true">
  <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
  <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
    <boolProp name="LoopController.continue_forever">false</boolProp>
    <stringProp name="LoopController.loops">1</stringProp>
  </elementProp>
  <stringProp name="ThreadGroup.num_threads">1</stringProp>
  <stringProp name="ThreadGroup.ramp_time">1</stringProp>
  <boolProp name="ThreadGroup.scheduler">false</boolProp>
  <stringProp name="ThreadGroup.duration"></stringProp>
  <stringProp name="ThreadGroup.delay"></stringProp>
  <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
</PostThreadGroup>
```

---

## 14. Backend Listener（后端监听器）

### 14.1 InfluxDB Backend Listener
```xml
<BackendListener guiclass="BackendListenerGui" testclass="BackendListener" testname="Backend Listener" enabled="true">
  <stringProp name="classname">org.apache.jmeter.visualizers.backend.influxdb.InfluxdbBackendListenerClient</stringProp>
  <elementProp name="Arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" enabled="true">
    <collectionProp name="Arguments.arguments">
      <elementProp name="influxdbUrl" elementType="Argument">
        <stringProp name="Argument.name">influxdbUrl</stringProp>
        <stringProp name="Argument.value">http://${__P(influxdb_host,localhost)}:${__P(influxdb_port,8086)}${__P(influxdb_path,/api/v2/write)}</stringProp>
      </elementProp>
      <elementProp name="influxdbToken" elementType="Argument">
        <stringProp name="Argument.name">influxdbToken</stringProp>
        <stringProp name="Argument.value">${__P(influxdb_token,)}</stringProp>
      </elementProp>
      <elementProp name="application" elementType="Argument">
        <stringProp name="Argument.name">application</stringProp>
        <stringProp name="Argument.value">${__P(application,JMeter-Test)}</stringProp>
      </elementProp>
      <elementProp name="measurement" elementType="Argument">
        <stringProp name="Argument.name">measurement</stringProp>
        <stringProp name="Argument.value">jmeter</stringProp>
      </elementProp>
      <elementProp name="summaryOnly" elementType="Argument">
        <stringProp name="Argument.name">summaryOnly</stringProp>
        <stringProp name="Argument.value">false</stringProp>
      </elementProp>
      <elementProp name="samplersRegex" elementType="Argument">
        <stringProp name="Argument.name">samplersRegex</stringProp>
        <stringProp name="Argument.value">.*</stringProp>
      </elementProp>
      <elementProp name="percentiles" elementType="Argument">
        <stringProp name="Argument.name">percentiles</stringProp>
        <stringProp name="Argument.value">50;90;95;99</stringProp>
      </elementProp>
      <elementProp name="testTitle" elementType="Argument">
        <stringProp name="Argument.name">testTitle</stringProp>
        <stringProp name="Argument.value">${__P(test_title,JMeter Load Test)}</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
  <stringProp name="asyncQueueSize">5000</stringProp>
</BackendListener>
```

### 14.2 Graphite Backend Listener
```xml
<BackendListener guiclass="BackendListenerGui" testclass="BackendListener" testname="Backend Listener" enabled="true">
  <stringProp name="classname">org.apache.jmeter.visualizers.backend.graphite.GraphiteBackendListenerClient</stringProp>
  <elementProp name="Arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" enabled="true">
    <collectionProp name="Arguments.arguments">
      <elementProp name="graphiteMetricsSender" elementType="Argument">
        <stringProp name="Argument.name">graphiteMetricsSender</stringProp>
        <stringProp name="Argument.value">org.apache.jmeter.visualizers.backend.graphite.TextGraphiteMetricsSender</stringProp>
      </elementProp>
      <elementProp name="graphiteHost" elementType="Argument">
        <stringProp name="Argument.name">graphiteHost</stringProp>
        <stringProp name="Argument.value">${__P(graphite_host,localhost)}</stringProp>
      </elementProp>
      <elementProp name="graphitePort" elementType="Argument">
        <stringProp name="Argument.name">graphitePort</stringProp>
        <stringProp name="Argument.value">${__P(graphite_port,2003)}</stringProp>
      </elementProp>
      <elementProp name="rootMetricsPrefix" elementType="Argument">
        <stringProp name="Argument.name">rootMetricsPrefix</stringProp>
        <stringProp name="Argument.value">jmeter.</stringProp>
      </elementProp>
      <elementProp name="summaryOnly" elementType="Argument">
        <stringProp name="Argument.name">summaryOnly</stringProp>
        <stringProp name="Argument.value">false</stringProp>
      </elementProp>
      <elementProp name="samplersList" elementType="Argument">
        <stringProp name="Argument.name">samplersList</stringProp>
        <stringProp name="Argument.value">.*</stringProp>
      </elementProp>
      <elementProp name="percentiles" elementType="Argument">
        <stringProp name="Argument.name">percentiles</stringProp>
        <stringProp name="Argument.value">50;90;95;99</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
  <stringProp name="asyncQueueSize">5000</stringProp>
</BackendListener>
```

---

## 15. Other Configuration Elements（其他配置元素）

### 15.1 HTTP Cache Manager
```xml
<CacheManager guiclass="CacheManagerGui" testclass="CacheManager" testname="HTTP Cache Manager" enabled="true">
  <boolProp name="clearEachIteration">false</boolProp>
  <boolProp name="useExpires">true</boolProp>
  <stringProp name="maxCacheSize">5000</stringProp>
</CacheManager>
```

### 15.2 HTTP Authorization Manager
```xml
<AuthManager guiclass="AuthPanel" testclass="AuthManager" testname="HTTP Authorization Manager" enabled="true">
  <boolProp name="AuthManager.clearEachIteration">false</boolProp>
  <collectionProp name="AuthManager.auth_list">
    <elementProp name="" elementType="Authorization">
      <stringProp name="Authorization.url">http://api.example.com</stringProp>
      <stringProp name="Authorization.username">admin</stringProp>
      <stringProp name="Authorization.password">password</stringProp>
      <stringProp name="Authorization.domain"></stringProp>
      <stringProp name="Authorization.realm"></stringProp>
      <stringProp name="Authorization.mechanism">BASIC</stringProp>
    </elementProp>
  </collectionProp>
</AuthManager>
```

### 15.3 DNS Cache Manager
```xml
<DNSCacheManager guiclass="DNSCachePanel" testclass="DNSCacheManager" testname="DNS Cache Manager" enabled="true">
  <boolProp name="clearEachIteration">false</boolProp>
  <boolProp name="isCustomResolver">true</boolProp>
  <collectionProp name="DNSCacheManager.servers">
    <stringProp name="">8.8.8.8</stringProp>
    <stringProp name="">8.8.4.4</stringProp>
  </collectionProp>
  <collectionProp name="DNSCacheManager.hosts"/>
</DNSCacheManager>
```

### 15.4 Keystore Configuration
```xml
<KeystoreConfig guiclass="TestBeanGUI" testclass="KeystoreConfig" testname="Keystore Configuration" enabled="true">
  <stringProp name="startIndex">0</stringProp>
  <stringProp name="endIndex">-1</stringProp>
  <stringProp name="preload">True</stringProp>
</KeystoreConfig>
```

### 15.5 Counter
```xml
<CounterConfig guiclass="CounterConfigGui" testclass="CounterConfig" testname="Counter" enabled="true">
  <stringProp name="CounterConfig.start">1</stringProp>
  <stringProp name="CounterConfig.incr">1</stringProp>
  <stringProp name="CounterConfig.max">9999</stringProp>
  <stringProp name="CounterConfig.name">counter</stringProp>
  <stringProp name="CounterConfig.format"></stringProp>
  <boolProp name="CounterConfig.per_user">true</boolProp>
  <boolProp name="CounterConfig.reset_on_tg_iteration">false</boolProp>
</CounterConfig>
```

### 15.6 Random Variable
```xml
<RandomVariableConfig guiclass="RandomVariableConfigGui" testclass="RandomVariableConfig" testname="Random Variable" enabled="true">
  <stringProp name="minimumValue">1</stringProp>
  <stringProp name="maximumValue">1000</stringProp>
  <stringProp name="variableName">random_id</stringProp>
  <stringProp name="outputFormat"></stringProp>
  <boolProp name="perThread">true</boolProp>
  <stringProp name="randomSeed"></stringProp>
</RandomVariableConfig>
```

---

## 16. Miscellaneous（杂项组件）

### 16.1 Debug Sampler
```xml
<DebugSampler guiclass="TestBeanGUI" testclass="DebugSampler" testname="Debug Sampler" enabled="true">
  <boolProp name="displayJMeterProperties">false</boolProp>
  <boolProp name="displayJMeterVariables">true</boolProp>
  <boolProp name="displaySystemProperties">false</boolProp>
</DebugSampler>
```

### 16.2 Flow Control Action
```xml
<ActionController guiclass="ActionControllerGui" testclass="ActionController" testname="Flow Control Action" enabled="true">
  <intProp name="ActionController.target">0</intProp>
  <intProp name="ActionController.action">1</intProp>
  <stringProp name="ActionController.duration">1000</stringProp>
</ActionController>
```
target: 0=current thread, 1=all threads
action: 0=pause, 1=stop, 2=stop now, 3=go to next loop iteration, 4=break current loop

### 16.3 Test Fragment
```xml
<TestFragmentController guiclass="TestFragmentControllerGui" testclass="TestFragmentController" testname="Test Fragment" enabled="true"/>
```

### 16.4 Result Status Action Handler
```xml
<ResultAction guiclass="ResultActionGui" testclass="ResultAction" testname="Result Status Action Handler" enabled="true">
  <intProp name="OnError.action">1</intProp>
</ResultAction>
```
OnError.action: 0=continue, 1=start next thread loop, 2=stop thread, 3=stop test, 4=stop test now

### 16.5 Sample Timeout
```xml
<SampleTimeout guiclass="SampleTimeoutGui" testclass="SampleTimeout" testname="Sample Timeout" enabled="true">
  <stringProp name="SampleTimeout.timeout">5000</stringProp>
</SampleTimeout>
```
