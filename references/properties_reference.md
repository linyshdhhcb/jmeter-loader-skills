# JMeter 关键属性参考

基于 Apache JMeter 官方文档（xdocs/usermanual/properties_reference.xml）整理，聚焦性能测试相关关键属性。

---

## 一、SSL 配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `https.sessioncontext.shared` | false | 是否共享 SSL 会话上下文（每线程） |
| `https.default.protocol` | TLS | 默认 HTTPS 协议 |
| `https.socket.protocols` | - | 启用的协议列表 |
| `https.cipherSuites` | JVM 默认 | 允许的 SSL 密码套件 |
| `httpclient.reset_state_on_thread_group_iteration` | true | 线程组迭代时重置 HTTP 状态 |
| `https.keyStoreStartIndex` | 0 | 密钥库起始索引 |
| `https.keyStoreEndIndex` | 0 | 密钥库结束索引 |

---

## 二、远程主机和 RMI 配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `remote_hosts` | 127.0.0.1 | 远程主机列表（逗号分隔） |
| `server_port` | 1099 | 服务器 RMI 端口 |
| `client.rmi.localport` | 0 | 客户端 RMI 本地端口（0=随机） |
| `client.tries` | 1 | 初始化远程引擎尝试次数 |
| `client.retries_delay` | 5000 | 重试延迟（毫秒） |
| `client.continue_on_fail` | false | 忽略失败节点继续测试 |
| `server.rmi.port` | 1099 | 服务器访问端口 |
| `server.rmi.localport` | 4000 | 服务器引擎本地端口 |
| `server.rmi.create` | true | 服务器是否创建 RMI 注册表 |
| `server.exitaftertest` | true | 测试后退出 |
| `server.rmi.ssl.disable` | false | 禁用 RMI SSL |

---

## 三、Apache HttpClient 配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `httpclient4.auth.preemptive` | true | 抢先发送 BASIC 认证头 |
| `httpclient4.retrycount` | 0 | 重试次数 |
| `httpclient4.request_sent_retry_enabled` | false | 是否重试已发送的请求 |
| `httpclient4.idletimeout` | 0 | 空闲连接超时（毫秒） |
| `httpclient4.validate_after_inactivity` | 4900 | 不活动后验证连接时间（毫秒） |
| `httpclient4.time_to_live` | 60000 | 连接 TTL（毫秒） |
| `httpclient4.deflate_relax_mode` | false | 忽略 Deflate EOFException |
| `httpclient4.gzip_relax_mode` | false | 忽略 GZip EOFException |

---

## 四、HTTP 缓存管理器

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `cacheable_methods` | GET | 可缓存的方法 |
| `cache_manager.cached_resource_mode` | RETURN_NO_SAMPLE | 缓存资源返回模式 |

缓存资源返回模式：

| 模式 | 说明 |
|------|------|
| `RETURN_NO_SAMPLE` | 不返回样本（默认） |
| `RETURN_200_CACHE` | 返回 200 状态码 |
| `RETURN_CUSTOM_STATUS` | 返回自定义状态码 |

---

## 五、结果文件配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `jmeter.save.saveservice.output_format` | csv | 输出格式（csv/xml） |
| `jmeter.save.saveservice.autoflush` | false | 自动刷新（影响性能） |
| `jmeter.save.saveservice.timestamp_format` | ms | 时间戳格式 |
| `jmeter.save.saveservice.print_field_names` | true | CSV 首行字段名 |
| `sample_variables` | - | 额外保存的变量 |
| `resultcollector.action_if_file_exists` | - | 文件已存在时的操作（ASK/APPEND/DELETE） |

---

## 六、SampleResult 相关设置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `sampleresult.timestamp.start` | false | 使用开始时间戳 |
| `sampleresult.useNanoTime` | true | 使用 nanoTime |
| `sampleresult.nanoThreadSleep` | 5000 | nanoTime 偏移线程间隔 |
| `subresults.disable_renaming` | false | 禁用子结果重命名策略 |

---

## 七、远程批处理配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `mode` | StrippedBatch | 样本发送模式 |
| `sample_sender_client_configured` | true | 客户端还是服务器配置发送器 |
| `sample_sender_strip_also_on_error` | true | 错误样本也剥离响应 |
| `key_on_threadname` | false | 统计样本按线程名分组 |
| `num_sample_threshold` | 100 | 批量发送样本数阈值 |
| `time_threshold` | 60000 | 批量发送时间阈值（毫秒） |
| `asynch.batch.queue.size` | 100 | 异步模式队列大小 |

---

## 八、汇总器配置（CLI 模式）

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `summariser.name` | summary | 汇总器名称 |
| `summariser.interval` | 30 | 汇总间隔（秒） |
| `summariser.log` | true | 写入日志文件 |
| `summariser.out` | true | 写入 System.out |
| `summariser.ignore_transaction_controller_sample_result` | true | 忽略事务控制器样本 |

---

## 九、聚合报告百分位数

| 属性 | 默认值 |
|------|--------|
| `aggregate_rpt_pct1` | 90 |
| `aggregate_rpt_pct2` | 95 |
| `aggregate_rpt_pct3` | 99 |

---

## 十、BackendListener 配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `backend_graphite.send_interval` | 1 | Graphite 发送间隔（秒） |
| `backend_influxdb.send_interval` | 5 | InfluxDB 发送间隔（秒） |
| `backend_influxdb.connection_timeout` | 1000 | InfluxDB 连接超时（毫秒） |
| `backend_influxdb.socket_timeout` | 3000 | InfluxDB 读取超时（毫秒） |
| `backend_metrics_window` | 100 | 百分位数滑动窗口大小 |
| `backend_metrics_large_window` | 5000 | timed 模式下的大窗口 |
| `backend_metrics_percentile_estimator` | LEGACY | 百分位数估算类型（设 R_3 与聚合报告一致） |
| `backend_metrics_window_mode` | fixed | 窗口模式（fixed/timed） |

---

## 十一、报告生成配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `jmeter.reportgenerator.apdex_satisfied_threshold` | 500 | APDEX 满意阈值（毫秒） |
| `jmeter.reportgenerator.apdex_tolerated_threshold` | 1500 | APDEX 容忍阈值（毫秒） |
| `jmeter.reportgenerator.overall_granularity` | 60000 | 时间图表粒度（毫秒） |
| `jmeter.reportgenerator.statistic_window` | 20000 | 百分位数滑动窗口 |
| `jmeter.reportgenerator.report_title` | "Apache JMeter Dashboard" | 报告标题 |
| `jmeter.reportgenerator.exporter.html.property.output_dir` | report-output | HTML 输出目录 |
| `jmeter.reportgenerator.exporter.html.series_filter` | "" | 系列过滤正则 |
| `generate_report_ui.generation_timeout` | 300000 | GUI 生成超时（毫秒） |

---

## 十二、HTTP 采样器配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `httpsampler.max_bytes_to_store_per_request` | 0 | 每个请求最大存储字节数（0=不截断） |
| `httpsampler.max_buffer_size` | 66560 | 读取响应最大缓冲区（字节） |
| `httpsampler.max_redirects` | 20 | 最大重定向次数 |
| `httpsampler.max_frame_depth` | 5 | 最大 frame/iframe 嵌套深度 |
| `httpsampler.ignore_failed_embedded_resources` | false | 忽略嵌入资源下载失败 |
| `httpsampler.embedded_resources_use_md5` | false | 嵌入资源仅保存 MD5 |
| `sampleresult.default.encoding` | UTF-8 | 默认编码 |

---

## 十三、线程组验证功能

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `testplan_validation.nb_threads_per_thread_group` | 1 | 验证时线程数 |
| `testplan_validation.ignore_timers` | true | 验证时忽略定时器 |
| `testplan_validation.ignore_backends` | true | 验证时忽略 BackendListener |
| `testplan_validation.number_iterations` | 1 | 验证时迭代次数 |
| `testplan_validation.tpc_force_100_pct` | false | 强制吞吐量控制器为 100% |

---

## 十四、定时器相关

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `timer.factor` | 1.0f | 应用于高斯/均匀/泊松随机定时器的暂停因子 |
| `think_time_creator.default_constant_pause` | 1000 | 默认常量暂停 |
| `think_time_creator.default_range` | 100 | 默认范围暂停 |

---

## 十五、JSR-223 脚本配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `jsr223.init.file` | - | 启动时调用的 JSR-223 脚本文件 |
| `jsr223.compiled_scripts_cache_size` | 100 | 编译脚本缓存大小 |

---

## 十六、类路径配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `search_paths` | - | 搜索 JMeter 插件类的目录列表（分号分隔） |
| `user.classpath` | - | 搜索工具和依赖类的目录列表 |
| `plugin_dependency_paths` | - | 插件依赖目录列表 |

---

## 十七、JMX 备份配置

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `jmeter.gui.action.save.backup_on_save` | true | 保存时自动备份 |
| `jmeter.gui.action.save.backup_directory` | `${JMETER_HOME}/backups` | 备份目录 |
| `jmeter.gui.action.save.keep_backup_max_hours` | 0 | 备份保留最大小时数 |
| `jmeter.gui.action.save.keep_backup_max_count` | 10 | 最大备份数量 |
| `save_automatically_before_run` | true | 运行前自动保存 |

---

## 十八、Cookie 管理器

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `CookieManager.delete_null_cookies` | true | 删除空值 Cookie |
| `CookieManager.save.cookies` | false | 将 Cookie 存储为变量 |

---

## 十九、引擎相关

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `jmeterengine.threadstop.wait` | 5000 | 线程停止等待时间（毫秒） |
| `jmeterengine.nongui.port` | 4445 | CLI 模式关闭监听端口 |
| `jmeterthread.rampup.granularity` | 1000 | Ramp-up 期间关闭检查间隔 |

---

## 二十、视图相关

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `view.results.tree.max_results` | 500 | 查看结果树最大样本数 |
| `view.results.tree.max_size` | 10485760 | HTML 页面最大显示大小 |
