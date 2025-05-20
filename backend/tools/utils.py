import importlib
from .models import Tool


def execute_tool(tool: Tool, payload: dict):
    module_path, func_name = tool.function_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name)
    return func(**payload)
