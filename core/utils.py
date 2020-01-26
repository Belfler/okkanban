from collections import namedtuple


Link = namedtuple('Link', 'text url')
Button = namedtuple('Button', 'text url is_warning', defaults=(None, False))
