"""Minimaler GEDCOM-5.5.1-Baum: einlesen, bearbeiten, schreiben."""
import datetime
import re

MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


class Node:
    __slots__ = ('tag', 'xref', 'value', 'children')

    def __init__(self, tag, value=None, xref=None, children=None):
        self.tag, self.value, self.xref = tag, value, xref
        self.children = children or []

    def add(self, tag, value=None, xref=None):
        n = Node(tag, value, xref)
        self.children.append(n)
        return n

    def first(self, tag):
        return next((c for c in self.children if c.tag == tag), None)

    def all(self, tag):
        return [c for c in self.children if c.tag == tag]

    def val(self, tag, default=None):
        c = self.first(tag)
        return c.value if c is not None else default

    def lines(self, level=0):
        head = f'{level} ' + (f'{self.xref} ' if self.xref else '') + self.tag
        if self.value not in (None, ''):
            head += ' ' + self.value
        out = [head]
        for c in self.children:
            out.extend(c.lines(level + 1))
        return out


LINE = re.compile(r'^(\d+) (?:(@[^@]+@) )?(\S+)(?: (.*))?$')


def parse(text):
    root = Node('ROOT')
    stack = [(-1, root)]
    for raw in text.splitlines():
        m = LINE.match(raw)
        if not m:
            raise ValueError(raw)
        lvl = int(m.group(1))
        n = Node(m.group(3), m.group(4), m.group(2))
        while stack[-1][0] >= lvl:
            stack.pop()
        stack[-1][1].children.append(n)
        stack.append((lvl, n))
    return root


def serialize(root):
    out = []
    for r in root.children:
        out.extend(r.lines(0))
    return '\n'.join(out) + '\n'


DATE = re.compile(r'^(?:(?:ABT|BEF|AFT|EST|CAL) )?(?:(\d{1,2}) )?(?:([A-Z]{3}) )?(\d{4})$')


def parse_date(s):
    """-> (Jahr, Monat|None, Tag|None) oder None"""
    m = DATE.match((s or '').strip())
    if not m:
        return None
    mon = MONTHS.index(m.group(2)) + 1 if m.group(2) else None
    return int(m.group(3)), mon, int(m.group(1)) if m.group(1) else None


def to_date(s):
    d = parse_date(s)
    if not d:
        return None
    return datetime.date(d[0], d[1] or 7, d[2] or 1)


def event_date(node):
    return to_date(node.val('DATE')) if node is not None else None
