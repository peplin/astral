DEFAULT_PROCESS_LOG_FMT = """
    [%(asctime)s: %(levelname)s/%(processName)s] %(message)s
""".strip()
DEFAULT_LOG_FMT = '[%(asctime)s: %(levelname)s] %(message)s'
DEFAULT_TASK_LOG_FMT = """[%(asctime)s: %(levelname)s/%(processName)s] \
%(task_name)s[%(task_id)s]: %(message)s"""


def str_to_bool(term, table={"false": False, "no": False, "0": False,
                             "true":  True, "yes": True,  "1": True}):
    try:
        return table[term.lower()]
    except KeyError:
        raise TypeError("%r can not be converted to type bool" % (term, ))


class Option(object):
    typemap = dict(string=str, int=int, float=float, any=lambda v: v,
                   bool=str_to_bool, dict=dict, tuple=tuple)

    def __init__(self, default=None, *args, **kwargs):
        self.default = default
        self.type = kwargs.get("type") or "string"

    def to_python(self, value):
        return self.typemap[self.type](value)


NAMESPACES = {
    "ASTRAL": {
        "SOME_SETTING": Option(False, type="bool"),
    },
    "ASTRALNODE": {
        "LOG_FORMAT": Option(DEFAULT_PROCESS_LOG_FMT),
        "LOG_COLOR": Option(type="bool"),
        "LOG_LEVEL": Option("WARN"),
        "LOG_FILE": Option(),
    },
}


def _flatten(d, ns=""):
    acc = []
    for key, value in d.iteritems():
        if isinstance(value, dict):
            acc.extend(_flatten(value, ns=key + '_'))
        else:
            acc.append((ns + key, value.default))
    return acc

DEFAULTS = dict(_flatten(NAMESPACES))
