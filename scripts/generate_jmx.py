#!/usr/bin/env python3
"""
JMX 生成脚本 - 支持模板渲染和动态组件组装两种模式

功能:
1. 模板模式: 加载预置 JMX 模板，参数替换后输出
2. 动态组装模式: 根据用户指定的组件列表，从零构建 JMX 测试计划
3. 验证输出格式

用法:
  # 模板模式
  python generate_jmx.py --template base.jmx --output test.jmx \
      --param target_host=example.com --param concurrency=50

  # 动态组装模式
  python generate_jmx.py --build --output test.jmx \
      --param target_host=api.example.com \
      --http-sampler name=GetUsers,path=/api/users,method=GET \
      --http-sampler name=CreateOrder,path=/api/orders,method=POST,body='{"item":"test"}' \
      --json-extractor refname=order_id,jsonPath=$.data.orderId \
      --assertion type=response,field=code,pattern=200 \
      --timer type=gaussian,delay=300,range=100

  # 列出可用模板
  python generate_jmx.py --list-templates

  # 列出可用组件
  python generate_jmx.py --list-components
"""

import argparse
import copy
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


class JMXComponentBuilder:
    """JMX 组件构建器 - 提供各类型组件的 XML 片段生成方法"""

    @staticmethod
    def _prop(name: str, value: str, prop_type: str = "string") -> ET.Element:
        el = ET.Element(f"{prop_type}Prop")
        el.set("name", name)
        el.text = str(value)
        return el

    @staticmethod
    def _bool_prop(name: str, value: bool) -> ET.Element:
        el = ET.Element("boolProp")
        el.set("name", name)
        el.text = "true" if value else "false"
        return el

    @staticmethod
    def _int_prop(name: str, value: int) -> ET.Element:
        el = ET.Element("intProp")
        el.set("name", name)
        el.text = str(value)
        return el

    @staticmethod
    def _string_prop(name: str, value: str) -> ET.Element:
        el = ET.Element("stringProp")
        el.set("name", name)
        el.text = str(value)
        return el

    @staticmethod
    def _collection_prop(name: str) -> ET.Element:
        el = ET.Element("collectionProp")
        el.set("name", name)
        return el

    @staticmethod
    def _element_prop(name: str, elem_type: str) -> ET.Element:
        el = ET.Element("elementProp")
        el.set("name", name)
        el.set("elementType", elem_type)
        return el

    @staticmethod
    def _header(name: str, value: str) -> ET.Element:
        el = ET.Element("elementProp")
        el.set("name", "")
        el.set("elementType", "Header")
        el.append(JMXComponentBuilder._string_prop("Header.name", name))
        el.append(JMXComponentBuilder._string_prop("Header.value", value))
        return el

    @staticmethod
    def _http_argument(name: str, value: str, use_equals: bool = True, always_encode: bool = False) -> ET.Element:
        el = ET.Element("elementProp")
        el.set("name", name)
        el.set("elementType", "HTTPArgument")
        el.append(JMXComponentBuilder._bool_prop("HTTPArgument.always_encode", always_encode))
        el.append(JMXComponentBuilder._string_prop("Argument.value", value))
        el.append(JMXComponentBuilder._string_prop("Argument.metadata", "="))
        if use_equals:
            el.append(JMXComponentBuilder._bool_prop("HTTPArgument.use_equals", True))
            el.append(JMXComponentBuilder._string_prop("Argument.name", name))
        return el

    @staticmethod
    def build_test_plan(name: str = "Test Plan", comments: str = "",
                        functional_mode: bool = False, serialize_tg: bool = False,
                        variables: Dict[str, str] = None) -> ET.Element:
        tp = ET.Element("TestPlan")
        tp.set("guiclass", "TestPlanGui")
        tp.set("testclass", "TestPlan")
        tp.set("testname", name)
        tp.set("enabled", "true")
        tp.append(JMXComponentBuilder._string_prop("TestPlan.comments", comments))
        tp.append(JMXComponentBuilder._bool_prop("TestPlan.functional_mode", functional_mode))
        tp.append(JMXComponentBuilder._bool_prop("TestPlan.tearDown_on_shutdown", True))
        tp.append(JMXComponentBuilder._bool_prop("TestPlan.serialize_threadgroups", serialize_tg))
        udv = ET.Element("elementProp")
        udv.set("name", "TestPlan.user_defined_variables")
        udv.set("elementType", "Arguments")
        udv.set("guiclass", "ArgumentsPanel")
        udv.set("testclass", "Arguments")
        udv.set("testname", "User Defined Variables")
        udv.set("enabled", "true")
        args_coll = JMXComponentBuilder._collection_prop("Arguments.arguments")
        if variables:
            for k, v in variables.items():
                arg_el = JMXComponentBuilder._element_prop(k, "Argument")
                arg_el.append(JMXComponentBuilder._string_prop("Argument.name", k))
                arg_el.append(JMXComponentBuilder._string_prop("Argument.value", v))
                arg_el.append(JMXComponentBuilder._string_prop("Argument.metadata", "="))
                args_coll.append(arg_el)
        udv.append(args_coll)
        tp.append(udv)
        tp.append(JMXComponentBuilder._string_prop("TestPlan.user_define_classpath", ""))
        return tp

    @staticmethod
    def build_thread_group(name: str = "Thread Group",
                           threads: str = "${__P(concurrency,10)}",
                           rampup: str = "${__P(rampup,10)}",
                           duration: str = "${__P(duration,60)}",
                           loops: str = "-1",
                           on_sample_error: str = "continue",
                           same_user: bool = True,
                           delay: str = "") -> ET.Element:
        tg = ET.Element("ThreadGroup")
        tg.set("guiclass", "ThreadGroupGui")
        tg.set("testclass", "ThreadGroup")
        tg.set("testname", name)
        tg.set("enabled", "true")
        tg.append(JMXComponentBuilder._string_prop("ThreadGroup.on_sample_error", on_sample_error))
        lc = ET.Element("elementProp")
        lc.set("name", "ThreadGroup.main_controller")
        lc.set("elementType", "LoopController")
        lc.set("guiclass", "LoopControlPanel")
        lc.set("testclass", "LoopController")
        lc.set("testname", "Loop Controller")
        lc.set("enabled", "true")
        lc.append(JMXComponentBuilder._bool_prop("LoopController.continue_forever", True))
        lc.append(JMXComponentBuilder._string_prop("LoopController.loops", loops))
        tg.append(lc)
        tg.append(JMXComponentBuilder._string_prop("ThreadGroup.num_threads", threads))
        tg.append(JMXComponentBuilder._string_prop("ThreadGroup.ramp_time", rampup))
        tg.append(JMXComponentBuilder._bool_prop("ThreadGroup.scheduler", True))
        tg.append(JMXComponentBuilder._string_prop("ThreadGroup.duration", duration))
        tg.append(JMXComponentBuilder._string_prop("ThreadGroup.delay", delay))
        tg.append(JMXComponentBuilder._bool_prop("ThreadGroup.same_user_on_next_iteration", same_user))
        return tg

    @staticmethod
    def build_http_defaults(host: str = "${__P(target_host,localhost)}",
                            port: str = "${__P(target_port,80)}",
                            protocol: str = "${__P(protocol,http)}",
                            encoding: str = "UTF-8",
                            path: str = "") -> ET.Element:
        el = ET.Element("ConfigTestElement")
        el.set("guiclass", "HttpDefaultsGui")
        el.set("testclass", "ConfigTestElement")
        el.set("testname", "HTTP Request Defaults")
        el.set("enabled", "true")
        args = ET.Element("elementProp")
        args.set("name", "HTTPsampler.Arguments")
        args.set("elementType", "Arguments")
        args.set("guiclass", "HTTPArgumentsPanel")
        args.set("testclass", "Arguments")
        args.set("enabled", "true")
        args.append(JMXComponentBuilder._collection_prop("Arguments.arguments"))
        el.append(args)
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.domain", host))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.port", port))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.protocol", protocol))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.contentEncoding", encoding))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.path", path))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.concurrentPool", "6"))
        el.append(JMXComponentBuilder._bool_prop("HTTPSampler.embedded_url_re", False))
        return el

    @staticmethod
    def build_header_manager(headers: List[Dict[str, str]] = None) -> ET.Element:
        if headers is None:
            headers = [{"name": "Content-Type", "value": "application/json"},
                       {"name": "Accept", "value": "application/json"}]
        el = ET.Element("HeaderManager")
        el.set("guiclass", "HeaderPanel")
        el.set("testclass", "HeaderManager")
        el.set("testname", "HTTP Header Manager")
        el.set("enabled", "true")
        coll = JMXComponentBuilder._collection_prop("HeaderManager.headers")
        for h in headers:
            coll.append(JMXComponentBuilder._header(h["name"], h["value"]))
        el.append(coll)
        return el

    @staticmethod
    def build_cookie_manager(clear_each_iteration: bool = False) -> ET.Element:
        el = ET.Element("CookieManager")
        el.set("guiclass", "CookiePanel")
        el.set("testclass", "CookieManager")
        el.set("testname", "HTTP Cookie Manager")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._collection_prop("CookieManager.cookies"))
        el.append(JMXComponentBuilder._bool_prop("CookieManager.clearEachIteration", clear_each_iteration))
        el.append(JMXComponentBuilder._bool_prop("CookieManager.controlledByThreadGroup", True))
        return el

    @staticmethod
    def build_http_sampler(name: str = "HTTP Request",
                           method: str = "GET",
                           path: str = "/",
                           host: str = "",
                           port: str = "",
                           protocol: str = "",
                           encoding: str = "",
                           body: str = "",
                           params: List[Dict[str, str]] = None,
                           connect_timeout: str = "",
                           response_timeout: str = "",
                           follow_redirects: bool = True,
                           use_keepalive: bool = True,
                           post_body_raw: bool = False) -> ET.Element:
        el = ET.Element("HTTPSamplerProxy")
        el.set("guiclass", "HttpTestSampleGui")
        el.set("testclass", "HTTPSamplerProxy")
        el.set("testname", name)
        el.set("enabled", "true")
        args_el = ET.Element("elementProp")
        args_el.set("name", "HTTPsampler.Arguments")
        args_el.set("elementType", "Arguments")
        args_el.set("guiclass", "HTTPArgumentsPanel")
        args_el.set("testclass", "Arguments")
        args_el.set("enabled", "true")
        args_coll = JMXComponentBuilder._collection_prop("Arguments.arguments")
        if post_body_raw and body:
            args_coll.append(JMXComponentBuilder._http_argument("", body, use_equals=True, always_encode=False))
        elif params:
            for p in params:
                args_coll.append(JMXComponentBuilder._http_argument(
                    p.get("name", ""), p.get("value", ""),
                    use_equals=True, always_encode=False
                ))
        args_el.append(args_coll)
        el.append(args_el)
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.domain", host))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.port", port))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.protocol", protocol))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.contentEncoding", encoding))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.path", path))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.method", method))
        el.append(JMXComponentBuilder._bool_prop("HTTPSampler.follow_redirects", follow_redirects))
        el.append(JMXComponentBuilder._bool_prop("HTTPSampler.auto_redirects", False))
        el.append(JMXComponentBuilder._bool_prop("HTTPSampler.use_keepalive", use_keepalive))
        el.append(JMXComponentBuilder._bool_prop("HTTPSampler.DO_MULTIPART_POST", False))
        if post_body_raw and body:
            el.append(JMXComponentBuilder._bool_prop("HTTPSampler.postBodyRaw", True))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.embedded_url_re", ""))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.connect_timeout", connect_timeout))
        el.append(JMXComponentBuilder._string_prop("HTTPSampler.response_timeout", response_timeout))
        return el

    @staticmethod
    def build_json_extractor(refname: str, json_path: str,
                             match_number: str = "1",
                             default_value: str = "NOT_FOUND") -> ET.Element:
        el = ET.Element("JSONPostProcessor")
        el.set("guiclass", "JSONPostProcessorGui")
        el.set("testclass", "JSONPostProcessor")
        el.set("testname", f"JE_{refname}")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("JSONPostProcessor.referenceNames", refname))
        el.append(JMXComponentBuilder._string_prop("JSONPostProcessor.jsonPathExprs", json_path))
        el.append(JMXComponentBuilder._string_prop("JSONPostProcessor.match_numbers", match_number))
        el.append(JMXComponentBuilder._string_prop("JSONPostProcessor.default_values", default_value))
        return el

    @staticmethod
    def build_boundary_extractor(refname: str, left_boundary: str, right_boundary: str,
                                 match_number: str = "1",
                                 default_value: str = "NOT_FOUND",
                                 use_headers: str = "false") -> ET.Element:
        el = ET.Element("BoundaryExtractor")
        el.set("guiclass", "BoundaryExtractorGui")
        el.set("testclass", "BoundaryExtractor")
        el.set("testname", f"BE_{refname}")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("BoundaryExtractor.refname", refname))
        el.append(JMXComponentBuilder._string_prop("BoundaryExtractor.boundaries", left_boundary))
        el.append(JMXComponentBuilder._string_prop("BoundaryExtractor.rightBoundary", right_boundary))
        el.append(JMXComponentBuilder._string_prop("BoundaryExtractor.defaultValue", default_value))
        el.append(JMXComponentBuilder._string_prop("BoundaryExtractor.matchNumber", match_number))
        el.append(JMXComponentBuilder._string_prop("BoundaryExtractor.useHeaders", use_headers))
        return el

    @staticmethod
    def build_regex_extractor(refname: str, regex: str, template: str = "$1$",
                              match_number: str = "1",
                              default_value: str = "NOT_FOUND") -> ET.Element:
        el = ET.Element("RegexExtractor")
        el.set("guiclass", "RegexExtractorGui")
        el.set("testclass", "RegexExtractor")
        el.set("testname", f"RE_{refname}")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("RegexExtractor.useHeaders", "false"))
        el.append(JMXComponentBuilder._string_prop("RegexExtractor.refname", refname))
        el.append(JMXComponentBuilder._string_prop("RegexExtractor.regex", regex))
        el.append(JMXComponentBuilder._string_prop("RegexExtractor.template", template))
        el.append(JMXComponentBuilder._string_prop("RegexExtractor.match_number", match_number))
        el.append(JMXComponentBuilder._string_prop("RegexExtractor.default", default_value))
        return el

    @staticmethod
    def build_response_assertion(name: str = "Response Assertion",
                                 test_field: str = "Assertion.response_code",
                                 test_type: int = 16,
                                 patterns: List[str] = None,
                                 custom_message: str = "") -> ET.Element:
        if patterns is None:
            patterns = ["200"]
        el = ET.Element("ResponseAssertion")
        el.set("guiclass", "AssertionGui")
        el.set("testclass", "ResponseAssertion")
        el.set("testname", name)
        el.set("enabled", "true")
        coll = JMXComponentBuilder._collection_prop("Asserter.testStrings")
        for p in patterns:
            s = JMXComponentBuilder._element_prop("", "string")
            s.append(JMXComponentBuilder._string_prop("Argument.value", p))
            s.append(JMXComponentBuilder._string_prop("Argument.metadata", "="))
            coll.append(s)
        el.append(coll)
        el.append(JMXComponentBuilder._string_prop("Assertion.custom_message", custom_message))
        el.append(JMXComponentBuilder._string_prop("Assertion.test_field", test_field))
        el.append(JMXComponentBuilder._bool_prop("Assertion.assume_success", False))
        el.append(JMXComponentBuilder._int_prop("Assertion.test_type", test_type))
        return el

    @staticmethod
    def build_duration_assertion(duration_ms: str = "5000") -> ET.Element:
        el = ET.Element("DurationAssertion")
        el.set("guiclass", "DurationAssertionGui")
        el.set("testclass", "DurationAssertion")
        el.set("testname", "Duration Assertion")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("DurationAssertion.duration", duration_ms))
        return el

    @staticmethod
    def build_json_assertion(json_path: str, expected_value: str = "",
                             is_regex: bool = False,
                             expect_null: bool = False,
                             invert: bool = False) -> ET.Element:
        el = ET.Element("JSONPathAssertion")
        el.set("guiclass", "JSONPathAssertionGui")
        el.set("testclass", "JSONPathAssertion")
        el.set("testname", "JSON Assertion")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("JSON_PATH", json_path))
        el.append(JMXComponentBuilder._string_prop("EXPECTED_VALUE", expected_value))
        el.append(JMXComponentBuilder._bool_prop("JSONVALIDATION", True))
        el.append(JMXComponentBuilder._bool_prop("EXPECT_NULL", expect_null))
        el.append(JMXComponentBuilder._bool_prop("INVERT", invert))
        el.append(JMXComponentBuilder._bool_prop("ISREGEX", is_regex))
        return el

    @staticmethod
    def build_constant_timer(delay_ms: str = "${__P(think_time,1000)}") -> ET.Element:
        el = ET.Element("ConstantTimer")
        el.set("guiclass", "ConstantTimerGui")
        el.set("testclass", "ConstantTimer")
        el.set("testname", "Constant Timer")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("ConstantTimer.delay", delay_ms))
        return el

    @staticmethod
    def build_gaussian_timer(delay_ms: str = "1000", range_ms: str = "300") -> ET.Element:
        el = ET.Element("GaussianRandomTimer")
        el.set("guiclass", "GaussianRandomTimerGui")
        el.set("testclass", "GaussianRandomTimer")
        el.set("testname", "Gaussian Random Timer")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("ConstantTimer.delay", delay_ms))
        el.append(JMXComponentBuilder._string_prop("RandomTimer.range", range_ms))
        return el

    @staticmethod
    def build_uniform_timer(delay_ms: str = "1000", range_ms: str = "500") -> ET.Element:
        el = ET.Element("UniformRandomTimer")
        el.set("guiclass", "UniformRandomTimerGui")
        el.set("testclass", "UniformRandomTimer")
        el.set("testname", "Uniform Random Timer")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("ConstantTimer.delay", delay_ms))
        el.append(JMXComponentBuilder._string_prop("RandomTimer.range", range_ms))
        return el

    @staticmethod
    def build_synchronizing_timer(group_size: str = "10", timeout_ms: str = "0") -> ET.Element:
        el = ET.Element("Synchronizer")
        el.set("guiclass", "SynchronizerGui")
        el.set("testclass", "Synchronizer")
        el.set("testname", "Synchronizing Timer")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("groupSize", group_size))
        el.append(JMXComponentBuilder._string_prop("timeoutInMs", timeout_ms))
        return el

    @staticmethod
    def build_if_controller(condition: str, evaluate_all: bool = False) -> ET.Element:
        el = ET.Element("IfController")
        el.set("guiclass", "IfControllerPanel")
        el.set("testclass", "IfController")
        el.set("testname", "If Controller")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("IfController.condition", condition))
        el.append(JMXComponentBuilder._bool_prop("IfController.evaluateAll", evaluate_all))
        el.append(JMXComponentBuilder._bool_prop("IfController.useExpression", True))
        return el

    @staticmethod
    def build_transaction_controller(name: str, parent: bool = True,
                                     include_timers: bool = False) -> ET.Element:
        el = ET.Element("TransactionController")
        el.set("guiclass", "TransactionControllerGui")
        el.set("testclass", "TransactionController")
        el.set("testname", name)
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._bool_prop("TransactionController.include_timers", include_timers))
        el.append(JMXComponentBuilder._bool_prop("TransactionController.parent", parent))
        return el

    @staticmethod
    def build_once_only_controller() -> ET.Element:
        el = ET.Element("OnceOnlyController")
        el.set("guiclass", "OnceOnlyControllerGui")
        el.set("testclass", "OnceOnlyController")
        el.set("testname", "Once Only Controller")
        el.set("enabled", "true")
        return el

    @staticmethod
    def build_loop_controller(loops: str = "5") -> ET.Element:
        el = ET.Element("LoopController")
        el.set("guiclass", "LoopControlPanel")
        el.set("testclass", "LoopController")
        el.set("testname", "Loop Controller")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._bool_prop("LoopController.continue_forever", False))
        el.append(JMXComponentBuilder._string_prop("LoopController.loops", loops))
        return el

    @staticmethod
    def build_foreach_controller(input_prefix: str, output_var: str,
                                  start_index: str = "0", end_index: str = "-1",
                                  use_separator: bool = True) -> ET.Element:
        el = ET.Element("ForeachController")
        el.set("guiclass", "ForeachControlPanel")
        el.set("testclass", "ForeachController")
        el.set("testname", "ForEach Controller")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("ForeachController.inputVal", input_prefix))
        el.append(JMXComponentBuilder._string_prop("ForeachController.startIndex", start_index))
        el.append(JMXComponentBuilder._string_prop("ForeachController.endIndex", end_index))
        el.append(JMXComponentBuilder._string_prop("ForeachController.returnVal", output_var))
        el.append(JMXComponentBuilder._bool_prop("ForeachController.useSeparator", use_separator))
        return el

    @staticmethod
    def build_csv_data_set(filename: str = "testdata.csv", variable_names: str = "username,password",
                           delimiter: str = ",", ignore_first_line: bool = True,
                           recycle: bool = True, stop_thread: bool = False,
                           share_mode: str = "shareMode.thread",
                           encoding: str = "") -> ET.Element:
        el = ET.Element("CSVDataSet")
        el.set("guiclass", "TestBeanGUI")
        el.set("testclass", "CSVDataSet")
        el.set("testname", "CSV Data Set Config")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("delimiter", delimiter))
        el.append(JMXComponentBuilder._string_prop("fileEncoding", encoding))
        el.append(JMXComponentBuilder._string_prop("filename", filename))
        el.append(JMXComponentBuilder._bool_prop("ignoreFirstLine", ignore_first_line))
        el.append(JMXComponentBuilder._bool_prop("quotedData", False))
        el.append(JMXComponentBuilder._bool_prop("recycle", recycle))
        el.append(JMXComponentBuilder._string_prop("shareMode", share_mode))
        el.append(JMXComponentBuilder._bool_prop("stopThread", stop_thread))
        el.append(JMXComponentBuilder._string_prop("variableNames", variable_names))
        return el

    @staticmethod
    def build_jsr223_postprocessor(script: str, language: str = "groovy",
                                    cache_key: bool = True) -> ET.Element:
        el = ET.Element("JSR223PostProcessor")
        el.set("guiclass", "TestBeanGUI")
        el.set("testclass", "JSR223PostProcessor")
        el.set("testname", "JSR223 PostProcessor")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("scriptLanguage", language))
        el.append(JMXComponentBuilder._string_prop("parameters", ""))
        el.append(JMXComponentBuilder._string_prop("filename", ""))
        el.append(JMXComponentBuilder._bool_prop("cacheKey", cache_key))
        el.append(JMXComponentBuilder._string_prop("script", script))
        return el

    @staticmethod
    def build_jsr223_preprocessor(script: str, language: str = "groovy",
                                   cache_key: bool = True) -> ET.Element:
        el = ET.Element("JSR223PreProcessor")
        el.set("guiclass", "TestBeanGUI")
        el.set("testclass", "JSR223PreProcessor")
        el.set("testname", "JSR223 PreProcessor")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("scriptLanguage", language))
        el.append(JMXComponentBuilder._string_prop("parameters", ""))
        el.append(JMXComponentBuilder._string_prop("filename", ""))
        el.append(JMXComponentBuilder._bool_prop("cacheKey", cache_key))
        el.append(JMXComponentBuilder._string_prop("script", script))
        return el

    @staticmethod
    def build_debug_sampler(display_jmeter_vars: bool = True,
                            display_jmeter_props: bool = False,
                            display_system_props: bool = False) -> ET.Element:
        el = ET.Element("DebugSampler")
        el.set("guiclass", "TestBeanGUI")
        el.set("testclass", "DebugSampler")
        el.set("testname", "Debug Sampler")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._bool_prop("displayJMeterProperties", display_jmeter_props))
        el.append(JMXComponentBuilder._bool_prop("displayJMeterVariables", display_jmeter_vars))
        el.append(JMXComponentBuilder._bool_prop("displaySystemProperties", display_system_props))
        return el

    @staticmethod
    def build_result_collector(filename: str = "${__P(result_file,result.jtl)}",
                                error_logging: bool = False) -> ET.Element:
        el = ET.Element("ResultCollector")
        el.set("guiclass", "ViewResultsFullVisualizer")
        el.set("testclass", "ResultCollector")
        el.set("testname", "View Results Tree")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._bool_prop("ResultCollector.error_logging", error_logging))
        obj = ET.Element("objProp")
        name_el = ET.Element("name")
        name_el.text = "saveConfig"
        obj.append(name_el)
        value = ET.Element("value")
        value.set("class", "SampleSaveConfiguration")
        for tag, val in [("time", True), ("latency", True), ("timestamp", True),
                         ("success", True), ("label", True), ("code", True),
                         ("message", True), ("threadName", True), ("dataType", True),
                         ("encoding", False), ("assertions", True), ("subresults", True),
                         ("responseData", False), ("samplerData", False), ("xml", False),
                         ("fieldNames", True), ("responseHeaders", False),
                         ("requestHeaders", False), ("responseDataOnError", False),
                         ("saveAssertionResultsFailureMessage", True),
                         ("assertionsResultsToSave", "0"), ("bytes", True),
                         ("sentBytes", True), ("url", True), ("threadCounts", True),
                         ("idleTime", True), ("connectTime", True)]:
            child = ET.Element(tag)
            child.text = str(val).lower() if isinstance(val, bool) else str(val)
            value.append(child)
        obj.append(value)
        el.append(obj)
        el.append(JMXComponentBuilder._string_prop("filename", filename))
        return el

    @staticmethod
    def build_backend_listener_influxdb(influxdb_url: str = "http://localhost:8086/api/v2/write",
                                         influxdb_token: str = "",
                                         application: str = "JMeter-Test",
                                         samplers_regex: str = ".*",
                                         percentiles: str = "50;90;95;99",
                                         summary_only: bool = False,
                                         queue_size: str = "5000") -> ET.Element:
        el = ET.Element("BackendListener")
        el.set("guiclass", "BackendListenerGui")
        el.set("testclass", "BackendListener")
        el.set("testname", "Backend Listener (InfluxDB)")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._string_prop("classname",
                  "org.apache.jmeter.visualizers.backend.influxdb.InfluxdbBackendListenerClient"))
        args_el = ET.Element("elementProp")
        args_el.set("name", "Arguments")
        args_el.set("elementType", "Arguments")
        args_el.set("guiclass", "ArgumentsPanel")
        args_el.set("testclass", "Arguments")
        args_el.set("enabled", "true")
        args_coll = JMXComponentBuilder._collection_prop("Arguments.arguments")
        for k, v in [("influxdbUrl", influxdb_url), ("influxdbToken", influxdb_token),
                      ("application", application), ("measurement", "jmeter"),
                      ("summaryOnly", str(summary_only).lower()),
                      ("samplersRegex", samplers_regex),
                      ("percentiles", percentiles),
                      ("testTitle", "JMeter Load Test")]:
            arg = JMXComponentBuilder._element_prop(k, "Argument")
            arg.append(JMXComponentBuilder._string_prop("Argument.name", k))
            arg.append(JMXComponentBuilder._string_prop("Argument.value", v))
            args_coll.append(arg)
        args_el.append(args_coll)
        el.append(args_el)
        el.append(JMXComponentBuilder._string_prop("asyncQueueSize", queue_size))
        return el

    @staticmethod
    def build_cache_manager(clear_each_iteration: bool = False,
                            use_expires: bool = True) -> ET.Element:
        el = ET.Element("CacheManager")
        el.set("guiclass", "CacheManagerGui")
        el.set("testclass", "CacheManager")
        el.set("testname", "HTTP Cache Manager")
        el.set("enabled", "true")
        el.append(JMXComponentBuilder._bool_prop("clearEachIteration", clear_each_iteration))
        el.append(JMXComponentBuilder._bool_prop("useExpires", use_expires))
        el.append(JMXComponentBuilder._string_prop("maxCacheSize", "5000"))
        return el


class JMXDynamicBuilder:
    """动态 JMX 构建器 - 从零组装 JMX 测试计划"""

    def __init__(self):
        self.cb = JMXComponentBuilder()
        self.test_plan = None
        self.test_plan_hash = None
        self.thread_groups: List[Tuple[ET.Element, ET.Element]] = []

    def set_test_plan(self, name: str = "Test Plan", **kwargs) -> 'JMXDynamicBuilder':
        self.test_plan = self.cb.build_test_plan(name=name, **kwargs)
        self.test_plan_hash = ET.Element("hashTree")
        return self

    def add_thread_group(self, name: str = "Thread Group", **kwargs) -> 'JMXDynamicBuilder':
        if self.test_plan is None:
            self.set_test_plan()
        tg = self.cb.build_thread_group(name=name, **kwargs)
        tg_hash = ET.Element("hashTree")
        self.test_plan_hash.append(tg)
        self.test_plan_hash.append(tg_hash)
        self.thread_groups.append((tg, tg_hash))
        return self

    def _get_current_tg_hash(self) -> ET.Element:
        if not self.thread_groups:
            self.add_thread_group()
        return self.thread_groups[-1][1]

    def add_http_defaults(self, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_http_defaults(**kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_header_manager(self, headers: List[Dict[str, str]] = None, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_header_manager(headers=headers, **kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_cookie_manager(self, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_cookie_manager(**kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_cache_manager(self, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_cache_manager(**kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_csv_data_set(self, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_csv_data_set(**kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_http_sampler(self, name: str = "HTTP Request",
                         extractors: List[Dict] = None,
                         assertions: List[Dict] = None,
                         headers: List[Dict[str, str]] = None,
                         **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        sampler = self.cb.build_http_sampler(name=name, **kwargs)
        h.append(sampler)
        sampler_hash = ET.Element("hashTree")
        if extractors:
            for ext in extractors:
                ext_type = ext.pop("type", "json")
                if ext_type == "json":
                    sampler_hash.append(self.cb.build_json_extractor(**ext))
                elif ext_type == "boundary":
                    sampler_hash.append(self.cb.build_boundary_extractor(**ext))
                elif ext_type == "regex":
                    sampler_hash.append(self.cb.build_regex_extractor(**ext))
                sampler_hash.append(ET.Element("hashTree"))
        if assertions:
            for a in assertions:
                a_type = a.pop("type", "response")
                if a_type == "response":
                    sampler_hash.append(self.cb.build_response_assertion(**a))
                elif a_type == "duration":
                    sampler_hash.append(self.cb.build_duration_assertion(**a))
                elif a_type == "json":
                    sampler_hash.append(self.cb.build_json_assertion(**a))
                sampler_hash.append(ET.Element("hashTree"))
        if headers:
            sampler_hash.append(self.cb.build_header_manager(headers=headers))
            sampler_hash.append(ET.Element("hashTree"))
        h.append(sampler_hash)
        return self

    def add_timer(self, timer_type: str = "gaussian", **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        if timer_type == "constant":
            h.append(self.cb.build_constant_timer(**kwargs))
        elif timer_type == "gaussian":
            h.append(self.cb.build_gaussian_timer(**kwargs))
        elif timer_type == "uniform":
            h.append(self.cb.build_uniform_timer(**kwargs))
        elif timer_type == "synchronizing":
            h.append(self.cb.build_synchronizing_timer(**kwargs))
        else:
            h.append(self.cb.build_gaussian_timer(**kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_if_controller(self, condition: str, children_builder=None, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        ic = self.cb.build_if_controller(condition=condition, **kwargs)
        h.append(ic)
        ic_hash = ET.Element("hashTree")
        h.append(ic_hash)
        return self

    def add_transaction_controller(self, name: str, children_builder=None, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        tc = self.cb.build_transaction_controller(name=name, **kwargs)
        h.append(tc)
        tc_hash = ET.Element("hashTree")
        h.append(tc_hash)
        return self

    def add_once_only_controller(self) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_once_only_controller())
        h.append(ET.Element("hashTree"))
        return self

    def add_debug_sampler(self, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_debug_sampler(**kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_jsr223_postprocessor(self, script: str, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_jsr223_postprocessor(script=script, **kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_jsr223_preprocessor(self, script: str, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_jsr223_preprocessor(script=script, **kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_result_collector(self, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_result_collector(**kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def add_backend_listener_influxdb(self, **kwargs) -> 'JMXDynamicBuilder':
        h = self._get_current_tg_hash()
        h.append(self.cb.build_backend_listener_influxdb(**kwargs))
        h.append(ET.Element("hashTree"))
        return self

    def build(self) -> str:
        if self.test_plan is None:
            self.set_test_plan()
        if not self.thread_groups:
            self.add_thread_group()
        root = ET.Element("jmeterTestPlan")
        root.set("version", "1.2")
        root.set("properties", "5.0")
        root.set("jmeter", "5.4.1")
        root_hash = ET.Element("hashTree")
        root_hash.append(self.test_plan)
        root_hash.append(self.test_plan_hash)
        root.append(root_hash)
        ET.indent(root, space="  ")
        xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str + "\n"


class JMXGenerator:
    """JMX 文件生成器类 - 支持模板模式和动态组装模式"""

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(
                os.path.dirname(script_dir), 'assets', 'templates'
            )
        self.template_dir = template_dir
        self.env = None
        if JINJA2_AVAILABLE:
            self.env = Environment(
                loader=FileSystemLoader(template_dir),
                trim_blocks=True, lstrip_blocks=True
            )

    def list_available_templates(self) -> List[str]:
        templates = []
        if os.path.exists(self.template_dir):
            for file in os.listdir(self.template_dir):
                if file.endswith('.jmx'):
                    templates.append(file)
        return sorted(templates)

    @staticmethod
    def list_available_components() -> Dict[str, List[str]]:
        return {
            "Samplers": ["http_sampler", "debug_sampler"],
            "Controllers": ["if_controller", "transaction_controller",
                           "once_only_controller", "loop_controller",
                           "foreach_controller"],
            "Timers": ["constant_timer", "gaussian_timer", "uniform_timer",
                      "synchronizing_timer"],
            "Extractors": ["json_extractor", "boundary_extractor", "regex_extractor"],
            "Assertions": ["response_assertion", "duration_assertion", "json_assertion"],
            "Config": ["http_defaults", "header_manager", "cookie_manager",
                      "cache_manager", "csv_data_set"],
            "Processors": ["jsr223_postprocessor", "jsr223_preprocessor"],
            "Listeners": ["result_collector", "backend_listener_influxdb"],
        }

    def parse_parameters(self, params_list: List[str]) -> Dict[str, Any]:
        params = {}
        for param in params_list:
            if '=' in param:
                key, value = param.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif self._is_float(value):
                    value = float(value)
                params[key] = value
        return params

    @staticmethod
    def parse_kv_string(kv_str: str) -> Dict[str, str]:
        result = {}
        for part in kv_str.split(','):
            if '=' in part:
                k, v = part.split('=', 1)
                result[k.strip()] = v.strip()
        return result

    def _is_float(self, value: str) -> bool:
        try:
            float(value)
            return '.' in value or 'e' in value.lower()
        except ValueError:
            return False

    def _apply_defaults(self, params: Dict[str, Any]) -> Dict[str, Any]:
        defaults = {
            'concurrency': 10, 'rampup': 10, 'duration': 60,
            'target_port': 80, 'protocol': 'http',
            'method': 'GET', 'target_path': '/',
        }
        result = defaults.copy()
        result.update(params)
        return result

    def generate_with_jinja2(self, template_name: str, params: Dict[str, Any]) -> str:
        if not JINJA2_AVAILABLE:
            raise ImportError("Jinja2 not installed")
        full_params = self._apply_defaults(params)
        try:
            template = self.env.get_template(template_name)
            return template.render(**full_params)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template not found: {template_name}")

    def generate_simple(self, template_name: str, params: Dict[str, Any]) -> str:
        template_path = os.path.join(self.template_dir, template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_name}")
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        full_params = self._apply_defaults(params)
        for key, value in full_params.items():
            placeholder = f"{{{{" + key + "}}}}"
            content = content.replace(placeholder, str(value))
        return content

    def generate(self, template_name: str, params: Dict[str, Any],
                 use_jinja2: bool = None) -> str:
        if use_jinja2 is None:
            use_jinja2 = JINJA2_AVAILABLE
        if use_jinja2:
            return self.generate_with_jinja2(template_name, params)
        else:
            return self.generate_simple(template_name, params)

    @staticmethod
    def build_dynamic(params: Dict[str, Any],
                      http_samplers: List[Dict] = None,
                      extractors: List[Dict] = None,
                      assertions: List[Dict] = None,
                      timers: List[Dict] = None,
                      controllers: List[Dict] = None,
                      config_elements: List[Dict] = None,
                      listeners: List[Dict] = None,
                      backend_listeners: List[Dict] = None) -> str:
        builder = JMXDynamicBuilder()
        tp_kwargs = {}
        if params.get("test_plan_name"):
            tp_kwargs["name"] = params["test_plan_name"]
        if params.get("serialize_tg"):
            tp_kwargs["serialize_tg"] = params["serialize_tg"]
        if params.get("variables"):
            tp_kwargs["variables"] = params["variables"]
        builder.set_test_plan(**tp_kwargs)

        tg_kwargs = {}
        if params.get("thread_group_name"):
            tg_kwargs["name"] = params["thread_group_name"]
        if params.get("concurrency"):
            tg_kwargs["threads"] = str(params["concurrency"])
        if params.get("rampup"):
            tg_kwargs["rampup"] = str(params["rampup"])
        if params.get("duration"):
            tg_kwargs["duration"] = str(params["duration"])
        if params.get("on_sample_error"):
            tg_kwargs["on_sample_error"] = params["on_sample_error"]
        builder.add_thread_group(**tg_kwargs)

        if config_elements:
            for cfg in config_elements:
                cfg_type = cfg.pop("type", "http_defaults")
                if cfg_type == "http_defaults":
                    builder.add_http_defaults(**cfg)
                elif cfg_type == "header_manager":
                    builder.add_header_manager(**cfg)
                elif cfg_type == "cookie_manager":
                    builder.add_cookie_manager(**cfg)
                elif cfg_type == "cache_manager":
                    builder.add_cache_manager(**cfg)
                elif cfg_type == "csv_data_set":
                    builder.add_csv_data_set(**cfg)

        if timers:
            for t in timers:
                builder.add_timer(**t)

        if http_samplers:
            for s in http_samplers:
                s_extractors = s.pop("extractors", None)
                s_assertions = s.pop("assertions", None)
                s_headers = s.pop("headers", None)
                builder.add_http_sampler(
                    name=s.pop("name", "HTTP Request"),
                    extractors=s_extractors,
                    assertions=s_assertions,
                    headers=s_headers,
                    **s
                )
        elif assertions:
            for a in assertions:
                a_type = a.pop("type", "response")
                if a_type == "response":
                    builder._get_current_tg_hash().append(
                        JMXComponentBuilder.build_response_assertion(**a))
                    builder._get_current_tg_hash().append(ET.Element("hashTree"))
                elif a_type == "duration":
                    builder._get_current_tg_hash().append(
                        JMXComponentBuilder.build_duration_assertion(**a))
                    builder._get_current_tg_hash().append(ET.Element("hashTree"))

        if listeners is None:
            listeners = [{}]
        for l_cfg in listeners:
            builder.add_result_collector(**l_cfg)

        if backend_listeners:
            for bl in backend_listeners:
                builder.add_backend_listener_influxdb(**bl)

        return builder.build()

    @staticmethod
    def validate_jmx(content: str) -> bool:
        required = ['<jmeterTestPlan', '</jmeterTestPlan>',
                    '<hashTree>', '</hashTree>']
        for el in required:
            if el not in content:
                print(f"Warning: missing element {el}")
                return False
        return True

    @staticmethod
    def save_to_file(content: str, output_path: str) -> bool:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True


def _parse_sampler_args(args_list: List[str]) -> List[Dict]:
    result = []
    for s in args_list:
        kv = JMXGenerator.parse_kv_string(s)
        if 'body' in kv:
            kv['body'] = kv['body']
            kv['post_body_raw'] = True
        if 'extractors' in kv:
            ext_list = []
            for ext_str in kv.pop('extractors').split('|'):
                ext_kv = JMXGenerator.parse_kv_string(ext_str)
                ext_list.append(ext_kv)
            kv['extractors'] = ext_list
        if 'assertions' in kv:
            ass_list = []
            for ass_str in kv.pop('assertions').split('|'):
                ass_kv = JMXGenerator.parse_kv_string(ass_str)
                ass_list.append(ass_kv)
            kv['assertions'] = ass_list
        result.append(kv)
    return result


def main():
    parser = argparse.ArgumentParser(
        description='JMeter JMX Test Plan Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Template mode:
  python generate_jmx.py --template base.jmx --output test.jmx \
    --param target_host=api.example.com --param concurrency=50

Dynamic build mode:
  python generate_jmx.py --build --output test.jmx \
    --param target_host=api.example.com \
    --http-sampler name=GetUsers,path=/api/users,method=GET \
    --http-sampler name=CreateOrder,path=/api/orders,method=POST,body='{"item":"test"}' \
    --timer type=gaussian,delay=300,range=100

List available:
  python generate_jmx.py --list-templates
  python generate_jmx.py --list-components
        '''
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--template', '-t', type=str, help='Template file name')
    mode_group.add_argument('--build', '-b', action='store_true',
                            help='Dynamic build mode')
    mode_group.add_argument('--list-templates', '-l', action='store_true',
                            help='List available templates')
    mode_group.add_argument('--list-components', action='store_true',
                            help='List available components for build mode')

    parser.add_argument('--output', '-o', type=str, help='Output JMX file path')
    parser.add_argument('--param', '-p', action='append', default=[],
                        help='Parameter key=value, can be used multiple times')
    parser.add_argument('--template-dir', type=str, help='Template directory path')
    parser.add_argument('--no-jinja2', action='store_true',
                        help='Do not use Jinja2')
    parser.add_argument('--validate', '-v', action='store_true',
                        help='Validate generated JMX format')

    parser.add_argument('--http-sampler', action='append', default=[],
                        help='HTTP sampler config: name=X,path=Y,method=Z,body=W')
    parser.add_argument('--timer', action='append', default=[],
                        help='Timer config: type=gaussian,delay=1000,range=300')
    parser.add_argument('--extractor', action='append', default=[],
                        help='Extractor config: type=json,refname=X,jsonPath=Y')
    parser.add_argument('--assertion', action='append', default=[],
                        help='Assertion config: type=response,field=code,pattern=200')
    parser.add_argument('--config', action='append', default=[],
                        help='Config element: type=cookie_manager or type=csv_data_set,...')
    parser.add_argument('--backend-listener', action='append', default=[],
                        help='Backend listener: type=influxdb,url=...')

    args = parser.parse_args()
    generator = JMXGenerator(args.template_dir)

    if args.list_templates:
        templates = generator.list_available_templates()
        print("Available templates:")
        for tmpl in templates:
            print(f"  - {tmpl}")
        return 0

    if args.list_components:
        components = generator.list_available_components()
        print("Available components for --build mode:")
        for category, items in components.items():
            print(f"\n  {category}:")
            for item in items:
                print(f"    - {item}")
        return 0

    if not args.output:
        parser.error("--output is required")

    params = generator.parse_parameters(args.param)

    print("=" * 60)
    print("JMX Generation Config")
    print("=" * 60)

    try:
        if args.build:
            print("Mode: Dynamic Build")
            print(f"Params: {params}")

            http_samplers = _parse_sampler_args(args.http_sampler) if args.http_sampler else None

            timers = []
            for t_str in args.timer:
                timers.append(JMXGenerator.parse_kv_string(t_str))

            global_extractors = []
            for e_str in args.extractor:
                global_extractors.append(JMXGenerator.parse_kv_string(e_str))

            global_assertions = []
            for a_str in args.assertion:
                global_assertions.append(JMXGenerator.parse_kv_string(a_str))

            config_elements = []
            for c_str in args.config:
                config_elements.append(JMXGenerator.parse_kv_string(c_str))

            backend_listeners = []
            for bl_str in args.backend_listener:
                backend_listeners.append(JMXGenerator.parse_kv_string(bl_str))

            if not http_samplers and params.get("target_path"):
                http_samplers = [{
                    "name": params.get("sampler_name", "HTTP Request"),
                    "path": str(params.get("target_path", "/")),
                    "method": str(params.get("method", "GET")),
                }]

            content = generator.build_dynamic(
                params=params,
                http_samplers=http_samplers,
                timers=timers if timers else [{"timer_type": "gaussian", "delay_ms": "300", "range_ms": "100"}],
                assertions=global_assertions if global_assertions else None,
                config_elements=config_elements if config_elements else None,
                backend_listeners=backend_listeners if backend_listeners else None,
            )
        elif args.template:
            print(f"Mode: Template ({args.template})")
            print(f"Params: {params}")
            content = generator.generate(
                args.template, params,
                use_jinja2=not args.no_jinja2
            )
        else:
            parser.error("Specify --template or --build")
            return 1

        if args.validate:
            if generator.validate_jmx(content):
                print("[OK] JMX format validation passed")
            else:
                print("[WARNING] JMX format warnings detected")

        generator.save_to_file(content, args.output)
        print(f"[OK] JMX file generated: {args.output}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
