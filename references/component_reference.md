# JMeter 组件完整参考

基于 Apache JMeter 官方文档（xdocs/usermanual/component_reference.xml）整理，涵盖 JMeter 5.x 全部组件。

## 组件分类总览

| 分类 | 数量 | 说明 |
|------|------|------|
| Samplers（采样器） | 19 | 向服务器发送请求 |
| Logic Controllers（逻辑控制器） | 17 | 控制请求执行逻辑 |
| Listeners（监听器） | 17 | 查看/保存测试结果 |
| Configuration Elements（配置元素） | 20 | 设置默认值和变量 |
| Assertions（断言） | 15 | 验证响应结果 |
| Timers（定时器） | 9 | 控制请求间隔 |
| Pre Processors（前置处理器） | 8 | 采样前执行操作 |
| Post-Processors（后置处理器） | 11 | 采样后提取数据 |
| Miscellaneous（杂项） | 13 | 线程组、测试计划等 |

---

## 一、Samplers（采样器）

采样器执行 JMeter 的实际工作，每个采样器生成一个或多个采样结果。

### 1. FTP Request

向 FTP 服务器发送"检索文件"或"上传文件"请求。下载的文件可存储到磁盘或响应数据中。延迟时间设置为登录所需时间。

| 属性 | 说明 |
|------|------|
| Server Name/IP | FTP 服务器地址 |
| Port | 端口号 |
| Remote File | 远程文件路径 |
| Local File | 本地文件路径 |
| Local File Contents | 本地文件内容 |
| get(RETR)/put(STOR) | 下载或上传 |
| Binary Mode | 是否使用二进制模式 |
| Save File in Response | 是否在响应中保存文件 |
| Username | 用户名 |
| Password | 密码 |

### 2. HTTP Request

向 Web 服务器发送 HTTP/HTTPS 请求。可控制是否解析 HTML 文件中的嵌入资源（图片、applet、CSS、脚本、框架等）。

三种实现：
- **AJP/1.3 Sampler**：使用 Tomcat AJP 协议
- **HTTP Request（Java/HttpClient4）**：默认使用 HttpClient4
- **GraphQL HTTP Request**：GraphQL 请求

| 属性 | 说明 |
|------|------|
| Server | 服务器名称或 IP |
| Port | 端口号 |
| Connect Timeout | 连接超时（毫秒） |
| Response Timeout | 响应超时（毫秒） |
| Protocol | 协议（http/https） |
| Method | HTTP 方法（GET/POST/PUT/DELETE 等） |
| Content Encoding | 内容编码 |
| Redirect Automatically | 自动重定向 |
| Follow Redirects | 跟随重定向 |
| Use KeepAlive | 使用 Keep-Alive |
| multipart/form-data | 是否使用 multipart |
| Path | 请求路径 |
| Parameters | 请求参数 |
| Retrieve All Embedded Resources | 获取所有嵌入资源 |
| Source address | 源地址（IP/网络接口） |

### 3. JDBC Request

向数据库发送 JDBC 请求（SQL 查询）。需先配置 JDBC Connection Configuration。

| 属性 | 说明 |
|------|------|
| Variable Name of Pool | 连接池变量名 |
| Query Type | 查询类型（Select/Update/Callable/Prepared） |
| SQL Query | SQL 语句 |
| Parameter values | 参数值 |
| Parameter types | 参数类型 |
| Variable Names | 结果列变量名 |
| Result Variable Name | 完整结果集变量名 |
| Query timeout | 查询超时 |
| Limit ResultSet | 限制结果集行数 |
| Handle ResultSet | 结果集处理方式 |

查询类型：

| 类型 | 说明 |
|------|------|
| Select Statement | 执行 SELECT 查询 |
| Update Statement | 执行 UPDATE/INSERT/DELETE |
| Callable Statement | 调用存储过程 |
| Prepared Select Statement | 预编译 SELECT |
| Prepared Update Statement | 预编译 UPDATE/INSERT/DELETE |
| Commit | 提交事务 |
| Rollback | 回滚事务 |
| AutoCommit(false) | 关闭自动提交 |
| AutoCommit(true) | 开启自动提交 |

### 4. Java Request

控制实现了 JavaSamplerClient 接口的 Java 类。可编写自定义实现，利用 JMeter 的多线程、参数控制和数据收集功能。

| 属性 | 说明 |
|------|------|
| Classname | Java 采样器类名 |
| Send Parameters with Request | 请求参数 |
| Sleep_time | 休眠时间 |
| Sleep_mask | 休眠掩码 |
| Label | 标签 |
| ResponseCode | 响应码 |
| ResponseMessage | 响应消息 |
| Status | 状态 |
| SamplerData | 采样器数据 |
| ResultData | 结果数据 |

### 5. LDAP Request

向 LDAP 服务器发送 Add/Modify/Delete/Search 请求。

| 属性 | 说明 |
|------|------|
| Server Name/IP | LDAP 服务器地址 |
| Port | 端口号 |
| root DN | 根 DN |
| Username | 用户名 |
| Password | 密码 |
| Entry DN | 条目 DN |
| Delete | 删除操作 |
| Search base | 搜索基础 |
| Search filter | 搜索过滤器 |

### 6. LDAP Extended Request

LDAP 采样器的扩展版本，可发送 8 种不同的 LDAP 请求：Thread bind/unbind、Single bind/unbind、Rename entry、Add/Delete/Search/Modification test、Compare。

### 7. Access Log Sampler

读取访问日志并生成 HTTP 请求。支持 Tomcat 通用日志格式。

| 属性 | 说明 |
|------|------|
| Server | 服务器地址 |
| Protocol | 协议 |
| Port | 端口 |
| Log parser class | 日志解析器类 |
| Filter | 过滤器 |
| Location of log file | 日志文件路径 |

### 8. BeanShell Sampler

使用 BeanShell 脚本语言编写采样器。**建议迁移到 JSR223 Sampler + Groovy 以获得更好性能。**

| 属性 | 说明 |
|------|------|
| Reset bsh.Interpreter before each call | 每次调用前重置解释器 |
| Parameters | 参数 |
| Script file | 脚本文件 |
| Script | 脚本内容 |

### 9. JSR223 Sampler

使用 JSR223 脚本代码执行采样或计算。支持脚本编译缓存以显著提升性能，**推荐使用 Groovy 语言**。

| 属性 | 说明 |
|------|------|
| Scripting Language | 脚本语言（推荐 Groovy） |
| Script File | 脚本文件 |
| Parameters | 参数 |
| Cache compiled script if available | 缓存编译脚本（推荐勾选） |
| Script | 脚本内容 |

### 10. TCP Sampler

打开到指定服务器的 TCP/IP 连接，发送文本并等待响应。

| 属性 | 说明 |
|------|------|
| TCPClient classname | TCP 客户端实现类 |
| ServerName/IP | 服务器地址 |
| Port | 端口 |
| Re-use connection | 复用连接 |
| Close connection | 关闭连接 |
| SO_LINGER | SO_LINGER 设置 |
| EOL byte value | 消息结束字节值 |
| Connect/Response Timeout | 连接/响应超时 |
| Set NoDelay | 禁用 Nagle 算法 |
| Text to Send | 发送文本 |

TCP 客户端实现类：

| 实现类 | 说明 |
|--------|------|
| `TCPClientImpl` | 文本 TCP 客户端 |
| `BinaryTCPClientImpl` | 二进制 TCP 客户端 |
| `LengthPrefixedBinaryTCPClientImpl` | 长度前缀二进制客户端 |

### 11. JMS Publisher

向指定目标（topic/queue）发布 JMS 消息。支持 Text/Map/Object/Bytes 消息类型。

| 属性 | 说明 |
|------|------|
| use JNDI properties file | 使用 JNDI 属性文件 |
| JNDI Initial Context Factory | JNDI 初始上下文工厂 |
| Provider URL | 提供者 URL |
| Destination | 目标（topic/queue） |
| Setup | 设置方式 |
| Authentication | 认证方式 |
| User/Password | 用户名/密码 |
| Expiration | 过期时间 |
| Priority | 优先级 |
| Number of samples to aggregate | 聚合样本数 |
| Message source | 消息来源 |
| Message type | 消息类型 |
| Content encoding | 内容编码 |

### 12. JMS Subscriber

订阅指定目标（topic/queue）中的 JMS 消息。

| 属性 | 说明 |
|------|------|
| use JNDI properties file | 使用 JNDI 属性文件 |
| JNDI Initial Context Factory | JNDI 初始上下文工厂 |
| Provider URL | 提供者 URL |
| Destination | 目标 |
| Durable Subscription ID | 持久订阅 ID |
| Client ID | 客户端 ID |
| JMS Selector | JMS 选择器 |
| Setup | 设置方式 |
| Number of samples to aggregate | 聚合样本数 |
| Save response | 保存响应 |
| Timeout | 超时时间 |
| Client | 客户端实现 |
| Stop between samples | 采样间停止 |

### 13. JMS Point-to-Point

通过点对点连接（队列）发送和可选接收 JMS 消息。

通信模式：

| 模式 | 说明 |
|------|------|
| Request Only | 仅发送 |
| Request Response | 请求-响应 |
| Read | 读取 |
| Browse | 浏览 |
| Clear | 清除 |

### 14. JUnit Request

支持标准 JUnit 约定和扩展，包括 JUnit4 注解（@Test, @Before, @After, @BeforeClass, @AfterClass）。

| 属性 | 说明 |
|------|------|
| Search for JUnit4 annotations | 搜索 JUnit4 注解 |
| Package filter | 包过滤器 |
| Class name | 类名 |
| Constructor string | 构造函数字符串 |
| Test method | 测试方法 |
| Success/Failure/Error message/code | 成功/失败/错误消息/代码 |
| Do not call setUp/tearDown | 不调用 setUp/tearDown |
| Append assertion errors | 追加断言错误 |
| Append runtime exceptions | 追加运行时异常 |
| Create a new Instance per sample | 每次采样创建新实例 |

### 15. Mail Reader Sampler

使用 POP3(S) 或 IMAP(S) 协议读取（并可选删除）邮件消息。

| 属性 | 说明 |
|------|------|
| Server Type | 服务器类型（POP3/IMAP） |
| Server | 服务器地址 |
| Port | 端口 |
| Username | 用户名 |
| Password | 密码 |
| Folder | 邮件文件夹 |
| Number of messages to retrieve | 获取消息数 |
| Fetch headers only | 仅获取头部 |
| Delete messages | 删除消息 |
| Store the message using MIME | 使用 MIME 存储消息 |
| 安全选项 | SSL/StartTLS/Trust All |

### 16. Flow Control Action

用于条件控制器中的采样器，不生成样本，而是暂停或停止选定目标。

| 属性 | 说明 |
|------|------|
| Target | 目标（Current Thread/All Threads） |
| Action | 动作（Pause/Stop/Stop Now/Go to next loop iteration） |
| Duration | 暂停时长（毫秒） |

### 17. SMTP Sampler

使用 SMTP/SMTPS 协议发送邮件消息。

| 属性 | 说明 |
|------|------|
| Server | 服务器地址 |
| Port | 端口 |
| Connection/Read timeout | 连接/读取超时 |
| Address From/To/CC/BCC/Reply-To | 邮件地址 |
| Use Auth | 使用认证 |
| Username/Password | 用户名/密码 |
| 安全选项 | SSL/TLS |
| Subject | 主题 |
| Message | 消息内容 |
| Attach files | 附件 |
| Send .eml | 发送 .eml 文件 |
| Calculate message size | 计算消息大小 |

### 18. OS Process Sampler

在本地机器上执行命令。

| 属性 | 说明 |
|------|------|
| Command | 命令 |
| Working directory | 工作目录 |
| Command Parameters | 命令参数 |
| Environment Parameters | 环境参数 |
| Standard input/output/error | 标准输入/输出/错误 |
| Check Return Code | 检查返回码 |
| Expected Return Code | 期望返回码 |
| Timeout | 超时时间 |

### 19. Bolt Request

通过 Bolt 协议运行 Cypher 查询（Neo4j 数据库）。需先配置 Bolt Connection Configuration。

| 属性 | 说明 |
|------|------|
| Cypher statement | Cypher 语句 |
| Params | 参数 |
| Record Query Results | 记录查询结果 |
| Access Mode | 访问模式（WRITE/READ） |
| Database | 数据库名 |
| Transaction timeout | 事务超时 |

---

## 二、Logic Controllers（逻辑控制器）

逻辑控制器决定采样器的处理顺序。

### 1. Simple Controller

组织采样器和其他逻辑控制器，不提供额外功能，仅作为存储设备。

### 2. Loop Controller

循环执行其子元素指定次数。循环索引暴露为变量 `__jm__<Name>__idx`。

| 属性 | 说明 |
|------|------|
| Loop Count | 循环次数（-1 或 forever 表示永久） |

### 3. Once Only Controller

每个线程仅处理一次控制器内的内容。在循环父控制器的第一次迭代时执行。适合放置登录请求。

### 4. Interleave Controller

每次循环迭代时交替执行子控制器。

| 属性 | 说明 |
|------|------|
| ignore sub-controller blocks | 忽略子控制器块 |
| Interleave across threads | 跨线程交替 |

### 5. Random Controller

类似 Interleave Controller，但随机选择子控制器/采样器执行。

| 属性 | 说明 |
|------|------|
| ignore sub-controller blocks | 忽略子控制器块 |

### 6. Random Order Controller

类似 Simple Controller，但以随机顺序执行每个子元素（最多执行一次）。

### 7. Throughput Controller

控制其执行频率。有两种模式：百分比执行和总执行次数。**注意：名称有误导性，实际不控制吞吐量。**

| 属性 | 说明 |
|------|------|
| Execution Style | 执行方式（百分比/总次数） |
| Throughput | 吞吐量值 |
| Per User | 是否按用户计算 |

### 8. Runtime Controller

控制其子元素的运行时长，超过配置的运行时间后停止。

| 属性 | 说明 |
|------|------|
| Runtime (seconds) | 运行时长（秒） |

### 9. If Controller

根据条件控制是否执行子元素。**推荐使用变量表达式模式**（`${__jexl3()}` 或 `${__groovy()}`）而非 JavaScript 模式以获得更好性能。

| 属性 | 说明 |
|------|------|
| Condition | 条件表达式 |
| Interpret Condition as Variable Expression? | 将条件解释为变量表达式 |
| Evaluate for all children | 对所有子元素评估条件 |

### 10. While Controller

当条件为 "false" 时停止循环子元素。循环索引暴露为变量 `__jm__<Name>__idx`。

| 属性 | 说明 |
|------|------|
| Condition | 条件（blank=永真循环/LAST=上一次成功/变量或函数） |

### 11. Switch Controller

根据开关值运行指定的子元素。开关值可以是数字或名称。

| 属性 | 说明 |
|------|------|
| Switch Value | 开关值（数字索引或名称） |

### 12. ForEach Controller

遍历一组相关变量的值。特别适合与正则表达式后处理器配合使用。循环索引暴露为变量 `__jm__<Name>__idx`。

| 属性 | 说明 |
|------|------|
| Input variable prefix | 输入变量前缀 |
| Start index for loop | 起始索引 |
| End index for loop | 结束索引 |
| Output variable | 输出变量名 |
| Use Separator | 使用分隔符 |

### 13. Module Controller

在运行时将测试计划片段替换到当前测试计划中。片段可位于任何线程组中。

| 属性 | 说明 |
|------|------|
| Module to Run | 要运行的模块 |

### 14. Include Controller

引用外部 JMX 文件。设计用于包含 Test Fragment。

| 属性 | 说明 |
|------|------|
| Filename | JMX 文件路径 |

### 15. Transaction Controller

生成一个额外样本，测量嵌套测试元素的总执行时间。

| 属性 | 说明 |
|------|------|
| Generate Parent Sample | 作为父样本生成 |
| Include duration of timer and pre-post processors | 包含定时器和前后处理器的耗时 |

### 16. Recording Controller

占位符，指示代理服务器应将样本记录到何处。运行时无效果。

### 17. Critical Section Controller

确保其子元素同时只被一个线程执行（使用命名锁）。**锁仅在单个 JVM 内有效。**

| 属性 | 说明 |
|------|------|
| Lock Name | 锁名称（同名锁互斥） |

---

## 三、Listeners（监听器）

监听器监听测试结果，提供查看、保存和读取测试结果的功能。

### 性能警告

以下监听器会保留每个样本的副本，大量样本时消耗大量内存：
- View Results Tree
- View Results in Table
- Assertion Results
- Graph Results

**负载测试时不得使用 View Results Tree 和 Graph Results。**

### 不保留副本的监听器（推荐用于负载测试）

- Simple Data Writer
- BeanShell/JSR223 Listener
- Mailer Visualizer
- Monitor Results
- Summary Report

### 聚合后不保留每个样本的监听器

- Aggregate Report
- Aggregate Graph

### 1. Simple Data Writer

将结果记录到文件但不显示 UI。**提供高效的数据记录方式，消除 GUI 开销。**

### 2. Aggregate Report

为每个不同名称的请求创建表格行，汇总响应信息。

| 列 | 说明 |
|----|------|
| Label | 请求标签 |
| # Samples | 样本数 |
| Average | 平均响应时间 |
| Median | 中位数 |
| 90%/95%/99% Line | 百分位数 |
| Min | 最小值 |
| Max | 最大值 |
| Error % | 错误率 |
| Throughput | 吞吐量 |
| Received/Sent KB/sec | 收发速率 |

### 3. Aggregate Graph

类似 Aggregate Report，但提供生成条形图和保存为 PNG 文件的功能。

### 4. Response Time Graph

绘制折线图显示每个标记请求的响应时间演变。

| 属性 | 说明 |
|------|------|
| Interval (ms) | 时间间隔 |
| Sampler label selection | 采样器标签选择 |
| Title | 图表标题 |
| Line settings | 线条设置 |
| Graph size | 图表大小 |
| X/Y Axis settings | 坐标轴设置 |
| Legend | 图例 |

### 5. View Results Tree

以树形结构显示所有采样响应。支持多种渲染器：CSS/JQuery Tester、Document、HTML、JSON、Regexp Tester、XPath Tester、Boundary Extractor Tester 等。**仅用于调试，负载测试时不得使用。**

### 6. View Results in Table

为每个采样结果创建一行。内存消耗大。

### 7. Summary Report

类似 Aggregate Report 但使用更少内存。

### 8. Mailer Visualizer

当测试运行收到过多失败响应时发送电子邮件通知。

| 属性 | 说明 |
|------|------|
| From | 发件人 |
| Addressee(s) | 收件人 |
| Success/Failure Subject | 成功/失败主题 |
| Success/Failure Limit | 成功/失败阈值 |
| Host | SMTP 主机 |
| Port | 端口 |
| Login | 登录名 |
| Password | 密码 |
| Connection security | 连接安全 |

### 9. BeanShell Listener

使用 BeanShell 处理采样结果。**建议迁移到 JSR223 Listener + Groovy。**

### 10. JSR223 Listener

使用 JSR223 脚本代码处理采样结果。

### 11. Generate Summary Results

生成测试运行摘要到日志文件和/或标准输出。显示运行总计和差异数据。**主要用于 CLI 模式。**

### 12. Backend Listener

异步监听器，可插入自定义 BackendListenerClient 实现。

三种内置实现：

**Graphite 实现：**

| 属性 | 说明 |
|------|------|
| graphiteMetricsSender | Graphite 发送器类 |
| graphiteHost | Graphite 主机 |
| graphitePort | Graphite 端口 |
| rootMetricsPrefix | 根指标前缀 |
| summaryOnly | 仅摘要 |
| samplersList | 采样器列表 |
| percentiles | 百分位数 |

**InfluxDB 实现：**

| 属性 | 说明 |
|------|------|
| influxdbMetricsSender | InfluxDB 发送器类 |
| influxdbUrl | InfluxDB URL |
| influxdbToken | InfluxDB Token |
| application | 应用名称 |
| measurement | 度量名称 |
| summaryOnly | 仅摘要 |
| samplersRegex | 采样器正则 |
| testTitle | 测试标题 |
| eventTags | 事件标签 |
| percentiles | 百分位数 |

### 13. Save Responses to a file

为范围内的每个采样创建响应数据文件。

| 属性 | 说明 |
|------|------|
| Filename Prefix | 文件名前缀 |
| Variable Name containing saved file name | 保存文件名的变量 |
| Minimum Length of sequence number | 序列号最小长度 |
| Save Failed/Successful Responses only | 仅保存失败/成功响应 |
| Don't add number/suffix to prefix | 不添加编号/后缀 |
| Add timestamp | 添加时间戳 |

### 14. Assertion Results

显示每个采样的标签和断言失败信息。**负载测试时不得使用。**

### 15. Graph Results

生成简单图形。**负载测试时不得使用。**

### 16. Comparison Assertion Visualizer

显示 Compare Assertion 元素的比较结果。

### 17. Sample Result Save Configuration

配置监听器保存到结果日志文件（JTL）的不同项目。

---

## 四、Configuration Elements（配置元素）

配置元素用于设置默认值和变量，供后续采样器使用。**只在放置的树分支内可访问。**

### 1. CSV Data Set Config

从文件读取行并拆分为变量。比 `__CSVRead()` 和 `__StringFromFile()` 函数更易用。

| 属性 | 说明 |
|------|------|
| Filename | 文件名 |
| File Encoding | 文件编码 |
| Variable Names | 变量名列表（逗号分隔） |
| Use first line as Variable Names | 使用首行作为变量名 |
| Delimiter | 分隔符 |
| Allow quoted data | 允许引号数据 |
| Recycle on EOF | 文件结束时循环 |
| Stop thread on EOF | 文件结束时停止线程 |
| Sharing mode | 共享模式 |

共享模式：

| 模式 | 说明 |
|------|------|
| All threads | 所有线程共享 |
| Current thread group | 当前线程组共享 |
| Current thread | 当前线程独占 |

### 2. HTTP Request Defaults

设置 HTTP 请求控制器使用的默认值。

| 属性 | 说明 |
|------|------|
| Server | 服务器名称 |
| Port | 端口 |
| Connect/Response Timeout | 连接/响应超时 |
| Implementation | 实现方式 |
| Protocol | 协议 |
| Content encoding | 内容编码 |
| Path | 路径 |
| Parameters | 参数 |
| Proxy settings | 代理设置 |
| Retrieve All Embedded Resources | 获取所有嵌入资源 |

### 3. HTTP Header Manager

添加或覆盖 HTTP 请求头。支持多个 Header Manager，头部条目会合并。

| 属性 | 说明 |
|------|------|
| Name (Header) | 头名称 |
| Value | 头值 |

### 4. HTTP Cookie Manager

存储和发送 Cookie（像 Web 浏览器一样）。每个 JMeter 线程有自己的 Cookie 存储区域。

| 属性 | 说明 |
|------|------|
| Clear Cookies each Iteration | 每次迭代清除 Cookie |
| Cookie Policy | Cookie 策略 |
| Implementation | 实现方式 |
| User-Defined Cookies | 用户定义的 Cookie |

### 5. HTTP Cache Manager

为 HTTP 请求添加缓存功能以模拟浏览器缓存。每个虚拟用户线程有自己的缓存，默认最多 5000 项。

| 属性 | 说明 |
|------|------|
| Clear cache each iteration | 每次迭代清除缓存 |
| Use Cache Control/Expires header | 使用缓存控制头 |
| Max Number of elements in cache | 缓存最大项数 |

### 6. HTTP Authorization Manager

为使用服务器认证的网页指定一个或多个用户登录信息。支持 BASIC、DIGEST 和 Kerberos 认证。

| 属性 | 说明 |
|------|------|
| Clear auth on each iteration | 每次迭代清除认证 |
| Base URL | 基础 URL |
| Username | 用户名 |
| Password | 密码 |
| Domain | 域 |
| Realm | 领域 |
| Mechanism | 认证机制（BASIC/DIGEST/Kerberos） |

### 7. DNS Cache Manager

允许测试使用负载均衡器（CDN 等）后有多台服务器的应用。每个线程每次迭代单独解析名称并保存到内部 DNS 缓存。**仅适用于 HTTPClient4 实现。**

| 属性 | 说明 |
|------|------|
| Clear cache each Iteration | 每次迭代清除缓存 |
| Use system/custom DNS resolver | 使用系统/自定义 DNS 解析器 |
| Hostname or IP address | DNS 服务器列表 |
| Static host table | 静态主机表 |

### 8. JDBC Connection Configuration

创建数据库连接（供 JDBC Request 采样器使用）。使用 DBCP 连接池。

| 属性 | 说明 |
|------|------|
| Variable Name for created pool | 连接池变量名 |
| Max Number of Connections | 最大连接数 |
| Max Wait | 最大等待时间 |
| Time Between Eviction Runs | 逐出运行间隔 |
| Auto Commit | 自动提交 |
| Transaction isolation | 事务隔离级别 |
| Pool Prepared Statements | 预编译语句池 |
| Preinit Pool | 预初始化连接池 |
| Init SQL statements | 初始化 SQL |
| Test While Idle | 空闲时测试 |
| Soft Min Evictable Idle Time | 软最小可逐出空闲时间 |
| Validation Query | 验证查询 |
| Database URL | 数据库 URL |
| JDBC Driver class | JDBC 驱动类 |
| Username | 用户名 |
| Password | 密码 |

### 9. FTP Request Defaults

设置 FTP 请求的默认值。

### 10. Java Request Defaults

设置 Java 测试的默认值。

### 11. LDAP Request Defaults

设置 LDAP 请求的默认值。

### 12. LDAP Extended Request Defaults

设置 LDAP 扩展请求的默认值。

### 13. TCP Sampler Config

设置 TCP 采样器的默认值。

### 14. User Defined Variables

允许用户定义一组变量。**所有线程共享相同的变量值。** 无论放在哪里，都在测试开始时处理。建议仅放在 Thread Group 的开始位置。

### 15. Random Variable

生成随机数字变量。

### 16. Counter

生成递增数字变量。每个线程可独立或共享计数器。

| 属性 | 说明 |
|------|------|
| Start | 起始值 |
| Increment | 增量 |
| Maximum | 最大值 |
| Format | 数字格式 |
| Track Counter Independently for each User | 每个用户独立跟踪 |
| Reset counter on each Thread Group Iteration | 每次迭代重置 |
| Variable Name | 变量名 |

### 17. Keystore Configuration

配置密钥库设置以进行客户端证书测试。

### 18. Login Config Element

设置登录和密码的默认值。

### 19. Simple Config Element

允许添加任意值到采样器请求中。

### 20. Bolt Connection Configuration

配置 Bolt 协议连接（Neo4j 数据库），供 Bolt Request 采样器使用。

---

## 五、Assertions（断言）

断言用于验证采样器返回的结果是否符合预期。**断言适用于其作用域内的所有采样器。** 要限制到单个采样器，将断言添加为该采样器的子元素。

### 1. Response Assertion

对响应的各个部分进行模式匹配验证。支持文本模式和正则表达式模式。

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| Field to check | 检查字段（文本/代码/消息/头等） |
| Pattern Match Rules | 模式匹配规则（包含/匹配/相等等） |
| Patterns to Test | 测试模式 |

### 2. Duration Assertion

验证响应是否在指定时间内完成。

| 属性 | 说明 |
|------|------|
| Duration in milliseconds | 持续时间（毫秒） |

### 3. Size Assertion

验证响应大小是否符合指定条件。

| 属性 | 说明 |
|------|------|
| Field to check | 检查字段 |
| Size in bytes | 大小（字节） |
| Type of Comparison | 比较类型（=、!=、>、<、>=、<=） |

### 4. XML Assertion

验证响应数据是否包含格式正确的 XML。

### 5. JSON Assertion

使用 JSON Path 表达式验证 JSON 响应数据。

| 属性 | 说明 |
|------|------|
| Assert JSON Path exists | 断言 JSON Path 存在 |
| JSON Path | JSON Path 表达式 |
| Expected Value | 期望值 |
| Match as regular expression | 作为正则表达式匹配 |
| Also assert | 额外断言 |

### 6. JSON JMESPath Assertion

使用 JMESPath 表达式验证 JSON 响应数据。

| 属性 | 说明 |
|------|------|
| JMESPath expression | JMESPath 表达式 |
| Expected Value | 期望值 |
| Match as regular expression | 作为正则表达式匹配 |

### 7. XPath Assertion

对文档应用 XPath 表达式并验证匹配结果。

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| XML Parsing Options | XML 解析选项 |
| XPath | XPath 表达式 |

### 8. XPath2 Assertion

使用 XPath2 查询语言验证响应。提供比 XPath Assertion 更好的命名空间管理和性能。

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| XPath2 expression | XPath2 表达式 |
| Namespaces aliases list | 命名空间别名列表 |

### 9. XML Schema Assertion

验证 XML 响应是否符合指定的 XML Schema 定义。

| 属性 | 说明 |
|------|------|
| File or URL of XML Schema | XML Schema 文件或 URL |

### 10. MD5Hex Assertion

验证响应数据的 MD5 哈希值。

| 属性 | 说明 |
|------|------|
| MD5Hex | 期望的 MD5 哈希值 |

### 11. HTML Assertion

使用 JTidy 验证响应数据的 HTML 语法。

| 属性 | 说明 |
|------|------|
| doctype | 文档类型 |
| format | 格式 |
| error threshold | 错误阈值 |
| warning threshold | 警告阈值 |
| error only | 仅错误 |
| filename | 文件名 |

### 12. BeanShell Assertion

使用 BeanShell 脚本执行断言。**建议迁移到 JSR223 Assertion + Groovy。**

### 13. JSR223 Assertion

使用 JSR223 脚本代码执行断言。

### 14. Compare Assertion

比较采样结果。

| 属性 | 说明 |
|------|------|
| Compare Content | 比较内容 |
| Compare Time | 比较时间 |
| Comparison Filters | 比较过滤器 |

### 15. SMIME Assertion

验证 SMIME 签名邮件消息。

| 属性 | 说明 |
|------|------|
| Verify Signature | 验证签名 |
| Signer Certificate | 签名者证书 |
| Signer Certificates from file | 文件中的签名者证书 |
| Signer by Serial Number | 按序列号签名 |
| Signer by email | 按邮箱签名 |
| Signer no check | 不检查签名者 |

---

## 六、Timers（定时器）

定时器在采样器之间引入延迟，模拟真实用户行为。**默认情况下 JMeter 线程连续执行采样器，不暂停。建议添加定时器。**

定时器在其**作用域内**的每个采样器**之前**引起延迟。多个定时器：JMeter 取所有定时器之和作为延迟时间。

### 1. Constant Timer

在每个采样之间添加固定延迟时间。

| 属性 | 说明 |
|------|------|
| Thread Delay (in milliseconds) | 延迟时间（毫秒） |

### 2. Gaussian Random Timer

添加高斯分布的随机延迟时间。延迟时间大部分集中在偏差值附近。

| 属性 | 说明 |
|------|------|
| Deviation (in milliseconds) | 偏差（毫秒） |
| Constant Delay Offset (in milliseconds) | 固定延迟偏移（毫秒） |

### 3. Uniform Random Timer

添加均匀分布的随机延迟时间。

| 属性 | 说明 |
|------|------|
| Random Delay Maximum (in milliseconds) | 最大随机延迟（毫秒） |
| Constant Delay Offset (in milliseconds) | 固定延迟偏移（毫秒） |

### 4. Constant Throughput Timer

根据指定的吞吐量控制采样频率，引入可变延迟以维持目标吞吐量。

| 属性 | 说明 |
|------|------|
| Target throughput (in samples per minute) | 目标吞吐量（样本/分钟） |
| Calculate Throughput based on | 计算吞吐量的基准 |

### 5. Precise Throughput Timer

生成精确吞吐量的定时器，比 Constant Throughput Timer 更精确。

| 属性 | 说明 |
|------|------|
| Target throughput (samples per minute) | 目标吞吐量 |
| Throughput period | 吞吐量周期 |
| Number of threads | 线程数 |
| Test duration | 测试持续时间 |
| Random seed | 随机种子 |

### 6. Synchronizing Timer

阻塞线程直到指定数量的线程到达后同时释放，模拟并发用户同时发起请求。

| 属性 | 说明 |
|------|------|
| Number of Simulated Users to Group by | 分组模拟用户数 |
| Timeout in milliseconds | 超时时间（毫秒） |

### 7. Poisson Random Timer

添加泊松分布的随机延迟时间。

| 属性 | 说明 |
|------|------|
| Lambda (in milliseconds) | Lambda 值（毫秒） |
| Constant Delay Offset (in milliseconds) | 固定延迟偏移（毫秒） |

### 8. BeanShell Timer

使用 BeanShell 脚本计算延迟时间。**建议迁移到 JSR223 Timer + Groovy。**

### 9. JSR223 Timer

使用 JSR223 脚本计算延迟时间。

---

## 七、Pre Processors（前置处理器）

前置处理器在采样器执行之前运行，用于修改采样器设置或准备数据。

### 1. HTML Link Parser

解析 HTML 响应以提取链接和表单信息。

### 2. HTTP URL Re-writing Modifier

修改 HTTP 请求以包含会话 ID 信息，用于使用 URL 重写维护会话的应用。

| 属性 | 说明 |
|------|------|
| Session Argument Name | 会话参数名 |
| Path Extension | 路径扩展 |
| Do not use equals | 不使用等号 |
| Do not use questionmark | 不使用问号 |
| Cache Session Id | 缓存会话 ID |

### 3. User Parameters

为每个用户（线程）定义变量值。每个线程可使用不同的值。

| 属性 | 说明 |
|------|------|
| Name | 名称 |
| User Variables (per thread) | 每线程用户变量 |

### 4. BeanShell PreProcessor

在采样前使用 BeanShell 脚本进行处理。**建议迁移到 JSR223 PreProcessor + Groovy。**

### 5. JSR223 PreProcessor

在采样前使用 JSR223 脚本进行处理。

### 6. JDBC PreProcessor

在采样运行前执行 SQL 语句。适用于 JDBC 采样需要数据库中预先存在数据的情况。

### 7. RegEx User Parameters

使用正则表达式从另一个 HTTP 请求提取的动态值指定 HTTP 参数。

| 属性 | 说明 |
|------|------|
| Regular Expression Reference Name | 正则表达式引用名 |
| Parameter names regexp group number | 参数名正则组号 |
| Parameter values regex group number | 参数值正则组号 |

### 8. Sample Timeout

如果采样耗时过长则中断。采样器必须实现 Interruptible 接口。

| 属性 | 说明 |
|------|------|
| Sample Timeout | 采样超时时间 |

---

## 八、Post-Processors（后置处理器）

后置处理器在采样器之后应用，用于从响应中提取数据。

### 1. Regular Expression Extractor

使用 Perl 类型正则表达式从服务器响应中提取值。

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| Field to check | 检查字段 |
| Name of created variable | 创建的变量名 |
| Regular Expression | 正则表达式 |
| Template | 模板（如 `$1$`） |
| Match No. | 匹配编号（0=随机/正数=第N个/-1=全部） |
| Default Value | 默认值 |
| Use empty default value | 使用空默认值 |

### 2. CSS Selector Extractor

使用 CSS 选择器语法从 HTML 响应中提取值。支持 JSoup 和 Jodd-Lagarto 两种实现。

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| CSS Selector Implementation | CSS 选择器实现 |
| Name of created variable | 创建的变量名 |
| CSS/JQuery expression | CSS/JQuery 表达式 |
| Attribute | 属性名 |
| Match No. | 匹配编号 |
| Default Value | 默认值 |

### 3. JSON Extractor

使用 JSON-PATH 语法从 JSON 响应中提取数据。支持多个变量和表达式。

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| Names of created variables | 创建的变量名列表 |
| JSON Path Expressions | JSON Path 表达式列表 |
| Default Values | 默认值列表 |
| Match Numbers | 匹配编号列表 |
| Compute concatenation var | 计算拼接变量 |

### 4. JSON JMESPath Extractor

使用 JMESPath 查询语言从 JSON 响应中提取值。

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| Name of created variable | 创建的变量名 |
| JMESPath expressions | JMESPath 表达式 |
| Match No. | 匹配编号 |
| Default Value | 默认值 |

### 5. XPath2 Extractor

使用 XPath2 查询语言从结构化响应中提取值。**自 JMeter 5.0 起推荐使用。**

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| Return entire XPath fragment | 返回整个 XPath 片段 |
| Name of created variable | 创建的变量名 |
| XPath Query | XPath 查询 |
| Match No. | 匹配编号 |
| Default Value | 默认值 |
| Namespaces aliases list | 命名空间别名列表 |

### 6. XPath Extractor

使用 XPath 查询语言从结构化响应中提取值。**自 JMeter 5.0 起推荐使用 XPath2 Extractor。**

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| Use Tidy | 使用 Tidy |
| Quiet | 静默模式 |
| Report Errors | 报告错误 |
| Show warnings | 显示警告 |
| Use Namespaces | 使用命名空间 |
| Validate XML | 验证 XML |
| Ignore Whitespace | 忽略空白 |
| Fetch External DTDs | 获取外部 DTD |
| Return entire XPath fragment | 返回整个 XPath 片段 |
| Name of created variable | 创建的变量名 |
| XPath Query | XPath 查询 |
| Match No. | 匹配编号 |
| Default Value | 默认值 |

### 7. Boundary Extractor

使用左右边界从服务器响应中提取值。无需正则表达式，更简单高效。

| 属性 | 说明 |
|------|------|
| Apply to | 应用范围 |
| Field to check | 检查字段 |
| Name of created variable | 创建的变量名 |
| Left Boundary | 左边界 |
| Right Boundary | 右边界 |
| Match No. | 匹配编号 |
| Default Value | 默认值 |

### 8. Result Status Action Handler

当相关采样器失败时停止线程或整个测试。

| 属性 | 说明 |
|------|------|
| Action to be taken after a Sampler error | 采样器错误后的操作 |

操作选项：

| 操作 | 说明 |
|------|------|
| Continue | 继续 |
| Start next thread loop | 开始下一线程循环 |
| Stop Thread | 停止线程 |
| Stop Test | 停止测试 |
| Stop Test Now | 立即停止测试 |

### 9. BeanShell PostProcessor

在采样后使用 BeanShell 脚本处理。**建议迁移到 JSR223 PostProcessor + Groovy。**

### 10. JSR223 PostProcessor

在采样后使用 JSR223 脚本处理。

### 11. JDBC PostProcessor

在采样运行后执行 SQL 语句。适用于重置 JDBC 采样更改的数据状态。

---

## 九、Miscellaneous Features（杂项功能）

### 1. Test Plan

指定测试的整体设置。

| 属性 | 说明 |
|------|------|
| Functional Testing Mode | 功能测试模式（捕获完整响应数据） |
| Run Thread Groups consecutively | 串行运行线程组 |
| Run tearDown Thread Groups after shutdown | 关闭后运行 tearDown 线程组 |
| Classpath | 类路径设置 |

### 2. Thread Group

定义执行特定测试用例的用户池。

| 属性 | 说明 |
|------|------|
| Action after Sampler error | 采样器错误后的操作 |
| Number of Threads | 线程数 |
| Ramp-up Period | Ramp-up 时间（秒） |
| Same user on each iteration | 每次迭代使用相同用户 |
| Loop Count | 循环次数 |
| Delay Thread creation | 延迟线程创建 |
| Specify Thread lifetime | 指定线程生命周期 |
| Duration | 持续时间（秒） |
| Startup delay | 启动延迟（秒） |

### 3. setUp Thread Group

特殊线程组，用于执行测试前操作。**在常规线程组之前执行。**

### 4. tearDown Thread Group

特殊线程组，用于执行测试后操作。**在常规线程组完成后执行。** 默认在优雅关闭时不运行。

### 5. Test Fragment

与 Include Controller 和 Module Controller 配合使用。不会被执行，除非被引用。

### 6. HTTP(S) Test Script Recorder

允许 JMeter 拦截和记录浏览器操作。作为 HTTP(S) 代理服务器实现，支持动态证书生成。

| 属性 | 说明 |
|------|------|
| Port | 代理端口 |
| HTTPS Domains | HTTPS 域名 |
| Target Controller | 目标控制器 |
| Grouping | 分组方式 |
| Capture HTTP Headers | 捕获 HTTP 头 |
| Add Assertions | 添加断言 |
| Regex Matching | 正则匹配 |
| Prefix/Transaction name | 前缀/事务名 |
| Naming scheme | 命名方案 |
| Content Type filter | 内容类型过滤 |
| Patterns to Include/Exclude | 包含/排除模式 |
| Redirect/Follow settings | 重定向设置 |

### 7. Debug Sampler

生成包含所有 JMeter 变量和/或属性值的样本。可在 View Results Tree 中查看。

| 属性 | 说明 |
|------|------|
| JMeter Properties | 显示 JMeter 属性 |
| JMeter Variables | 显示 JMeter 变量 |
| System Properties | 显示系统属性 |

### 8. Debug PostProcessor

创建包含前一个采样器属性、JMeter 变量、属性和/或系统属性的子样本。

---

## 执行顺序

JMeter 测试元素严格按以下顺序执行：

1. **Configuration elements**（配置元素）
2. **Pre-Processors**（前置处理器）
3. **Timers**（定时器）
4. **Sampler**（采样器）
5. **Post-Processors**（后置处理器，除非 SampleResult 为 null）
6. **Assertions**（断言，除非 SampleResult 为 null）
7. **Listeners**（监听器，除非 SampleResult 为 null）

### 作用域规则

- **层次型元素**：Listeners、Config Elements、Post-Processors、Pre-Processors、Assertions、Timers
  - 如果父元素是请求，则应用于该请求
  - 如果父元素是控制器，则影响该控制器的所有后代请求
- **有序型元素**：Controllers、Samplers — 按树中出现的顺序处理
- **配置元素特殊规则**：
  - Configuration Default 元素的设置会合并到 Sampler 可访问的值集中
  - Manager 类元素（Header Manager、Cookie Manager、Authorization Manager）的设置**不会合并**
