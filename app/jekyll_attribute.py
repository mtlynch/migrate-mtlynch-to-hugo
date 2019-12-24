import re


def parse(line, attribute_name):
    m = re.search(r'%s\s*=\s*"([^"]+)"' % attribute_name, line)
    if m:
        return m.group(1)
    m = re.search(r"%s\s*=\s*'([^']+)'" % attribute_name, line)
    if m:
        return m.group(1)
    return None
