import jekyll_attribute


def to_inline_file_shortcode(contents):
    lines = []
    for line in contents.split('\n'):
        if line.startswith('{% include files.html'):
            line = _translate_include(line)
        lines.append(line)
    return '\n'.join(lines)


def _translate_include(line):
    title = jekyll_attribute.parse(line, 'title')
    language = jekyll_attribute.parse(line, 'language')
    return '{{< inline-file filename="%s" language="%s" >}}' % (title, language)
