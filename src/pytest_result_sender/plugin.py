from datetime import datetime

import pytest
import requests

# 安照hook规则 编写pytest开头的函数，实现对应的hook

# 结果 --一个全局变量
data = {
    "passed": 0,
    "failed": 0,
}


def pytest_addoption(parser):
    parser.addini("send_when", help="什么时候发送结果")
    parser.addini("send_api", help="发送到哪里")


def pytest_collection_finish(session: pytest.Session):
    # 用例加载完成后，执行调用
    # pytest.Session 就是我们的那个大会话，里面包含了很多信息，测试用例就是加载在这里的
    # 用例总个数
    data["total"] = len(session.items)


def pytest_runtest_logreport(report: pytest.TestReport):
    # 每个用例执行后，会调用，其中的参数report 指示了每个用例的执行结果
    if report.when == "call":
        print(report.outcome)
        data[report.outcome] += 1


def pytest_configure(config: pytest.Config):
    # 配置加载完成后，所有测试用例执行前，调用
    data["start_time"] = datetime.now().replace(microsecond=0)
    # 获取配置文件数据
    data["send_when"] = config.getini("send_when")
    data["send_api"] = config.getini("send_api")


def pytest_unconfigure():
    # 配置卸载完成后，所有测试用例执行完成后，调用
    data["end_time"] = datetime.now().replace(microsecond=0)
    # 执行时长
    data["duration"] = datetime.now().replace(microsecond=0) - data["start_time"]
    data["passed_ratio"] = f"{((data['passed'] / data['total']) * 100):.2f}%"

    # # 单元测试：（越是单元，反而越容易自动化，断言一下就好了）做完了注释掉 -每一个assert都是一个用例
    # # 测试驱动开发，如果断言失败，则代表我的需求没有开发完，不能结束。
    # assert 0 < data["duration"].total_seconds() < 3
    # assert data["total"] == 3
    # # 测试用例执行结果是否准确，说明：单元测试，使用assert就可以进行测试了
    # assert data["passed"] == 2
    # assert data["failed"] == 1
    # # 我需要在代码运行结果中得到这样一个数据结果
    # assert data["passed_ratio"] == "66.67%"
    pytest_send_result()


def pytest_send_result():
    if data["send_when"] == "on_fail" and data["failed"] == 0:
        # 如果没有失败用例，直接return，不发送
        return
    if data["send_api"] is None:
        return

    # 对于字典中的键值对，使用中括号取值的时候必须使用单引号
    url = data["send_api"]
    content = f"""
pytest自动化测试结果


测试时间：{data['end_time']}
用例数量：{data['total']}
执行时长：{data['duration']}
测试通过：<font color='green'>{data['passed']}</font>
测试失败：<font color='red'>{data['failed']}</font>
测试通过率：{data['passed_ratio']}

测试报告地址：{url}
"""
    try:
        requests.post(
            url, json={"msgtype": "markdown", "markdown": {"content": content}}
        )
    except Exception as e:
        print(e)

    # 运行到最后，如果成功发送，就更改成功发送的标志
    data["send_done"] = 1
