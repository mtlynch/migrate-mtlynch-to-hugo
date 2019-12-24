import collections
import re

LegacyImageReference = collections.namedtuple(
    'LegacyImageReference', ['src', 'alt', 'fig_caption', 'max_width'])


def parse(line):
    return LegacyImageReference(
        src=_parse_attribute(line, 'file'),
        alt=_parse_attribute(line, 'alt'),
        fig_caption=_parse_attribute(line, 'fig_caption'),
        max_width=_parse_attribute(line, 'max_width'),
    )


def _parse_attribute(line, attribute_name):
    m = re.search(r'%s="([^"]+)"' % attribute_name, line)
    if not m:
        return None
    return m.group(1)
