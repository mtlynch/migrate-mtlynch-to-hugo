def make(src, alt=None, caption=None, max_width=None, has_border=False):
    shortcode_parts = ['{{< img']

    attrsMap = {
        'src': src,
        'alt': alt,
        'caption': caption,
        'maxWidth': max_width,
        'hasBorder': has_border,
    }
    attrs = [(k, v) for (k, v) in attrsMap.items() if v]
    for attr_name, attr_value in attrs:
        shortcode_parts.append('%s="%s"' % (attr_name, attr_value))

    shortcode_parts.append('>}}')
    return ' '.join(shortcode_parts)
