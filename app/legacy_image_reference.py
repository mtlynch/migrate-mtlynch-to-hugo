import collections
import logging
import re

logger = logging.getLogger(__name__)

LegacyImageReference = collections.namedtuple(
    'LegacyImageReference',
    ['src', 'alt', 'fig_caption', 'max_width', 'has_border'])


def parse(line):
    return LegacyImageReference(src=_parse_attribute(line, 'file'),
                                alt=_parse_attribute(line, 'alt'),
                                fig_caption=_parse_attribute(
                                    line, 'fig_caption'),
                                max_width=_parse_attribute(line, 'max_width'),
                                has_border=_check_border(line))


def _parse_attribute(line, attribute_name):
    m = re.search(r'%s="([^"]+)"' % attribute_name, line)
    if not m:
        return None
    return m.group(1)


def _check_border(line):
    class_attr = _parse_attribute(line, 'class')
    if not class_attr:
        return False
    if class_attr == 'img-border':
        return True
    else:
        logger.error('Unrecognized class value: %s', class_attr)
        return False
