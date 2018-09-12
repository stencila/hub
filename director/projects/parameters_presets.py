"""
Simple method of defining presets for selection of `SessionParameters` of a `Project`
"""

parameters_presets = [
    {
        'name': 'Small',
        'memory': 1,
        'cpu': 5,
        'network': 10,
        'lifetime': 30,
        'timeout': 10
    },
    {
        'name': 'Medium',
        'memory': 2,
        'cpu': 10,
        'network': 20,
        'lifetime': 60,
        'timeout': 30
    },
    {
        'name': 'Large',
        'memory': 4,
        'cpu': 20,
        'network': 50,
        'lifetime': None,
        'timeout': 60
    }
]
