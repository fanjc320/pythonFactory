def recursive_types(obj, indent=0):
    indent_str = ' ' * indent
    print(f"{indent_str}{type(obj)}")

    if isinstance(obj, dict):
        for k, v in obj.items():
            recursive_types(k, indent + 4)
            recursive_types(v, indent + 4)
    elif isinstance(obj, (list, tuple, set)) and not isinstance(obj, str):
        for item in obj:
            recursive_types(item, indent + 4)
    elif hasattr(obj, '__dict__'):
        recursive_types(vars(obj), indent + 4)

def recursive_type_info(obj, indent=0):
    """递归打印变量及其内部元素的类型信息"""
    indent_str = ' ' * indent

    # 打印当前对象的类型
    print(f"{indent_str}Type: {type(obj)}")

    # 处理字典类型
    if isinstance(obj, dict):
        print(f"{indent_str}Dict with {len(obj)} items:")
        for key, value in obj.items():
            print(f"{indent_str}  Key: {type(key)}")
            recursive_type_info(value, indent + 4)

    # 处理列表、元组、集合等可迭代对象（但不是字符串）
    elif isinstance(obj, (list, tuple, set)) and not isinstance(obj, str):
        print(f"{indent_str}{obj.__class__.__name__} with {len(obj)} items:")
        for item in obj:
            recursive_type_info(item, indent + 4)

    # 处理自定义对象
    elif hasattr(obj, '__dict__'):
        print(f"{indent_str}Object of {obj.__class__.__name__}:")
        recursive_type_info(vars(obj), indent + 4)

    # 基本类型直接打印
    else:
        print(f"{indent_str}Value: {obj} (Type: {type(obj)})")

def recursive_type_info_enhanced(obj, indent=0, visited=None):
    if visited is None:
        visited = set()

    # 防止循环引用
    obj_id = id(obj)
    if obj_id in visited:
        print(' ' * indent + "[...] (circular reference)")
        return
    visited.add(obj_id)

    indent_str = ' ' * indent
    print(f"{indent_str}Type: {type(obj)}")

    if isinstance(obj, dict):
        print(f"{indent_str}Dict with {len(obj)} items:")
        for key, value in obj.items():
            print(f"{indent_str}  Key type: {type(key)}")
            recursive_type_info_enhanced(value, indent + 4, visited)

    elif isinstance(obj, (list, tuple, set, frozenset)) and not isinstance(obj, (str, bytes, bytearray)):
        print(f"{indent_str}{obj.__class__.__name__} with {len(obj)} items:")
        for item in obj:
            recursive_type_info_enhanced(item, indent + 4, visited)

    elif hasattr(obj, '__dict__'):
        print(f"{indent_str}Object of {obj.__class__.__name__}:")
        recursive_type_info_enhanced(vars(obj), indent + 4, visited)

    else:
        print(f"{indent_str}Value type: {type(obj)}")

    visited.remove(obj_id)


data = {
    'name': 'Alice',
    'age': 30,
    'scores': [95, 88.5, 72],
    'info': {
        'address': '123 Main St',
        'contacts': ['email@example.com', 1234567890]
    }
}


def recursive_type_compact(obj, indent=0):
    """递归显示类型信息，相同类型元素只显示类型和数量"""
    indent_str = ' ' * indent

    # 基本类型直接显示
    if not isinstance(obj, (dict, list, tuple, set)) or isinstance(obj, str):
        print(f"{indent_str}{type(obj)}")
        return

    # 处理字典
    if isinstance(obj, dict):
        print(f"{indent_str}Dict: {len(obj)} items")

        # 检查所有键是否同类型
        key_types = {type(k) for k in obj.keys()}
        if len(key_types) == 1:
            print(f"{indent_str}  Keys: {key_types.pop()} × {len(obj)}")
        else:
            for k in obj.keys():
                print(f"{indent_str}  Key: {type(k)}")

        # 检查所有值是否同类型
        value_types = {type(v) for v in obj.values()}
        if len(value_types) == 1:
            print(f"{indent_str}  Values: {value_types.pop()} × {len(obj)}")
        else:
            for k, v in obj.items():
                print(f"{indent_str}  Value for key '{k}':")
                recursive_type_compact(v, indent + 4)
        return

    # 处理列表、元组、集合
    container_type = obj.__class__.__name__
    print(f"{indent_str}{container_type}: {len(obj)} items")

    # 检查所有元素是否同类型
    element_types = {type(e) for e in obj}
    if len(element_types) == 1:
        print(f"{indent_str}  Elements: {element_types.pop()} × {len(obj)}")
    else:
        for i, item in enumerate(obj):
            print(f"{indent_str}  Item {i}:")
            recursive_type_compact(item, indent + 4)

if __name__ == "__main__":
    recursive_type_info(data)
    print("--------------------")
    recursive_types(data)
    print("--------------------")

    recursive_type_compact(data)