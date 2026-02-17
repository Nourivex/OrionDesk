COMMAND_DEFINITIONS = [
    {
        "keyword": "open",
        "usage": "open <app_alias>",
        "min_args": 1,
        "handler_name": "_handle_open",
        "dangerous": False,
    },
    {
        "keyword": "search",
        "usage": "search file <query>",
        "min_args": 2,
        "first_arg_equals": "file",
        "handler_name": "_handle_search",
        "dangerous": False,
    },
    {
        "keyword": "sys",
        "usage": "sys info",
        "min_args": 1,
        "max_args": 1,
        "first_arg_equals": "info",
        "handler_name": "_handle_sys",
        "dangerous": False,
    },
]
