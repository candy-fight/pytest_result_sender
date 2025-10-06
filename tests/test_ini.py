# 补充测试用例
# 测试配置文件
import configparser
from pathlib import Path

import pytest
from _pytest.pytester import Pytester

from pytest_result_sender import plugin

pytest_plugins = ["pytester"]  # 测试开发


@pytest.fixture(autouse=True)
def mock():
    # 设置干净的测试环境
    back_data = plugin.data
    plugin.data = {
        "passed": 0,
        "failed": 0,
    }
    yield
    # 恢复插件测试环境
    plugin.data = back_data


# 参数化装饰器，也可使用参数，参数1为变量，参数2为变量值
@pytest.mark.parametrize("send_when", ["every", "on_fail"])
def test_send_when(send_when, pytester: Pytester, tmp_path: Path) -> None:
    # 我要测试配置文件，所以需要获取/创建配置文件
    config_path = tmp_path.joinpath("pytest.ini")
    config_path.write_text(
        f"""
[pytest]    
send_when = {send_when}
send_api = "https://www.baidu.com"
"""
    )
    # 解析获取的配置
    config = pytester.parseconfig(config_path)
    assert config.getini("send_when") == send_when

    # 创建py文件，设计用例全部通过的场景
    pytester.makepyfile(
        """
    def test_example():
        pass
    """
    )
    # 在子进程中启动一个真实的 pytest 运行实例，并返回运行结果
    pytester.runpytest("-c", str(config_path))

    # 执行后，如何断言插件有无发送结果 -导入插件中的全局结果变量，根据标识判断
    print(plugin.data)
    if send_when == "every":
        assert plugin.data["send_done"] == 1
    else:
        assert plugin.data.get("send_done") is None


@pytest.mark.parametrize("send_api", ["https://www.baidu.com"])
def test_send_api(send_api, pytester: Pytester, tmp_path: Path) -> None:
    # 我要测试配置文件，所以需要获取/创建配置文件
    config_path = tmp_path.joinpath("pytest.ini")
    config_path.write_text(
        f"""
[pytest]    
send_when = "every"
send_api = {send_api}
"""
    )
    # 解析获取的配置
    config = pytester.parseconfig(config_path)
    assert config.getini("send_api") == send_api

    # 创建py文件，设计用例全部通过的场景
    pytester.makepyfile(
        """
    def test_example():
        pass
    """
    )
    # 在子进程中启动一个真实的 pytest 运行实例，并返回运行结果
    pytester.runpytest("-c", str(config_path))

    # 执行后，如何断言插件有无发送结果 -导入插件中的全局结果变量，根据标识判断
    print(plugin.data)
    if send_api:
        assert plugin.data["send_done"] == 1
    else:
        assert plugin.data.get("send_done") is None
