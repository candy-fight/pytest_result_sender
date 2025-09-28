from datetime import datetime

# 安照hook规则 编写pytest开头的函数，实现对应的hook

def pytest_configure():
    # 配置加载完成后，所有测试用例执行前，调用
    print(f"{datetime.now()} pytest开始执行")
    print("{} pytest开始执行".format(datetime.now()))

def pytest_unconfigure():
    # 配置卸载完成后，所有测试用例执行完成后，调用
    pass