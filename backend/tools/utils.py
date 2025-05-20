# import importlib
# from .models import Tool


# def execute_tool(tool: Tool, payload: dict):
#     module = importlib.import_module(tool.module_path)
#     func = getattr(module, tool.function_name)
#     return func(**payload)
