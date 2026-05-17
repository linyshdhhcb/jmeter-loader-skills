# JMeter 分布式测试指南

基于 Apache JMeter 官方文档（xdocs/usermanual/remote-test.xml）整理。

---

## 一、概述

当单台 JMeter 客户端机器性能不足以模拟足够用户压力时，可通过远程/分布式测试从一台客户端控制多台远程 JMeter 引擎，以模拟更大的负载。

### 核心特性

- 将测试样本保存到本地机器
- 从单台机器管理多个 JMeterEngine
- 无需将测试计划复制到每台服务器 — 客户端自动发送

### 重要提示

- 所有服务器运行**相同的测试计划**，JMeter **不会**在服务器之间分配负载
- 如果设置 1000 线程且有 6 台 JMeter 服务器，最终会产生 **6000 线程**
- 远程模式比独立运行相同数量的 CLI 模式测试消耗更多资源
- 如果服务器实例过多，客户端 JMeter 可能会过载

### 最佳实践

**不要在应用服务器上运行 JMeterEngine**，而应在与应用服务器同一以太网段上的独立机器上运行，以最小化网络影响且不影响应用服务器性能。

---

## 二、配置步骤

### Step 0: 配置节点

- 所有节点（客户端和服务器）必须运行**完全相同版本**的 JMeter
- 所有系统使用**相同版本**的 Java
- 拥有有效的 RMI over SSL 密钥库，或已禁用 SSL
- 数据文件**不会**由客户端发送，必须确保每台服务器上都有相应的数据文件
- 可通过编辑各服务器的 `user.properties` 或 `system.properties` 定义不同的属性值

### Step 1: 启动服务器

运行 `JMETER_HOME/bin/jmeter-server`（Unix）或 `JMETER_HOME/bin/jmeter-server.bat`（Windows）

- 每个节点只能运行一个 JMeter 服务器（除非使用不同的 RMI 端口）
- JMeter 服务器会自行启动 RMI 注册表
- 可通过 `server.rmi.localport` 属性控制动态端口

### Step 2: 添加服务器 IP 到客户端属性文件

编辑 `JMETER_HOME/bin/jmeter.properties` 中的 `remote_hosts` 属性：

```properties
remote_hosts=192.168.1.100,192.168.1.101,192.168.1.102
```

也可使用 `-R` 命令行选项：

```bash
jmeter -Rhost1,127.0.0.1,host2
```

设置 `server.exitaftertest=true` 可使服务器在运行一次测试后退出。

### Step 3a: 从 GUI 客户端启动

1. 运行 `bin/jmeter.bat`（Windows）或 `bin/jmeter`（Unix）
2. 使用 Run 菜单中的 "Remote Start" 和 "Remote Stop"

### Step 3b: 从 CLI 模式启动（推荐）

```bash
jmeter -n -t script.jmx -r
# 或指定服务器
jmeter -n -t script.jmx -R server1,server2,...
```

### 其他有用标志

| 标志 | 说明 |
|------|------|
| `-Gproperty=value` | 在所有服务器上定义属性 |
| `-X` | 测试结束后退出远程服务器 |
| `-Dproperty=value` | 定义系统属性 |
| `-q filename` | 加载额外属性文件 |

---

## 三、SSL 设置（自 JMeter 4.0 起）

RMI 默认使用 SSL 传输，需要创建密钥和证书。

### 生成密钥库

使用 `bin/create-rmi-keystore.bat`（Windows）或 `bin/create-rmi-keystore.sh`（Unix）生成密钥库：

- 生成有效期为 7 天的密钥对
- 默认密码为 `changeit`
- 密钥别名为 `rmi`

### 部署密钥库

将生成的 `rmi_keystore.jks` 复制到每台 JMeter 服务器和客户端的 `bin` 目录。

### 禁用 SSL

如果不希望使用 SSL，在 `user.properties` 中设置：

```properties
server.rmi.ssl.disable=true
```

---

## 四、使用不同端口

默认使用 RMI 端口 `1099`，修改需三方一致：

1. 服务器上以新端口号启动 `rmiregistry`
2. 服务器上定义 `server_port` 属性
3. 客户端更新 `remote_hosts` 为 `host:port` 格式

Windows 示例：

```cmd
SET SERVER_PORT=1664
JMETER-SERVER
```

Unix 示例：

```bash
SERVER_PORT=1664 jmeter-server
```

---

## 五、样本发送模式

在客户端设置 `mode` 属性，默认为 `StrippedBatch`（自 2.9 起）。

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `Standard` | 同步发送，样本生成后立即发送 | 调试 |
| `Hold` | 保存样本到运行结束（可能消耗大量内存） | 不推荐 |
| `DiskStore` | 将样本保存到磁盘文件，运行结束后发送 | 大量样本 |
| `StrippedDiskStore` | 移除成功样本的 responseData + DiskStore | 推荐 |
| `Batch` | 达到数量或时间阈值后批量发送 | 减少网络开销 |
| `Statistical` | 按线程组名和样本标签汇总发送 | 仅需汇总数据 |
| `Stripped` | 移除成功样本的 responseData | 减少数据传输 |
| `StrippedBatch` | 移除 responseData + Batch（默认） | 默认推荐 |
| `Asynch` | 异步发送，使用本地队列 | 高吞吐量 |
| `StrippedAsynch` | 移除 responseData + 异步发送 | 高吞吐量推荐 |

### 批量发送配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `num_sample_threshold` | 100 | 批量发送样本数阈值 |
| `time_threshold` | 60000 | 批量发送时间阈值（毫秒） |
| `asynch.batch.queue.size` | 100 | 异步模式队列大小 |

**注意**：Stripped 模式族会剥离 `responseData`，依赖前一个 `responseData` 的元素将无法工作。

---

## 六、处理启动失败的节点

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `client.tries` | 1 | 连接尝试次数 |
| `client.retries_delay` | 5000 | 重试间隔（毫秒） |
| `client.continue_on_fail` | false | 忽略失败节点继续测试 |

---

## 七、安全管理器

分布式环境中 JMeter 本质上是远程执行代理，可能被恶意利用。可通过 Java 安全管理器限制操作：

- 设置 `java.security.manager` 和 `java.security.policy` 系统属性
- 在 `setenv.sh` 中配置 JVM 参数
- 使用 `java.security.debug=access` 调试权限

---

## 八、网络提示

- JMeter/RMI 需要客户端到服务器的连接（默认端口 `1099`）
- 还需要反向连接（从服务器返回样本结果到客户端），使用高端口
- `client.rmi.localport` 属性控制客户端端口
- 防火墙需允许这些连接通过
- 支持 SSH 隧道：通过 `java.rmi.server.hostname` 参数允许使用回环接口

---

## 九、独立分布式模式

除了使用 JMeter 内置的远程测试功能，还可以在多台机器上独立运行多个 CLI 模式的 JMeter 实例：

```bash
# 在每台机器上独立运行
jmeter -n -t test.jmx -l result_$(hostname).jtl
```

优点：
- 不需要 RMI 连接
- 客户端不会成为瓶颈
- 更少的网络开销

缺点：
- 需要手动合并结果文件
- 无法从单一控制点启动/停止

### 合并结果文件

```bash
# 合并多个 JTL 文件
cat result_*.jtl > combined.jtl
# 或使用脚本处理
```

---

## 十、完整分布式测试示例

### 1. 环境准备

```
Master:  192.168.1.10 (客户端/控制器)
Slave1:  192.168.1.11 (JMeter 服务器)
Slave2:  192.168.1.12 (JMeter 服务器)
Slave3:  192.168.1.13 (JMeter 服务器)
```

### 2. 在每台 Slave 上启动 JMeter 服务器

```bash
# Slave1/2/3 上执行
cd JMETER_HOME/bin
./jmeter-server
```

### 3. 在 Master 上配置远程主机

编辑 `jmeter.properties`：

```properties
remote_hosts=192.168.1.11,192.168.1.12,192.168.1.13
```

### 4. 执行分布式测试

```bash
# 启动所有远程服务器
jmeter -n -t test.jmx -l result.jtl -r

# 或指定特定服务器
jmeter -n -t test.jmx -l result.jtl -R 192.168.1.11,192.168.1.12

# 传递属性到所有服务器
jmeter -n -t test.jmx -l result.jtl -r \
  -Gconcurrency=100 \
  -Gduration=300 \
  -Gtarget_host=api.example.com
```

### 5. 生成 HTML 报告

```bash
jmeter -g result.jtl -o report/
```
