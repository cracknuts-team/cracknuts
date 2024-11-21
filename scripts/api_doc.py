import importlib


def dynamic_import(path: str):
    """
    动态导入模块、类、方法或类的方法（支持未声明在 __init__.py 中的内容）。

    参数:
        path (str): 指定模块路径、类路径或方法路径。例如：
            - 模块: "package.module"
            - 类: "package.module.ClassName"
            - 方法: "package.module.ClassName.method"

    返回:
        object: 动态导入的模块、类、方法或类的方法。
    """
    try:
        # 将路径按 "." 分隔
        components = path.split(".")

        # 初始化模块加载路径和最终属性访问路径
        module_path = []
        remaining_components = components[:]

        # 找到最深的可导入模块路径
        while remaining_components:
            potential_module_path = ".".join(remaining_components)
            try:
                module = importlib.import_module(potential_module_path)
                module_path = remaining_components
                break
            except ModuleNotFoundError:
                # 如果当前路径无法导入，尝试上一级路径
                remaining_components.pop()

        if not module_path:
            raise ModuleNotFoundError(f"无法导入模块路径：'{path}'")

        # 从找到的模块开始，逐级解析属性
        obj = module
        for comp in components[len(module_path) :]:
            obj = getattr(obj, comp)

        return obj
    except (ModuleNotFoundError, AttributeError) as e:
        raise ImportError(f"无法导入路径 '{path}': {e}")


# 示例用法
if __name__ == "__main__":
    # 导入模块
    os_path = dynamic_import("os.path")
    print(os_path)

    # 导入包中未声明的模块
    json_scanner = dynamic_import("json.decoder.py_scanstring")
    print(json_scanner('"key": "value"', 1))  # 使用未声明的方法

    # 导入类
    json_decoder_class = dynamic_import("json.decoder.JSONDecoder")
    print(json_decoder_class)

    # 导入类的方法
    from_json_method = dynamic_import("json.decoder.JSONDecoder.decode")
    print(from_json_method(json_decoder_class(), '{"key": "value"}'))

    # 导入函数
    sqrt_func = dynamic_import("math.sqrt")
    print(sqrt_func(16))  # 输出: 4.0

    ck = dynamic_import("cracknuts.cracker.cracker.Cracker.cracker_read_register")
    print(ck.__doc__)
