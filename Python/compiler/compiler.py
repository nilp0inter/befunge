from collections import namedtuple
from itertools import zip_longest
from pprint import pprint
import dataclasses
import enum
import sys
import typing

from llvmlite import ir


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


@dataclasses.dataclass(frozen=True)
class JUMP:
    cell: 'CELL'


@dataclasses.dataclass(frozen=True)
class CODE:
    cell: 'CELL'


@dataclasses.dataclass(frozen=True)
class BRANCH:
    up: typing.Union[JUMP, 'CELL', None] = dataclasses.field(default=None)
    right: typing.Union[JUMP, 'CELL', None] = dataclasses.field(default=None)
    down: typing.Union[JUMP, 'CELL', None] = dataclasses.field(default=None)
    left: typing.Union[JUMP, 'CELL', None] = dataclasses.field(default=None)


@dataclasses.dataclass(frozen=True)
class CELL:
    direction: Direction
    x: int
    y: int
    stringmode: bool
    content: str
    next: typing.Union[BRANCH, JUMP, 'CELL', None] = dataclasses.field(
                                                default=None,
                                                hash=False)

    @property
    def label(s):
        if s.stringmode:
            return None
        else:
            return f"L_{s.direction}_{s.x}_{s.y}"


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
        self.destinations = set()
        self.tree = self._walk(
            CELL(direction=Direction.RIGHT,
                 x=0,
                 y=0,
                 stringmode=False,
                 content=None))

    def _next(self, cell):
        if cell.stringmode:
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            # TODO yield
            return CELL(direction=cell.direction,  # same direction
                        x=x,
                        y=y,
                        stringmode=cell.content != '"',  # toggle on \"
                        content=c)
        elif cell.content == '"':
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            return CELL(direction=cell.direction,
                        x=x,
                        y=y,
                        stringmode=True,  # toggle on \"
                        content=c)
        elif Direction.valid(cell.content):
            newdirection = Direction(cell.content)
            x, y, c = self.grid.nextto(cell.x, cell.y, newdirection)
            return CELL(direction=newdirection,
                        x=x,
                        y=y,
                        stringmode=False,  # toggle on \"
                        content=c)
        elif cell.content == '_':
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.LEFT)
            left = CELL(direction=Direction.LEFT,
                        x=x,
                        y=y,
                        stringmode=False,  # toggle on \"
                        content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.RIGHT)
            right = CELL(direction=Direction.RIGHT,
                         x=x,
                         y=y,
                         stringmode=False,  # toggle on \"
                         content=c)
            return BRANCH(left=left, right=right)
        elif cell.content == '|':
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.UP)
            up = CELL(direction=Direction.UP,
                      x=x,
                      y=y,
                      stringmode=False,  # toggle on \"
                      content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.DOWN)
            down = CELL(direction=Direction.DOWN,
                        x=x,
                        y=y,
                        stringmode=False,  # toggle on \"
                        content=c)
            return BRANCH(up=up, down=down)
        elif cell.content == '?':
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.UP)
            up = CELL(direction=Direction.UP,
                      x=x,
                      y=y,
                      stringmode=False,  # toggle on \"
                      content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.RIGHT)
            right = CELL(direction=Direction.RIGHT,
                         x=x,
                         y=y,
                         stringmode=False,  # toggle on \"
                         content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.DOWN)
            down = CELL(direction=Direction.DOWN,
                        x=x,
                        y=y,
                        stringmode=False,  # toggle on \"
                        content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.LEFT)
            left = CELL(direction=Direction.LEFT,
                        x=x,
                        y=y,
                        stringmode=False,  # toggle on \"
                        content=c)
            return BRANCH(up=up, right=right, down=down, left=left)
        elif cell.content == '#':
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            x, y, c = self.grid.nextto(x, y, cell.direction)
            return CELL(direction=cell.direction,
                        x=x,
                        y=y,
                        stringmode=False,  # toggle on \"
                        content=c)
        elif cell.content == '@':
            return None
        else:
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            return CELL(direction=cell.direction,
                        x=x,
                        y=y,
                        stringmode=False,  # toggle on \"
                        content=c)

    def _walk(self, cell):
        if cell not in self.visited:
            self.visited.add(cell)
            n = self._next(cell)
            if n is None:
                # End of the program
                return None
            elif isinstance(n, CELL):
                return CODE(dataclasses.replace(cell, next=self._walk(n)))
            elif isinstance(n, BRANCH):
                return dataclasses.replace(
                    n,
                    up=self._walk(n.up) if n.up is not None else None,
                    right=self._walk(n.right) if n.right is not None else None,
                    down=self._walk(n.down) if n.down is not None else None,
                    left=self._walk(n.left) if n.left is not None else None)
        else:
            self.destinations.add(cell)
            return JUMP(cell)


class LLVMBuilder:
    def __init__(self, tree, name):
        self.blocks = dict()
        self.tree = tree

        self.module = ir.Module(name=name)
        main = ir.Function(module, ft, "main")
        builder = self._add_block(main, 'code')
        self._build_branch(builder, tree)

    def _add_block(self, builder, name):
        block = builder.append_basic_block(name)
        self.blocks[name] = block
        return ir.IRBuilder(block)

    def _build_instruction(self, builder, head, tail):
        pass

    def _build_branch(self, builder, tree):
        if not tree:
            return
        else:
            head, *tail = tree
            if isinstance(head, CELL):
                if head in self.tree.destinations:
                    builder = self._add_block(builder, head.label)
                self._build_instruction(builder, head, tail)
                self._build_branch(tail)
            elif isinstance(head, JUMP):
                builder.branch(self.blocks[head.label])
            else:
                return


def tree2module(tree, name):
    i32 = ir.IntType(32)
    ft = ir.FunctionType(i32, ())

    build


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as fp:
        code = fp.read()
        grid = Grid(code)
        tree = CodeTree(grid)
        pprint(tree.tree)
        pprint(tree.destinations)
