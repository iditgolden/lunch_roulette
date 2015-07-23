LOGGING_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simpleFormatter': {
            'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        }
    },

    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simpleFormatter',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'requests': {
            'level': 'WARNING',
            'handlers': ['consoleHandler'],
            'propagate': 'no',
            'qualname': 'requests.packages.urllib3.connectionpool'
        },
        'selenium_framework': {
            'level': 'INFO',
            'handlers': ['consoleHandler'],
            'propagate': False,
        },
        'selenium': {
            'level': 'ERROR',
            'handlers': ['consoleHandler'],
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['consoleHandler'],
        'level': 'DEBUG',
    }
}