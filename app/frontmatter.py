import yaml


def filter_fields(contents, field_whitelist):
    filtered = {}
    for k, v in _parse_frontmatter(contents).items():
        if k in field_whitelist:
            filtered[k] = v
    return _replace_frontmatter(contents, filtered)


def translate_fields(contents, field_mappings):
    translated = {}
    for k, v in _parse_frontmatter(contents).items():
        mapped_key = k
        if k in field_mappings:
            mapped_key = field_mappings[k]
        translated[mapped_key] = v
    return _replace_frontmatter(contents, translated)


def insert_field(contents, key, value):
    parsed = _parse_frontmatter(contents)
    parsed[key] = value
    return _replace_frontmatter(contents, parsed)


def _parse_frontmatter(contents):
    lines = contents.split('\n')
    frontmatter_start = _find_frontmatter_start(lines)
    frontmatter_end = _find_frontmatter_end(lines, frontmatter_start)
    frontmatter_raw = '\n'.join(lines[frontmatter_start + 1:frontmatter_end])
    return yaml.safe_load(frontmatter_raw)


def _replace_frontmatter(contents, new_frontmatter):
    lines = contents.split('\n')
    frontmatter_start = _find_frontmatter_start(lines)
    frontmatter_end = _find_frontmatter_end(lines, frontmatter_start)
    return ('\n'.join(lines[:frontmatter_start + 1]) + '\n' +
            _dump_yaml(new_frontmatter) + '\n'.join(lines[frontmatter_end:]))


def _dump_yaml(d):
    return yaml.safe_dump(d, default_flow_style=False, sort_keys=False)


def _find_frontmatter_start(lines):
    for i, line in enumerate(lines):
        if line.strip() == '---':
            return i


def _find_frontmatter_end(lines, start_index):
    for i in range(start_index + 1, len(lines)):
        line = lines[i].strip()
        if line == '---':
            return i
