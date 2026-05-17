# JMeter 内置函数完整参考

基于 Apache JMeter 官方文档（xdocs/usermanual/functions.xml）整理，涵盖 JMeter 5.x 全部 49 个内置函数。

## 函数调用格式

```
${__functionName(var1,var2,var3)}
```

无参数函数可省略括号：`${__threadNum}`

### 重要注意事项

- **逗号转义**：函数参数中包含逗号时须用 `\` 转义，如 `${__time(EEE\, d MMM yyyy)}`
- **大小写敏感**：变量、函数和属性均区分大小写
- **空格修剪**：JMeter 使用前会修剪变量名中的空格
- **未定义引用**：引用未定义的函数或变量时，JMeter 不报错，原样返回引用字符串
- **Windows 路径**：使用 `\` 须转义为 `\\`，或直接使用 `/` 作为路径分隔符
- **嵌套变量**：不支持 `${Var${N}}`，需使用 `${__V(Var${N})}` 实现

---

## 一、Information（信息类）

### `__threadNum`

返回当前正在执行的线程编号。编号在线程组内局部唯一。

```
${__threadNum}
```

**注意**：在配置元素（如用户定义变量）和测试计划中不可用。

### `__threadGroupName`

返回当前正在执行的线程组名称。自 4.1 起可用。

```
${__threadGroupName}
```

### `__samplerName`

返回当前采样器的名称（标签）。

| 参数 | 必填 | 说明 |
|------|------|------|
| Variable Name | 否 | 引用名称 |

```
${__samplerName()}
${__samplerName(refName)}
```

### `__machineIP`

返回本机 IP 地址。

| 参数 | 必填 | 说明 |
|------|------|------|
| Variable Name | 否 | 引用名称 |

```
${__machineIP()}
```

### `__machineName`

返回本机主机名。

| 参数 | 必填 | 说明 |
|------|------|------|
| Variable Name | 否 | 引用名称 |

```
${__machineName()}
```

### `__time`

以多种格式返回当前时间。省略格式则返回自 epoch 以来的毫秒数。

| 参数 | 必填 | 说明 |
|------|------|------|
| Format | 否 | 时间格式字符串 |
| Name of variable | 否 | 存储结果的变量名 |

格式别名：
- `YMD` = `yyyyMMdd`
- `HMS` = `HHmmss`
- `YMDHMS` = `yyyyMMdd-HHmmss`
- `USER1`、`USER2`：自定义格式
- `/ddd`：毫秒数除以 ddd

```
${__time()}          → 1634567890123
${__time(YMD)}       → 20211018
${__time(YMDHMS)}    → 20211018-143210
${__time(yyyy-MM-dd)}
```

### `__timeShift`

返回指定格式日期加上指定偏移量后的日期。

| 参数 | 必填 | 说明 |
|------|------|------|
| Format | 否 | DateTimeFormatter 格式 |
| Date to shift | 否 | 要偏移的日期，省略则为当前时间 |
| Value to shift | 否 | ISO 8601 持续时间格式 |
| Locale | 否 | 区域设置 |
| Name of variable | 否 | 存储结果的变量名 |

偏移量格式（ISO 8601）：
- `P2D` = 2 天
- `PT10H` = 10 小时
- `-P6H3M` = -6 小时 -3 分

```
${__timeShift(yyyy-MM-dd,,P2D,,)}     → 当前日期 + 2 天
${__timeShift(yyyy-MM-dd,,-P1D,,)}    → 当前日期 - 1 天
```

### `__log`

记录一条日志消息，并返回其输入字符串。

| 参数 | 必填 | 说明 |
|------|------|------|
| String to be logged | 是 | 要记录的字符串 |
| Log Level | 否 | OUT/ERR/DEBUG/INFO(默认)/WARN/ERROR |
| Throwable text | 否 | 若非空，创建 Throwable |
| Comment | 否 | 注释 |

```
${__log(This is a message)}
${__log(This is a message,,,)ERROR}
```

### `__logn`

记录一条日志消息，返回空字符串（与 `__log` 的区别在于返回值）。

| 参数 | 必填 | 说明 |
|------|------|------|
| String to be logged | 是 | 要记录的字符串 |
| Log Level | 否 | OUT/ERR/DEBUG/INFO(默认)/WARN/ERROR |
| Throwable text | 否 | 若非空，创建 Throwable |

---

## 二、Input（输入类）

### `__StringFromFile`

从文本文件逐行读取字符串。每次调用读取下一行，所有线程共享同一实例。到达文件末尾时从头开始。

| 参数 | 必填 | 说明 |
|------|------|------|
| File Name | 是 | 文件路径，支持 DecimalFormat 序列号格式 |
| Variable Name | 否 | 引用名称 |
| Start sequence number | 否 | 起始序列号 |
| End sequence number | 否 | 结束序列号 |

```
${__StringFromFile(data/test.txt,,,)}
${__StringFromFile(data/test###.txt,myVar,1,10)}
```

### `__FileToString`

读取整个文件内容。每次调用读取整个文件。

| 参数 | 必填 | 说明 |
|------|------|------|
| File Name | 是 | 文件路径 |
| File encoding | 否 | 文件编码 |
| Variable Name | 否 | 引用名称 |

```
${__FileToString(data/payload.json,UTF-8,)}
```

### `__CSVRead`

从 CSV 文件读取字符串。文件首次遇到时被读入内部数组。

| 参数 | 必填 | 说明 |
|------|------|------|
| File Name | 是 | 文件名或 `*ALIAS` |
| Column number | 是 | 列号（0=第一列）；`next` 转到下一行；`*ALIAS` 分配别名 |

```
${__CSVRead(data/users.csv,0)}       → 读取第一列
${__CSVRead(data/users.csv,1)}       → 读取第二列
${__CSVRead(data/users.csv,next)}    → 移到下一行
```

### `__XPath`

读取 XML 文件并匹配 XPath 表达式。每次调用返回下一个匹配项。

| 参数 | 必填 | 说明 |
|------|------|------|
| XML file to parse | 是 | XML 文件路径 |
| XPath | 是 | XPath 表达式 |

```
${__XPath(data/config.xml,//server/@host)}
```

### `__StringToFile`

将字符串写入文件。自 5.2 起可用。

| 参数 | 必填 | 说明 |
|------|------|------|
| Path to file | 是 | 文件绝对路径 |
| String to write | 是 | 要写入的字符串，`\n` 表示换行 |
| Append to file? | 否 | true=追加(默认)，false=覆盖 |
| File encoding | 否 | 文件编码，默认 UTF-8 |

```
${__StringToFile(/tmp/output.txt,Hello World\n,true,UTF-8)}
```

---

## 三、Calculation（计算类）

### `__counter`

生成递增数字，从 1 开始每次 +1。最大值 2,147,483,647。

| 参数 | 必填 | 说明 |
|------|------|------|
| First argument | 是 | TRUE=每个线程独立计数，FALSE=全局计数 |
| Second argument | 否 | 引用名称 |

```
${__counter(TRUE,)}    → 每线程独立计数
${__counter(FALSE,)}   → 全局计数
```

### `__intSum`

计算两个或多个整数值的和。

| 参数 | 必填 | 说明 |
|------|------|------|
| First argument | 是 | 第一个 int 值 |
| Second argument | 是 | 第二个 int 值 |
| nth argument | 否 | 第 n 个 int 值 |
| last argument | 否 | 引用名称 |

```
${__intSum(1,2,3,varName)}    → varName = 6
```

### `__longSum`

计算两个或多个 long 值的和。当值超出 int 范围时使用。

```
${__longSum(2147483648,1,varName)}
```

### `__Random`

返回 min 和 max 之间的随机整数。

| 参数 | 必填 | 说明 |
|------|------|------|
| Minimum value | 是 | 最小值 |
| Maximum value | 是 | 最大值 |
| Variable Name | 否 | 引用名称 |

```
${__Random(1,100,randVar)}    → 1-100 之间的随机数
```

### `__RandomDate`

返回指定起止日期范围内的随机日期。

| 参数 | 必填 | 说明 |
|------|------|------|
| Time format | 否 | DateTimeFormatter 格式，默认 yyyy-MM-dd |
| Start date | 否 | 起始日期，默认当前时间 |
| End date | 是 | 结束日期 |
| Locale | 否 | 区域设置 |
| Name of variable | 否 | 存储结果的变量名 |

```
${__RandomDate(yyyy-MM-dd,2024-01-01,2024-12-31,,)}
```

### `__RandomString`

返回指定长度的随机字符串。

| 参数 | 必填 | 说明 |
|------|------|------|
| Length | 是 | 字符串长度 |
| Characters to use | 否 | 字符集 |
| Variable Name | 否 | 引用名称 |

```
${__RandomString(10,abcdefghijklmnopqrstuvwxyz,)}
```

### `__RandomFromMultipleVars`

基于 `|` 分隔的多个变量值中随机返回一个值。

| 参数 | 必填 | 说明 |
|------|------|------|
| Source Variables | 是 | 用 `|` 分隔的变量名列表 |
| Variable Name | 否 | 引用名称 |

```
${__RandomFromMultipleVars(VAR1|VAR2|VAR3,)}
```

### `__UUID`

返回一个伪随机的 Type 4 UUID。

```
${__UUID()}    → 如 0b3a5b0f-2e4d-4c5a-8f6e-1d2c3b4a5e6f
```

### `__digest`

使用指定哈希算法生成加密摘要值。

| 参数 | 必填 | 说明 |
|------|------|------|
| Algorithm | 是 | MD2/MD5/SHA-1/SHA-224/SHA-256/SHA-384/SHA-512 |
| String to encode | 是 | 要加密的字符串 |
| Salt to add | 否 | 盐值 |
| Upper Case value | 否 | true=大写 |
| Name of variable | 否 | 存储结果的变量名 |

```
${__digest(MD5,hello,,,)}           → 小写 MD5
${__digest(SHA-256,hello,,,true)}   → 大写 SHA-256
```

---

## 四、Formatting（格式化类）

### `__dateTimeConvert`

将日期从源格式转换为目标格式。

| 参数 | 必填 | 说明 |
|------|------|------|
| Date String | 是 | 要转换的日期字符串 |
| Source Date Format | 否 | 原始格式（空则 Date String 须为 epoch） |
| Target Date Format | 是 | 目标格式 |
| Name of variable | 否 | 存储结果的变量名 |

```
${__dateTimeConvert(2024-01-15,yyyy-MM-dd,dd/MM/yyyy,)}
```

---

## 五、Scripting（脚本类）

### `__groovy`（推荐）

执行 Apache Groovy 脚本并返回结果。**推荐用于高性能场景。**

| 参数 | 必填 | 说明 |
|------|------|------|
| Expression to evaluate | 是 | Groovy 表达式，含逗号须转义为 `\,` |
| Name of variable | 否 | 引用名称 |

可用变量：`log`、`ctx`、`vars`、`props`、`threadName`、`sampler`、`prev`、`OUT`

**最佳实践**：使用 `vars.get("myVar")` 而非 `"${myVar}"` 以确保脚本可缓存。

```
${__groovy(${RANDOM_NAME})}
${__groovy(vars.get("myVar").length(),)}
```

### `__BeanShell`

执行 BeanShell 脚本。**性能不如 `__groovy`，建议优先使用 `__groovy`。**

| 参数 | 必填 | 说明 |
|------|------|------|
| BeanShell script | 是 | BeanShell 脚本 |
| Name of variable | 否 | 引用名称 |

### `__javaScript`

执行 JavaScript 表达式。**性能不如 `__jexl3` 或 `__groovy`。**

| 参数 | 必填 | 说明 |
|------|------|------|
| Expression | 是 | JavaScript 表达式 |
| Variable Name | 否 | 引用名称 |

```
${__javaScript(Math.floor(Math.random()*10),)}
```

### `__jexl2`

使用 Commons JEXL 2 评估表达式。

```
${__jexl2(${a} > ${b},)}
```

### `__jexl3`（推荐用于条件表达式）

使用 Commons JEXL 3 评估表达式。

```
${__jexl3(${a} > ${b},)}
${__jexl3(${count} >= 10 && ${success} == true,)}
```

---

## 六、Properties（属性类）

属性全局共享，可用于线程间通信。

### `__isPropDefined`

判断属性是否存在。

```
${__isPropDefined(myProp)}    → true/false
```

### `__property`

读取 JMeter 属性值。

| 参数 | 必填 | 说明 |
|------|------|------|
| Property Name | 是 | 属性名 |
| Variable Name | 否 | 引用名称 |
| Default Value | 否 | 默认值 |

```
${__property(host,,localhost)}    → 读取 host 属性，默认 localhost
```

### `__P`

简化版属性读取函数，专用于命令行定义的属性。无默认值时默认为 `1`。

| 参数 | 必填 | 说明 |
|------|------|------|
| Property Name | 是 | 属性名 |
| Default Value | 否 | 默认值（省略则为 1） |

```
${__P(concurrency,10)}    → 读取 concurrency 属性，默认 10
${__P(loops)}             → 读取 loops 属性，默认 1
```

### `__setProperty`

设置 JMeter 属性值。默认返回空字符串。

| 参数 | 必填 | 说明 |
|------|------|------|
| Property Name | 是 | 属性名 |
| Property Value | 是 | 属性值 |
| True/False | 否 | true=返回旧值 |

```
${__setProperty(global_counter,${counter},)}
${__setProperty(global_counter,newValue,true)}    → 返回旧值
```

---

## 七、Variables（变量类）

变量是线程局部的，一个线程设置的变量不能被另一个线程读取。

### `__isVarDefined`

判断变量是否存在。

```
${__isVarDefined(myVar)}    → true/false
```

### `__split`

按分隔符拆分字符串。拆分结果存入 `${VAR_1}`、`${VAR_2}` 等，变量计数存入 `${VAR_n}`。

| 参数 | 必填 | 说明 |
|------|------|------|
| String to split | 是 | 要拆分的字符串 |
| Name of variable | 是 | 引用名称 |
| Delimiter | 否 | 分隔符，默认 `,` |

```
${__split(a|b|c,VAR,|)}    → VAR_1=a, VAR_2=b, VAR_3=c, VAR_n=3
```

### `__eval`

对字符串表达式进行求值，插值其中的变量和函数引用。

```
${__eval(${SQL})}    → 替换 SQL 变量中的所有嵌套引用
```

### `__evalVar`

对存储在变量中的表达式进行求值。与 `__eval` 类似，但直接传变量名。

```
${__evalVar(query)}    → 替换 query 变量中的变量引用
```

### `__V`

评估变量名表达式，用于实现嵌套变量引用。

| 参数 | 必填 | 说明 |
|------|------|------|
| Variable name | 是 | 变量名表达式 |
| Default value | 否 | 默认值 |

```
${__V(A${N})}    → 当 N=1 时返回变量 A1 的值
```

---

## 八、String（字符串类）

### `__char`

将一组数字转换为 Unicode 字符。支持十进制、十六进制（`0x`）、八进制（`0`）。

```
${__char(65)}       → A
${__char(0x41)}     → A
${__char(48,49,50)} → 012
```

### `__changeCase`

更改字符串大小写。

| 参数 | 必填 | 说明 |
|------|------|------|
| String to change case | 是 | 字符串 |
| Change case mode | 否 | UPPER(默认)/LOWER/CAPITALIZE |
| Name of variable | 否 | 变量名 |

```
${__changeCase(hello,UPPER,)}     → HELLO
${__changeCase(HELLO,LOWER,)}     → hello
${__changeCase(hello world,CAPITALIZE,)} → Hello world
```

### `__escapeHtml`

使用 HTML 实体转义字符串中的字符。

```
${__escapeHtml(<html>)}    → &lt;html&gt;
```

### `__unescapeHtml`

将包含 HTML 实体转义的字符串还原。

```
${__unescapeHtml(&lt;html&gt;)}    → <html>
```

### `__escapeXml`

使用 XML 1.0 实体转义字符串。

```
${__escapeXml(<tag>)}    → &lt;tag&gt;
```

### `__escapeOroRegexpChars`

转义 ORO 正则表达式元字符。

```
${__escapeOroRegexpChars(1+2=3,)}    → 1\+2\=3
```

### `__regexFunction`

使用正则表达式解析前一次响应，返回填充了变量值的模板字符串。

| 参数 | 必填 | 说明 |
|------|------|------|
| First argument (regex) | 是 | 正则表达式 |
| Second argument (template) | 是 | 替换模板，用 `$[group]$` 引用捕获组 |
| Third argument (match number) | 否 | 整数/RAND/ALL/0~1 浮点数 |
| Fourth argument (separator) | 否 | ALL 模式下各匹配间的分隔符 |
| Fifth argument (default) | 否 | 无匹配时的默认返回值 |
| Sixth argument (refName) | 否 | 引用名称 |
| Seventh argument (inputVar) | 否 | 输入变量名 |

```
${__regexFunction((\d+),$1$,1,,,ref,)}
```

### `__unescape`

处理包含 Java 转义字符的字符串。

```
${__unescape(\n\t)}    → 换行+Tab
```

### `__urldecode`

对 URL 编码的字符串进行解码。

```
${__urldecode(Hello%20World)}    → Hello World
```

### `__urlencode`

将字符串编码为 URL 格式。

```
${__urlencode(Hello World)}    → Hello+World
```

### `__TestPlanName`

返回当前测试计划的名称（文件名）。

```
${__TestPlanName}    → 如 Demo.jmx
```

---

## 预定义变量与属性

### 预定义变量

| 变量名 | 说明 |
|--------|------|
| `COOKIE_cookiename` | 包含 cookie 值（由 HTTP Cookie Manager 设置） |
| `JMeterThread.last_sample_ok` | 上一次采样是否成功：true/false |
| `START.MS` | JMeter 启动时间（毫秒） |
| `START.YMD` | JMeter 启动时间（yyyyMMdd 格式） |
| `START.HMS` | JMeter 启动时间（HHmmss 格式） |

### 预定义属性

| 属性名 | 说明 |
|--------|------|
| `START.MS` | JMeter 启动时间（毫秒） |
| `START.YMD` | JMeter 启动时间（yyyyMMdd 格式） |
| `START.HMS` | JMeter 启动时间（HHmmss 格式） |
| `TESTSTART.MS` | 测试启动时间（毫秒） |

---

## 分类汇总

| 分类 | 数量 | 函数列表 |
|------|------|----------|
| Information | 9 | `__threadNum`, `__threadGroupName`, `__samplerName`, `__machineIP`, `__machineName`, `__time`, `__timeShift`, `__log`, `__logn` |
| Input | 5 | `__StringFromFile`, `__FileToString`, `__CSVRead`, `__XPath`, `__StringToFile` |
| Calculation | 9 | `__counter`, `__intSum`, `__longSum`, `__Random`, `__RandomDate`, `__RandomString`, `__RandomFromMultipleVars`, `__UUID`, `__digest` |
| Formatting | 1 | `__dateTimeConvert` |
| Scripting | 5 | `__groovy`, `__BeanShell`, `__javaScript`, `__jexl2`, `__jexl3` |
| Properties | 4 | `__isPropDefined`, `__property`, `__P`, `__setProperty` |
| Variables | 5 | `__isVarDefined`, `__split`, `__eval`, `__evalVar`, `__V` |
| String | 11 | `__char`, `__changeCase`, `__escapeHtml`, `__unescapeHtml`, `__escapeXml`, `__escapeOroRegexpChars`, `__regexFunction`, `__unescape`, `__urldecode`, `__urlencode`, `__TestPlanName` |

**总计：49 个内置函数**
