# JMeter Sampler 类型配置说明

## 概述

Sampler（采样器）是 JMeter 中用于向服务器发送请求的核心组件。不同类型的 Sampler 支持不同的协议和请求方式。本文档详细说明常用 Sampler 的 XML 配置结构和参数说明。

## HTTP Request Sampler（HTTP 请求采样器）

HTTP 请求采样器是最常用的采样器，用于发送 HTTP/HTTPS 请求。

### XML 结构

```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP请求" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
    <collectionProp name="Arguments.arguments"/>
  </elementProp>
  <stringProp name="HTTPSampler.domain">${__P(target_host,localhost)}</stringProp>
  <stringProp name="HTTPSampler.port">${__P(target_port,80)}</stringProp>
  <stringProp name="HTTPSampler.protocol">${__P(protocol,http)}</stringProp>
  <stringProp name="HTTPSampler.contentEncoding"></stringProp>
  <stringProp name="HTTPSampler.path">${__P(target_path,/)}</stringProp>
  <stringProp name="HTTPSampler.method">${__P(method,GET)}</stringProp>
  <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
  <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
  <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
  <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
  <stringProp name="HTTPSampler.connect_timeout">${__P(connect_timeout,)}</stringProp>
  <stringProp name="HTTPSampler.response_timeout">${__P(response_timeout,)}</stringProp>
</HTTPSamplerProxy>
```

### 参数说明

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `HTTPSampler.domain` | string | 目标主机名或 IP 地址 | localhost |
| `HTTPSampler.port` | string | 目标端口 | 80 (HTTP), 443 (HTTPS) |
| `HTTPSampler.protocol` | string | 协议类型（http/https） | http |
| `HTTPSampler.path` | string | 请求路径 | / |
| `HTTPSampler.method` | string | HTTP 方法 | GET |
| `HTTPSampler.contentEncoding` | string | 内容编码（如 UTF-8） | 空 |
| `HTTPSampler.follow_redirects` | bool | 是否跟随重定向 | true |
| `HTTPSampler.auto_redirects` | bool | 是否自动重定向 | false |
| `HTTPSampler.use_keepalive` | bool | 是否使用 Keep-Alive | true |
| `HTTPSampler.DO_MULTIPART_POST` | bool | 是否使用 multipart/form-data | false |
| `HTTPSampler.embedded_url_re` | string | 嵌入式资源 URL 正则 | 空 |
| `HTTPSampler.connect_timeout` | string | 连接超时（毫秒） | 空 |
| `HTTPSampler.response_timeout` | string | 响应超时（毫秒） | 空 |

### HTTP 方法

支持的 HTTP 方法：
- `GET` - 获取资源
- `POST` - 提交数据
- `PUT` - 更新资源
- `DELETE` - 删除资源
- `HEAD` - 获取头部信息
- `OPTIONS` - 获取支持的方法
- `PATCH` - 部分更新
- `TRACE` - 追踪请求

### GET 请求示例

```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="获取用户信息" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
    <collectionProp name="Arguments.arguments">
      <elementProp name="userId" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value">${user_id}</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
        <boolProp name="HTTPArgument.use_equals">true</boolProp>
        <stringProp name="Argument.name">userId</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
  <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
  <stringProp name="HTTPSampler.port">80</stringProp>
  <stringProp name="HTTPSampler.protocol">http</stringProp>
  <stringProp name="HTTPSampler.path">/api/users</stringProp>
  <stringProp name="HTTPSampler.method">GET</stringProp>
  <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
</HTTPSamplerProxy>
```

### POST 请求示例（JSON Body）

```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="创建用户" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
    <collectionProp name="Arguments.arguments">
      <elementProp name="" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value">{"name":"${username}","email":"${email}"}</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
        <boolProp name="HTTPArgument.use_equals">true</boolProp>
      </elementProp>
    </collectionProp>
  </elementProp>
  <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
  <stringProp name="HTTPSampler.port">80</stringProp>
  <stringProp name="HTTPSampler.protocol">http</stringProp>
  <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
  <stringProp name="HTTPSampler.path">/api/users</stringProp>
  <stringProp name="HTTPSampler.method">POST</stringProp>
  <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
  <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
</HTTPSamplerProxy>
```

### POST 请求示例（Form Data）

```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="表单提交" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
    <collectionProp name="Arguments.arguments">
      <elementProp name="username" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value">${username}</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
        <boolProp name="HTTPArgument.use_equals">true</boolProp>
        <stringProp name="Argument.name">username</stringProp>
      </elementProp>
      <elementProp name="password" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value">${password}</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
        <boolProp name="HTTPArgument.use_equals">true</boolProp>
        <stringProp name="Argument.name">password</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
  <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
  <stringProp name="HTTPSampler.port">80</stringProp>
  <stringProp name="HTTPSampler.protocol">http</stringProp>
  <stringProp name="HTTPSampler.path">/api/login</stringProp>
  <stringProp name="HTTPSampler.method">POST</stringProp>
  <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
</HTTPSamplerProxy>
```

---

## JDBC Request Sampler（JDBC 请求采样器）

JDBC 请求采样器用于执行数据库查询和操作。

### XML 结构

```xml
<JDBCSampler guiclass="TestBeanGUI" testclass="JDBCSampler" testname="JDBC请求" enabled="true">
  <stringProp name="dataSource">${__P(jdbc_pool,myDatabase)}</stringProp>
  <stringProp name="queryType">${__P(query_type,Select Statement)}</stringProp>
  <stringProp name="query">${__P(query,SELECT * FROM users LIMIT 10)}</stringProp>
  <stringProp name="queryArguments"></stringProp>
  <stringProp name="queryArgumentsTypes"></stringProp>
  <stringProp name="variableNames"></stringProp>
  <stringProp name="resultVariable"></stringProp>
  <stringProp name="queryTimeout">${__P(query_timeout,)}</stringProp>
  <stringProp name="limitResultSet">${__P(result_limit,)}</stringProp>
  <stringProp name="fetchSize">${__P(fetch_size,)}</stringProp>
</JDBCSampler>
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `dataSource` | string | JDBC 连接池名称（需在 JDBC Connection Configuration 中定义） |
| `queryType` | string | 查询类型 |
| `query` | string | SQL 查询语句 |
| `queryArguments` | string | 查询参数（逗号分隔） |
| `queryArgumentsTypes` | string | 参数类型（逗号分隔，如 INTEGER, VARCHAR） |
| `variableNames` | string | 将结果列保存到变量的名称列表 |
| `resultVariable` | string | 将完整结果集保存到的变量名 |
| `queryTimeout` | string | 查询超时时间（秒） |
| `limitResultSet` | string | 结果集限制行数 |
| `fetchSize` | string | 每次获取的行数 |

### 查询类型

| 查询类型 | 说明 |
|----------|------|
| `Select Statement` | 执行 SELECT 查询 |
| `Update Statement` | 执行 UPDATE/INSERT/DELETE |
| `Callable Statement` | 调用存储过程 |
| `Prepared Select Statement` | 预编译 SELECT |
| `Prepared Update Statement` | 预编译 UPDATE/INSERT/DELETE |
| `Commit` | 提交事务 |
| `Rollback` | 回滚事务 |
| `AutoCommit(false)` | 关闭自动提交 |
| `AutoCommit(true)` | 开启自动提交 |

### JDBC 连接配置

```xml
<JDBCDataSource guiclass="TestBeanGUI" testclass="JDBCDataSource" testname="JDBC连接配置" enabled="true">
  <stringProp name="dataSource">myDatabase</stringProp>
  <stringProp name="poolMax">${__P(jdbc_pool_max,10)}</stringProp>
  <stringProp name="timeout">${__P(jdbc_timeout,10000)}</stringProp>
  <stringProp name="trimInterval">60000</stringProp>
  <stringProp name="autocommit">true</stringProp>
  <stringProp name="transactionIsolation">DEFAULT</stringProp>
  <boolProp name="keepAlive">true</boolProp>
  <stringProp name="connectionAge">5000</stringProp>
  <stringProp name="checkQuery">SELECT 1</stringProp>
  <stringProp name="dbUrl">jdbc:mysql://${__P(db_host,localhost)}:${__P(db_port,3306)}/${__P(db_name,mydb)}?useUnicode=true&amp;characterEncoding=utf8</stringProp>
  <stringProp name="driver">com.mysql.cj.jdbc.Driver</stringProp>
  <stringProp name="username">${__P(db_username,root)}</stringProp>
  <stringProp name="password">${__P(db_password,)}</stringProp>
</JDBCDataSource>
```

### SELECT 查询示例

```xml
<JDBCSampler guiclass="TestBeanGUI" testclass="JDBCSampler" testname="查询用户" enabled="true">
  <stringProp name="dataSource">myDatabase</stringProp>
  <stringProp name="queryType">Select Statement</stringProp>
  <stringProp name="query">SELECT id, name, email FROM users WHERE status = ? LIMIT ?</stringProp>
  <stringProp name="queryArguments">active,100</stringProp>
  <stringProp name="queryArgumentsTypes">VARCHAR,INTEGER</stringProp>
  <stringProp name="variableNames">user_id,user_name,user_email</stringProp>
  <stringProp name="resultVariable">userList</stringProp>
  <stringProp name="queryTimeout">30</stringProp>
  <stringProp name="limitResultSet">1000</stringProp>
</JDBCSampler>
```

### INSERT 示例

```xml
<JDBCSampler guiclass="TestBeanGUI" testclass="JDBCSampler" testname="插入用户" enabled="true">
  <stringProp name="dataSource">myDatabase</stringProp>
  <stringProp name="queryType">Prepared Update Statement</stringProp>
  <stringProp name="query">INSERT INTO users (name, email, created_at) VALUES (?, ?, NOW())</stringProp>
  <stringProp name="queryArguments">${username},${email}</stringProp>
  <stringProp name="queryArgumentsTypes">VARCHAR,VARCHAR</stringProp>
</JDBCSampler>
```

---

## TCP Sampler（TCP 采样器）

TCP 采样器用于发送原始 TCP 请求。

### XML 结构

```xml
<TCPSampler guiclass="TCPSamplerGui" testclass="TCPSampler" testname="TCP请求" enabled="true">
  <stringProp name="TCPSampler.server">${__P(tcp_host,localhost)}</stringProp>
  <stringProp name="TCPSampler.port">${__P(tcp_port,8080)}</stringProp>
  <stringProp name="TCPSampler.timeout">${__P(tcp_timeout,)}</stringProp>
  <stringProp name="TCPSampler.reUseConnection">true</stringProp>
  <stringProp name="TCPSampler.noDelay">false</stringProp>
  <stringProp name="TCPSampler.closeConnection">false</stringProp>
  <stringProp name="TCPSampler.soLinger">${__P(tcp_linger,)}</stringProp>
  <stringProp name="TCPSampler.eolByte">${__P(tcp_eol,)}</stringProp>
  <stringProp name="TCPSampler.requestData">${__P(tcp_request,)}</stringProp>
  <stringProp name="TCPSampler.username"></stringProp>
  <stringProp name="TCPSampler.password"></stringProp>
  <stringProp name="TCPSampler.classname">org.apache.jmeter.protocol.tcp.sampler.BinaryTCPClientImpl</stringProp>
</TCPSampler>
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `TCPSampler.server` | string | TCP 服务器主机 |
| `TCPSampler.port` | string | TCP 服务器端口 |
| `TCPSampler.timeout` | string | 超时时间（毫秒） |
| `TCPSampler.reUseConnection` | bool | 是否复用连接 |
| `TCPSampler.noDelay` | bool | 是否禁用 Nagle 算法 |
| `TCPSampler.closeConnection` | bool | 请求后关闭连接 |
| `TCPSampler.soLinger` | string | SO_LINGER 设置 |
| `TCPSampler.eolByte` | string | 消息结束字节值 |
| `TCPSampler.requestData` | string | 请求数据 |
| `TCPSampler.classname` | string | TCP 客户端实现类 |

### TCP 客户端实现类

| 实现类 | 说明 |
|--------|------|
| `org.apache.jmeter.protocol.tcp.sampler.BinaryTCPClientImpl` | 二进制 TCP 客户端 |
| `org.apache.jmeter.protocol.tcp.sampler.LengthPrefixedBinaryTCPClientImpl` | 长度前缀二进制客户端 |
| `org.apache.jmeter.protocol.tcp.sampler.TCPClientImpl` | 文本 TCP 客户端 |

---

## Java Request Sampler（Java 请求采样器）

Java 请求采样器用于执行自定义 Java 代码。

### XML 结构

```xml
<JavaSampler guiclass="JavaTestSamplerGui" testclass="JavaSampler" testname="Java请求" enabled="true">
  <stringProp name="classname">${__P(java_class,org.apache.jmeter.protocol.java.test.JavaTest)}</stringProp>
  <elementProp name="arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
    <collectionProp name="Arguments.arguments">
      <elementProp name="Sleep_Time" elementType="Argument">
        <stringProp name="Argument.name">Sleep_Time</stringProp>
        <stringProp name="Argument.value">${__P(sleep_time,100)}</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
      </elementProp>
      <elementProp name="Sleep_Mask" elementType="Argument">
        <stringProp name="Argument.name">Sleep_Mask</stringProp>
        <stringProp name="Argument.value">0xFF</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
</JavaSampler>
```

### 自定义 Java Sampler

要创建自定义 Java Sampler，需要实现 `JavaSamplerClient` 接口：

```java
import org.apache.jmeter.protocol.java.sampler.AbstractJavaSamplerClient;
import org.apache.jmeter.protocol.java.sampler.JavaSamplerContext;
import org.apache.jmeter.samplers.SampleResult;

public class CustomJavaSampler extends AbstractJavaSamplerClient {
    
    @Override
    public SampleResult runTest(JavaSamplerContext context) {
        SampleResult result = new SampleResult();
        result.sampleStart();
        
        try {
            String param1 = context.getParameter("param1", "default");
            
            // 执行自定义逻辑
            result.setResponseData("执行结果", "UTF-8");
            result.setResponseCode("200");
            result.setResponseMessage("OK");
            result.setSuccessful(true);
            
        } catch (Exception e) {
            result.setResponseCode("500");
            result.setResponseMessage("Error: " + e.getMessage());
            result.setSuccessful(false);
        } finally {
            result.sampleEnd();
        }
        
        return result;
    }
}
```

---

## 其他 Sampler 类型

### FTP Request

```xml
<FTPSampler guiclass="FtpTestSamplerGui" testclass="FTPSampler" testname="FTP请求" enabled="true">
  <stringProp name="FTPSampler.server">${__P(ftp_host,localhost)}</stringProp>
  <stringProp name="FTPSampler.port">${__P(ftp_port,21)}</stringProp>
  <stringProp name="FTPSampler.username">${__P(ftp_user,anonymous)}</stringProp>
  <stringProp name="FTPSampler.password">${__P(ftp_pass,test@test.com)}</stringProp>
  <stringProp name="FTPSampler.remote.file">${__P(ftp_remote_file,)}</stringProp>
  <stringProp name="FTPSampler.local.file">${__P(ftp_local_file,)}</stringProp>
  <stringProp name="FTPSampler.inputData"></stringProp>
  <boolProp name="FTPSampler.saveResponse">true</boolProp>
  <stringProp name="FTPSampler.action">${__P(ftp_action,get)}</stringProp>
  <boolProp name="FTPSampler.useBinaryMode">true</boolProp>
</FTPSampler>
```

### SMTP Sampler

```xml
<SMTPSampler guiclass="SmtpSamplerGui" testclass="SMTPSampler" testname="SMTP请求" enabled="true">
  <stringProp name="SMTPSampler.server">${__P(smtp_host,localhost)}</stringProp>
  <stringProp name="SMTPSampler.port">${__P(smtp_port,25)}</stringProp>
  <stringProp name="SMTPSampler.sender">${__P(smtp_sender,)}</stringProp>
  <stringProp name="SMTPSampler.receiver">${__P(smtp_receiver,)}</stringProp>
  <stringProp name="SMTPSampler.subject">${__P(smtp_subject,Test Email)}</stringProp>
  <stringProp name="SMTPSampler.message">${__P(smtp_message,)}</stringProp>
  <stringProp name="SMTPSampler.username">${__P(smtp_user,)}</stringProp>
  <stringProp name="SMTPSampler.password">${__P(smtp_pass,)}</stringProp>
  <boolProp name="SMTPSampler.useSSL">false</boolProp>
  <boolProp name="SMTPSampler.useStartTLS">false</boolProp>
  <boolProp name="SMTPSampler.enforceStartTLS">false</boolProp>
</SMTPSampler>
```

### LDAP Request

```xml
<LDAPSampler guiclass="LdapExtSamplerGui" testclass="LDAPSampler" testname="LDAP请求" enabled="true">
  <stringProp name="server">${__P(ldap_host,localhost)}</stringProp>
  <stringProp name="port">${__P(ldap_port,389)}</stringProp>
  <stringProp name="rootdn">${__P(ldap_rootdn,)}</stringProp>
  <stringProp name="test">search</stringProp>
  <stringProp name="base">${__P(ldap_base,)}</stringProp>
  <stringProp name="scope">subtree</stringProp>
  <stringProp name="filter">${__P(ldap_filter,(objectClass=*))}</stringProp>
  <stringProp name="attributes">${__P(ldap_attrs,)}</stringProp>
  <boolProp name="returnobject">false</boolProp>
  <boolProp name="derefaliases">false</boolProp>
  <longProp name="countlimit">0</longProp>
  <longProp name="timelimit">0</longProp>
</LDAPSampler>
```

## 配置元件与 Sampler 配合使用

### HTTP 请求 + Header Manager

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
    <elementProp name="" elementType="Header">
      <stringProp name="Header.name">X-Request-ID</stringProp>
      <stringProp name="Header.value">${__UUID}</stringProp>
    </elementProp>
  </collectionProp>
</HeaderManager>
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="API请求" enabled="true">
  <!-- HTTP 采样器配置 -->
</HTTPSamplerProxy>
```

### HTTP 请求 + Cookie Manager

```xml
<CookieManager guiclass="CookiePanel" testclass="CookieManager" testname="HTTP Cookie管理器" enabled="true">
  <collectionProp name="CookieManager.cookies">
    <elementProp name="" elementType="Cookie">
      <stringProp name="Cookie.name">session_id</stringProp>
      <stringProp name="Cookie.value">${session_id}</stringProp>
      <stringProp name="Cookie.domain">api.example.com</stringProp>
      <stringProp name="Cookie.path">/</stringProp>
      <boolProp name="Cookie.secure">false</boolProp>
      <longProp name="Cookie.expires">0</longProp>
      <boolProp name="Cookie.path_specified">true</boolProp>
      <boolProp name="Cookie.domain_specified">true</boolProp>
    </elementProp>
  </collectionProp>
  <boolProp name="CookieManager.clearEachIteration">false</boolProp>
  <boolProp name="CookieManager.controlledByThreadGroup">false</boolProp>
</CookieManager>
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="需要Cookie的请求" enabled="true">
  <!-- HTTP 采样器配置 -->
</HTTPSamplerProxy>
```

## 最佳实践

### 参数化

- 所有可变参数使用 `${__P(propname,default)}` 形式
- 使用配置元件（如 HTTP Request Defaults）管理公共配置
- 敏感信息（密码、Token）从外部传入，不硬编码

### 性能优化

- 高并发时减少监听器数量
- 结果收集器只保存必要字段
- 使用 CSV 格式而非 XML 格式存储结果
- 启用 Keep-Alive 减少连接开销

### 可维护性

- 使用有意义的组件命名
- 添加必要的注释
- 模块化测试计划（使用 Include Controller）
- 版本控制管理 JMX 文件

### 安全性

- 敏感数据使用 JMeter 内置加密
- 不要在 JMX 中硬编码密码
- 使用环境变量或外部属性文件
- 测试环境与生产环境隔离
