COMMAND_DEFINITIONS = [
    {
        "keyword": "delete",
        "usage": "delete <path>",
        "min_args": 1,
        "handler_name": "_execute_dangerous",
        "dangerous": True,
    },
    {
        "keyword": "kill",
        "usage": "kill <process_name_or_pid>",
        "min_args": 1,
        "handler_name": "_execute_dangerous",
        "dangerous": True,
    },
    {
        "keyword": "shutdown",
        "usage": "shutdown",
        "min_args": 0,
        "max_args": 0,
        "handler_name": "_execute_dangerous",
        "dangerous": True,
    },
]
