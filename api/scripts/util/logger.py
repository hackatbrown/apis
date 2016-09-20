# vim: set ts=4 sts=4 sw=4 expandtab:
import sys

_colors = {
    'INFO': '\033[94m',
    'OK': '\033[92m',
    'WARN': '\033[1m\033[93m',
    'ERR': '\033[1m\033[91m',
}


class Logger:
    ERR = 'ERR'
    WARN = 'WARN'
    OK = 'OK'
    INFO = 'INFO'
    __ENDC = '\033[0m'

    def log(self, msg, lvl=None):
        if lvl is None:
            lvl = self.INFO
        colorize = sys.stdout.isatty() and lvl in _colors

        if colorize:
            print(_colors[lvl], end="")
        print('[' + "%4s" % lvl + '] ', end="")
        if colorize:
            print(Logger.__ENDC, end="")

        print(msg)


_Logger = Logger()


def log(msg, lvl=Logger.INFO):
    _Logger.log(msg, lvl)
