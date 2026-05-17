# JMeter 最佳实践

基于 Apache JMeter 官方文档（xdocs/usermanual/best-practices.xml、test_plan.xml、hints_and_tips.xml、glossary.xml）整理。

---

## 一、通用最佳实践

### 1. 始终使用最新版本的 JMeter

- JMeter 性能在持续改进，强烈建议使用最新版本
- 应始终阅读变更列表以了解新改进和新组件
- **绝对避免**使用比最新版本早 3 个版本以上的旧版本

### 2. 使用正确的线程数

- 硬件能力和测试计划设计都会影响可运行的线程数
- 服务器越快，JMeter 工作越辛苦（因为响应返回更快），需要更多资源
- 线程数设置不当会导致"协调遗漏"(Coordinated Omission) 问题
- 大规模负载测试建议：在多台机器上运行多个 CLI 模式的 JMeter 实例
- 可使用 **JavaTest 采样器**测试 JMeter 在特定平台上的性能（无需网络访问）
- JMeter 支持延迟线程创建（直到线程开始采样时才创建），允许非常大的总线程数

### 3. 减少资源消耗

- **使用 CLI 模式**：`jmeter -n -t test.jmx -l test.jtl`
- **尽量少用 Listener**；使用 `-l` 标志时可删除或禁用所有 Listener
- **负载测试期间不要使用** View Results Tree 或 View Results in Table
- 使用循环+变量（CSV Data Set）代替大量相似采样器
- 不要使用功能模式 (Functional Mode)
- **使用 CSV 输出而非 XML**
- 只保存需要的数据
- 尽量少用断言 (Assertions)
- **使用性能最好的脚本语言**（Groovy > JEXL3 > JavaScript > BeanShell）
- 大量测试数据应预先创建在文件中，用 CSV Dataset 读取

### 4. 管理属性

- **不要直接修改 `jmeter.properties` 文件**
- 应将属性从 `jmeter.properties` 复制到 `user.properties` 文件中修改
- 这样做便于迁移到下一个 JMeter 版本
- `user.properties` 中的属性会覆盖 `jmeter.properties` 中定义的属性

### 5. 废弃元素

- 不要使用废弃元素（在变更列表和组件参考中标记为废弃）
- 废弃元素在版本 N 中从菜单中移除，但可通过 `not_in_menu` 属性重新启用
- **版本 N 中的废弃元素将在版本 N+1 中被永久移除**

---

## 二、脚本相关最佳实践

### 1. JSR223 元素 + Groovy

- 对于高强度负载测试，推荐使用实现了 `Compilable` 接口的脚本语言
- **Groovy** 实现了 `Compilable`；BeanShell 和 JavaScript 未实现，应避免用于高强度负载测试
- **重要**：勾选"Cache compiled script if available"属性
- **关键警告**：使用脚本缓存时，不要在脚本中使用 `${varName}` 方式引用变量（缓存只会取第一次的值），应改用 `vars.get("varName")`

```groovy
// 错误 - 缓存后值不会更新
def name = "${username}"

// 正确 - 使用 vars.get()
def name = vars.get("username")
```

### 2. 自 BeanShell 迁移到 JSR223 + Groovy

- 自 JMeter 3.1 起，建议从 BeanShell 切换到 JSR223 测试元素
- 从 `__Beanshell` 函数切换到 `__groovy` 函数
- 每个 BeanShell 测试元素有自己的解释器副本（每个线程）
- 长时间运行的测试可能导致解释器占用大量内存

### 3. 使用 Groovy 或 Jexl3 开发脚本函数

- 建议使用 Apache Groovy 或任何支持 JSR223 `Compilable` 接口的语言
- 开发方法：创建包含 JSR223 Sampler 和 Tree View Listener 的简单测试计划
- 脚本正常工作后，可存储为 Test Plan 变量
- 例如：Groovy 脚本存储在变量 `RANDOM_NAME` 中，函数调用为 `${__groovy(${RANDOM_NAME})}`

---

## 三、参数化测试

### 1. 使用 Test Plan 变量

定义 Test Plan 变量，在测试元素中引用：

```
LOOPS=10
```

在 Thread Group 中引用 `${LOOPS}`。

### 2. 使用属性参数化（推荐）

CLI 模式下更高效的方式：将变量定义为属性：

```
LOOPS=${__P(loops,10)}
HOST=${__P(host,www.example.com)}
THREADS=${__P(threads,10)}
```

命令行覆盖：

```bash
jmeter ... -Jhost=www3.example.org -Jloops=13 -Jthreads=50
```

### 3. 使用 CSV Data Set

使用 CSV Data Set 实现不同线程使用不同值（如唯一登录）：

1. 创建包含用户名和密码的文本文件（逗号分隔）
2. 添加 CSV DataSet 配置元素，命名变量为 `USER` 和 `PASS`
3. 在采样器中用 `${USER}` 和 `${PASS}` 替换登录名和密码

CSV Data Set 元素会为每个线程读取新行。

### 4. 使用属性文件集

大量属性需同时修改时，使用属性文件集，通过 `-q` 命令行选项传入：

```bash
jmeter -n -t test.jmx -l result.jtl -q prod.properties
```

---

## 四、变量共享

### 变量 vs 属性

| 特性 | 变量 | 属性 |
|------|------|------|
| 作用域 | 线程局部 | 全局 |
| 定义位置 | Test Plan、UDV、CSV Data Set | jmeter.properties、user.properties |
| 线程间共享 | 不可以 | 可以 |
| 运行时修改 | 仅影响当前线程 | 影响所有线程 |
| 引用方式 | `${varName}` | `${__P(propName)}` 或 `${__property(propName,,)}` |

### 线程间传递变量

JMeter 变量具有线程作用域（这是设计如此，使线程独立运行）。传递变量的方法：

1. **使用属性**：一个线程用 `__setProperty` 设置属性，另一个线程用 `__P` 读取
2. **使用文件**：一个线程写文件，另一个线程读文件
3. **使用 CSV Dataset**：如果数据可在测试开始前确定

### 跨线程共享变量（BeanShell/Groovy）

```java
import org.apache.jmeter.util.JMeterUtils;
String value = JMeterUtils.getPropDefault("name","");
JMeterUtils.setProperty("name", "value");
```

---

## 五、测试计划结构

### 执行顺序

严格按以下顺序执行：

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

### 线程组配置建议

- **Ramp-up 时间**：初始建议 Ramp-up = 线程数，然后根据需要调整
  - 应足够长以避免测试开始时工作负载过大
  - 足够短以使最后线程在第一个线程完成前开始运行
- **错误处理**：`on_sample_error` 设置
  - `continue`：继续执行（适用于大多数场景）
  - `startnextloop`：开始下一循环
  - `stopthread`：停止当前线程
  - `stoptest`/`stoptestnow`：停止测试

### 定时器使用

- 默认情况下 JMeter 线程连续执行采样器，不暂停
- **建议添加定时器**指定延迟，否则 JMeter 可能在极短时间内发出过多请求
- 定时器在其**作用域内**的每个采样器**之前**引起延迟
- 多个定时器：JMeter 取所有定时器之和作为延迟时间
- 定时器可作为采样器或控制器的子元素以限制作用范围

### 断言使用

- 断言适用于其作用域内的所有采样器
- 要限制到单个采样器，将断言添加为该采样器的子元素
- 尽量少用断言以减少资源消耗

---

## 六、HTTP(S) Test Script Recorder 使用

### 过滤请求

**最重要的操作**：过滤掉不感兴趣的请求（如图片请求）。

- 使用 Include Pattern 包含特定扩展名：`.*\.jsp`、`.*\.asp`、`.*\.php`
- 使用 Exclude Pattern 排除特定扩展名：`.*\.gif`，也可能需要排除样式表、JavaScript 文件等

### 变量替换功能

在 Test Plan 级别或 User Defined Variables 中定义变量，JMeter 会自动替换录制样本中的值：

- 例如定义 `server=xxx.example.com`，录制样本中的该值会被替换为 `${server}`
- **注意**：匹配区分大小写

### 常见问题

- 如果 JMeter 未录制任何样本，检查浏览器是否真的使用了代理
- 某些浏览器会忽略 `localhost` 或 `127.0.0.1` 的代理设置，尝试使用本地主机名或 IP
- `unknown_ca` 错误通常意味着浏览器未接受 JMeter 代理服务器证书

---

## 七、Cookie Manager 和 Authorization Manager

### Cookie Manager 放置位置

- 应添加到所有 Web 测试中
- 放在 Thread Group 级别确保所有 HTTP 请求共享相同 cookies
- 每个线程有自己的 Cookie 存储区域

### Authorization Manager 放置位置

- 放在需要认证的请求附近
- 支持 BASIC、DIGEST 和 Kerberos 认证

---

## 八、调试技巧

### 启用调试日志

- GUI 模式下：选择测试元素，使用 Help 菜单启用/禁用日志
- 查看日志消息：菜单 Options > Log Viewer
- 默认日志控制台禁用，启用方法：`jmeter.loggerpanel.display=true`
- 限制日志面板字符数：`jmeter.loggerpanel.maxlength=80000`

### 搜索功能

- 自 2.6 版本起提供搜索功能（Menu Search）
- 选项：Case sensitive（区分大小写）、Regular exp.（正则表达式）

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+0 | Thread Group |
| Ctrl+1 | HTTP Request |
| Ctrl+2 | Regular Expression Extractor |
| Ctrl+3 | Response Assertion |
| Ctrl+4 | Constant Timer |
| Ctrl+5 | Test Action |
| Ctrl+6 | JSR223 PostProcessor |
| Ctrl+7 | JSR223 PreProcessor |
| Ctrl+8 | Debug Sampler |
| Ctrl+9 | View Results Tree |

### 自动保存配置

- 自 JMeter 3.0 起，自动保存最多 10 个 jmx 文件备份
- 备份保存在 `${JMETER_HOME}/backups` 子文件夹

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `jmeter.gui.action.save.backup_on_save` | true | 启用自动备份 |
| `jmeter.gui.action.save.backup_directory` | `${JMETER_HOME}/backups` | 备份目录 |
| `jmeter.gui.action.save.keep_backup_max_hours` | 0 | 最大保留时间 |
| `jmeter.gui.action.save.keep_backup_max_count` | 10 | 最大备份数量 |

---

## 九、术语表

### Elapsed Time（经过时间/耗时）

JMeter 从**发送请求之前**到**接收到最后一个响应之后**的时间。**不包括**渲染响应的时间，也不处理任何客户端代码（如 JavaScript）。

### Latency（延迟时间）

JMeter 从**发送请求之前**到**接收到第一个响应之后**的时间。包含组装请求和组装响应第一部分所需的处理时间。

### Connect Time（连接时间）

建立连接所需的时间，包括 SSL 握手。**连接时间不会自动从延迟时间中减去。** 自 JMeter 3.1 起，仅对 TCP Sampler、HTTP Request 和 JDBC Request 计算。

### Median（中位数）

将样本分成两等分的数值。等同于第 50 百分位数。

### 90% Line（第 90 百分位数）

90% 的样本低于此值。

### Standard Deviation（标准差）

JMeter 计算的是**总体标准差**（STDEVP），而非样本标准差（STDEV）。

### Thread Name（线程名称）

格式：`groupName + " " + groupIndex + "-" + threadIndex`

示例：
```
Thread Group 1-1
Thread Group 1-2
Thread Group 2-1
Thread Group 2-2
```

### Throughput（吞吐量）

计算公式：**吞吐量 = 请求数 / 总时间**

时间从第一个样本开始到最后一个样本结束。包含样本之间的间隔时间，旨在代表服务器上的负载。
