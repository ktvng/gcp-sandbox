import importlib

simple_http_function_service = importlib.import_module("simple-http-function.entry")
def simple_http_function(args):
    return simple_http_function_service.entry(args)

secondary_function_service = importlib.import_module("secondary-function.entry")
def secondary_function(args):
    return secondary_function_service.entry(args)

autoscaler_service = importlib.import_module("autoscaler.entry")
def autoscaler(args):
    return autoscaler_service.entry(args)
