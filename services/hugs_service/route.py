

def hugs_functions(function, args):
    """These are all of the functions for the hug service"""
    if function == "hello":
        from hugs_service.hello import hello as _hello
        return _hello(args)
    if function == "goodbye":
        from hugs_service.goodbye import goodbye as _goodbye
        return _goodbye(args)
    else:
        from admin.handler import MissingFunctionError
        raise MissingFunctionError()


if __name__ == "__main__":
    import fdk
    from admin.handler import create_async_handler
    fdk.handle(create_async_handler(hugs_functions))