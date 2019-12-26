import re


def iframes_to_shortcodes(contents):
    lines = []
    for line in contents.split('\n'):
        m = re.search(
            r'<iframe .*src="https://(www.)?youtube.+/([_\-a-zA-Z0-9]{11})["\?]',
            line)
        if m:
            line = '{{< youtube %s >}}' % m.group(2)
        lines.append(line)
    return '\n'.join(lines)
