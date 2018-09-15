from collections import namedtuple
from itertools import zip_longest
from pprint import pprint
import enum
import sys


HEIGHT = 25
WIDTH = 80


class Direction(enum.Enum):
    UP = '^'
    RIGHT = '>'
    DOWN = 'v'
    LEFT = '<'

    @classmethod
    def valid(cls, value):
        try:
            cls(value)
        except ValueError:
            return False
        else:
            return True


CODE = namedtuple('CODE', ['cell'])
JUMP = namedtuple('JUMP', ['cell'])
CELL = namedtuple('CELL', ['direction', 'x', 'y', 'stringmode', 'content'])


class Grid(dict):
    def __init__(self, s, height=HEIGHT, width=WIDTH):
        self.height = height
        self.width = width
        for row, y in zip_longest(s.splitlines(), range(height), fillvalue=None):
            if row is None:
                row = ""
            for char, x in zip_longest(row, range(width), fillvalue=None):
                if x is None:
                    break
                elif char is None:
                    self[(x,y)] = ' '
                else:
                    self[(x,y)] = char
            if y is None:
                break

    def nextto(self, x, y, d):
        nx, ny = x, y
        if d is Direction.UP:
            ny -= 1
        elif d is Direction.RIGHT:
            nx += 1
        elif d is Direction.DOWN:
            ny += 1
        elif d is Direction.LEFT:
            nx -= 1
        else:
            raise ValueError(d)

        nx %= self.width
        ny %= self.height

        return (nx, ny, self[(nx, ny)])


class CodeTree:
    def __init__(self, grid):
        self.grid = grid
        self.visited = set()

    def _next(self, cell):
        if cell.stringmode:
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            # TODO yield
            yield CELL(direction=cell.direction,  # same direction
                       x=x,
                       y=y,
                       stringmode=cell.content != '"',  # toggle on \"
                       content=c)
        elif cell.content == '"':
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            yield CELL(direction=cell.direction,
                       x=x,
                       y=y,
                       stringmode=True,  # toggle on \"
                       content=c)
        elif Direction.valid(cell.content):
            newdirection = Direction(cell.content)
            x, y, c = self.grid.nextto(cell.x, cell.y, newdirection)
            yield CELL(direction=newdirection,
                       x=x,
                       y=y,
                       stringmode=False,  # toggle on \"
                       content=c)
        elif cell.content == '_':
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.LEFT)
            yield CELL(direction=Direction.LEFT,
                       x=x,
                       y=y,
                       stringmode=False,  # toggle on \"
                       content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.RIGHT)
            yield CELL(direction=Direction.RIGHT,
                       x=x,
                       y=y,
                       stringmode=False,  # toggle on \"
                       content=c)
        elif cell.content == '|':
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.UP)
            yield CELL(direction=Direction.UP,
                       x=x,
                       y=y,
                       stringmode=False,  # toggle on \"
                       content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.DOWN)
            yield CELL(direction=Direction.DOWN,
                       x=x,
                       y=y,
                       stringmode=False,  # toggle on \"
                       content=c)
        elif cell.content == '?':
            for direction in Direction:
                x, y, c = self.grid.nextto(cell.x, cell.y, direction)
                yield CELL(direction=direction,
                           x=x,
                           y=y,
                           stringmode=False,  # toggle on \"
                           content=c)
        elif cell.content == '#':
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            x, y, c = self.grid.nextto(x, y, cell.direction)
            yield CELL(direction=cell.direction,
                       x=x,
                       y=y,
                       stringmode=False,  # toggle on \"
                       content=c)
        elif cell.content == '@':
            # No next
            pass
        else:
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            yield CELL(direction=cell.direction,
                       x=x,
                       y=y,
                       stringmode=False,  # toggle on \"
                       content=c)

    def _walk(self, cell):
        if cell not in self.visited:
            self.visited.add(cell)
            yield CODE(cell)
            paths = list(self._next(cell))
            if not paths:
                pass
            elif len(paths) == 1:
                yield from self._walk(paths[0])
            else:
                yield [list(self._walk(p)) for p in paths]
        else:
            yield JUMP(cell)

    def walk(self):
        return list(
            self._walk(
                CELL(direction=Direction.RIGHT,
                     x=-1,
                     y=0,
                     stringmode=False,
                     content=None)))[1:]

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as code:
        pprint(CodeTree(grid=Grid(code.read())).walk())
