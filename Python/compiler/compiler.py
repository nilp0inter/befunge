from collections import namedtuple
from itertools import zip_longest
from pprint import pprint
import dataclasses
import enum
import pickle
import sys
import typing

from llvmlite import ir


HEIGHT = 25
WIDTH = 80


class Direction(enum.Enum):
    WHATEVER = None
    UP = '^'
    DOWN = 'v'
    LEFT = '<'
    RIGHT = '>'

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
    up: typing.Union[JUMP, CODE, None] = dataclasses.field(default=None)
    down: typing.Union[JUMP, CODE, None] = dataclasses.field(default=None)
    left: typing.Union[JUMP, CODE, None] = dataclasses.field(default=None)
    right: typing.Union[JUMP, CODE, None] = dataclasses.field(default=None)


@dataclasses.dataclass(frozen=True)
class CELL:
    direction: Direction
    x: int
    y: int
    stringmode: bool
    content: str
    next: typing.Union[BRANCH, JUMP, 'CELL', None] =\
        dataclasses.field(default=None, hash=False, compare=False)

    @property
    def label(s):
        if s.stringmode:
            return None
        else:
            return f"L_{s.direction.name}_{s.x}_{s.y}"


class Grid(dict):
    def __init__(self, s, height=HEIGHT, width=WIDTH):
        self.height = height
        self.width = width
        for row, y in zip_longest(s.splitlines(),
                                  range(height),
                                  fillvalue=None):
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
                 content=self.grid[(0, 0)]))

    def _next(self, cell):
        if cell.stringmode:
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            return CELL(
                direction=cell.direction,  # same direction
                x=x,
                y=y,
                stringmode=cell.content != '"',
                content=c)
        elif cell.content == '"':
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            return CELL(
                direction=cell.direction if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=True,
                content=c)
        elif Direction.valid(cell.content):
            newdirection = Direction(cell.content)
            x, y, c = self.grid.nextto(cell.x, cell.y, newdirection)
            return CELL(
                direction=newdirection if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
        elif cell.content == '_':
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.LEFT)
            left = CELL(
                direction=Direction.LEFT if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.RIGHT)
            right = CELL(
                direction=Direction.RIGHT if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
            return BRANCH(left=left, right=right)
        elif cell.content == '|':
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.UP)
            up = CELL(
                direction=Direction.UP if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.DOWN)
            down = CELL(
                direction=Direction.DOWN if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
            return BRANCH(up=up, down=down)
        elif cell.content == '?':
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.UP)
            up = CELL(
                direction=Direction.UP if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.DOWN)
            down = CELL(
                direction=Direction.DOWN if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.LEFT)
            left = CELL(
                direction=Direction.LEFT if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
            x, y, c = self.grid.nextto(cell.x, cell.y, Direction.RIGHT)
            right = CELL(
                direction=Direction.RIGHT if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
            return BRANCH(up=up, right=right, down=down, left=left)
        elif cell.content == '#':
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            x, y, c = self.grid.nextto(x, y, cell.direction)
            return CELL(
                direction=cell.direction if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)
        elif cell.content == '@':
            return None
        else:
            x, y, c = self.grid.nextto(cell.x, cell.y, cell.direction)
            return CELL(
                direction=cell.direction if c != '@' else Direction.WHATEVER,
                x=x,
                y=y,
                stringmode=False,
                content=c)

    def _walk(self, cell):
        if cell not in self.visited:
            self.visited.add(cell)
            n = self._next(cell)
            if n is None:
                # End of the program
                return CODE(cell)
            elif isinstance(n, CELL):
                return CODE(dataclasses.replace(cell, next=self._walk(n)))
            elif isinstance(n, BRANCH):
                n = dataclasses.replace(
                    n,
                    up=self._walk(n.up) if n.up is not None else None,
                    down=self._walk(n.down) if n.down is not None else None,
                    left=self._walk(n.left) if n.left is not None else None,
                    right=self._walk(n.right) if n.right is not None else None)
                return CODE(dataclasses.replace(cell, next=n))
        else:
            self.destinations.add(cell)
            return JUMP(cell)


i64 = ir.IntType(64)
stacktype = ir.ArrayType(i64, 1000)
ft = ir.FunctionType(i64, ())


class LLVMBuilder:
    def __init__(self, tree, name, stack_size=1000, safe_stack=True):
        self.blocks = dict()
        self.tree = tree
        if safe_stack:
            self._pop_to = self._safe_pop_to
            self._peek_to = self._safe_peek_to
        else:
            self._pop_to = self._unsafe_pop_to
            self._peek_to = self._unsafe_peek_to

        self.module = ir.Module(name=name)

        # External functions
        self._f_putchar = ir.Function(
            self.module,
            ir.FunctionType(ir.IntType(64), [ir.IntType(64)]),
            'putchar')
        self._f_srandom = ir.Function(
            self.module,
            ir.FunctionType(ir.VoidType(), [ir.IntType(64)]),
            'srandom')
        self._f_random = ir.Function(
            self.module,
            ir.FunctionType(ir.IntType(64), []),
            'random')
        self._f_time = ir.Function(
            self.module,
            ir.FunctionType(ir.IntType(64), [ir.IntType(64).as_pointer()]),
            'time')

        main = ir.Function(self.module, ft, 'main')
        builder = self._add_block(main, 'code')

        # Global variables
        self._v_stack_ptr = builder.alloca(stacktype, size=stack_size,
                                           name='stack')
        self._v_sp_ptr = builder.alloca(i64, name='sp')
        builder.store(i64(0), self._v_sp_ptr)
        self._v_a_ptr = builder.alloca(i64, name='a')
        self._v_b_ptr = builder.alloca(i64, name='b')
        self._v_c_ptr = builder.alloca(i64, name='x')

        # Init PRNG
        builder.call(self._f_srandom,
                     [builder.call(
                         self._f_time,
                         [ir.Constant(ir.IntType(64).as_pointer(), 'null')])])

        self._build_branch(builder, tree.tree)

        try:
            builder.ret_void()
        except AssertionError:
            pass

    def _add_block(self, builder, name):
        block = builder.append_basic_block(name)
        self.blocks[name] = block
        builder = ir.IRBuilder(block)
        return builder

    def _safe_pop_to(self, builder, dst_ptr=None):
        sp = builder.load(self._v_sp_ptr)
        prep = builder.icmp_unsigned('==', sp, i64(0))
        with builder.if_else(prep) as (then, otherwise):
            with then:
                if dst_ptr is not None:
                    builder.store(i64(0), dst_ptr)
            with otherwise:
                sp = builder.sub(sp, i64(1))
                elem_addr = builder.gep(self._v_stack_ptr, [sp])
                elem = builder.load(builder.bitcast(elem_addr, i64.as_pointer()))
                builder.store(elem, dst_ptr)
                builder.store(sp, self._v_sp_ptr)

    def _unsafe_pop_to(self, builder, dst_ptr=None):
        sp = builder.load(self._v_sp_ptr)
        sp = builder.sub(sp, i64(1))
        elem_addr = builder.gep(self._v_stack_ptr, [sp])
        elem = builder.load(builder.bitcast(elem_addr, i64.as_pointer()))
        builder.store(elem, dst_ptr)
        builder.store(sp, self._v_sp_ptr)

    def _safe_peek_to(self, builder, dst_ptr):
        sp = builder.load(self._v_sp_ptr)
        prep = builder.icmp_unsigned('==', sp, i64(0))
        with builder.if_else(prep) as (then, otherwise):
            with then:
                builder.store(i64(0), dst_ptr)
            with otherwise:
                sp = builder.sub(sp, i64(1))
                elem_addr = builder.gep(self._v_stack_ptr, [sp])
                elem = builder.load(builder.bitcast(elem_addr, i64.as_pointer()))
                builder.store(elem, dst_ptr)

    def _unsafe_peek_to(self, builder, dst_ptr):
        sp = builder.load(self._v_sp_ptr)
        sp = builder.sub(sp, i64(1))
        elem_addr = builder.gep(self._v_stack_ptr, [sp])
        elem = builder.load(builder.bitcast(elem_addr, i64.as_pointer()))
        builder.store(elem, dst_ptr)

    def _push_from(self, builder, src_ptr):
        sp = builder.load(self._v_sp_ptr)
        elem_addr = builder.gep(self._v_stack_ptr, [sp])
        value = builder.load(src_ptr)
        builder.store(value, builder.bitcast(elem_addr, i64.as_pointer()))
        builder.store(builder.add(sp, i64(1)), self._v_sp_ptr)

    def _push_value(self, builder, value):
        sp = builder.load(self._v_sp_ptr)
        elem_addr = builder.gep(self._v_stack_ptr, [sp])
        builder.store(value, builder.bitcast(elem_addr, i64.as_pointer()))
        builder.store(builder.add(sp, i64(1)), self._v_sp_ptr)

    def _build_instruction(self, builder, cell):
        if cell.stringmode:
            if cell.content != '"':
                self._push_value(builder, i64(ord(cell.content)))
        elif cell.content in '0123456789':
            self._push_value(builder, i64(int(cell.content)))
        elif cell.content == '+':
            self._pop_to(builder, self._v_a_ptr)
            self._pop_to(builder, self._v_b_ptr)
            a = builder.load(self._v_a_ptr)
            b = builder.load(self._v_b_ptr)
            self._push_value(builder, builder.add(a, b))
        elif cell.content == '-':
            self._pop_to(builder, self._v_a_ptr)
            self._pop_to(builder, self._v_b_ptr)
            a = builder.load(self._v_a_ptr)
            b = builder.load(self._v_b_ptr)
            self._push_value(builder, builder.sub(a, b))
        elif cell.content == '*':
            self._pop_to(builder, self._v_a_ptr)
            self._pop_to(builder, self._v_b_ptr)
            a = builder.load(self._v_a_ptr)
            b = builder.load(self._v_b_ptr)
            self._push_value(builder, builder.mul(a, b))
        elif cell.content == '/':
            self._pop_to(builder, self._v_a_ptr)
            self._pop_to(builder, self._v_b_ptr)
            a = builder.load(self._v_a_ptr)
            b = builder.load(self._v_b_ptr)
            self._push_value(builder, builder.sdiv(a, b))
        elif cell.content == '%':
            self._pop_to(builder, self._v_a_ptr)
            self._pop_to(builder, self._v_b_ptr)
            a = builder.load(self._v_a_ptr)
            b = builder.load(self._v_b_ptr)
            self._push_value(builder, builder.srem(a, b))
        elif cell.content == '`':
            self._pop_to(builder, self._v_a_ptr)
            self._pop_to(builder, self._v_b_ptr)
            a = builder.load(self._v_a_ptr)
            b = builder.load(self._v_b_ptr)
            prep = builder.icmp_unsigned('>', a, b)
            with builder.if_else(prep) as (then, otherwise):
                with then:
                    self._push_value(builder, i64(1))
                with otherwise:
                    self._push_value(builder, i64(0))
        elif cell.content == '&':
            raise NotImplemented
        elif cell.content == '~':
            raise NotImplemented
        elif cell.content == '.':
            raise NotImplemented
        elif cell.content in ',':
            self._pop_to(builder, self._v_a_ptr)
            a = builder.load(self._v_a_ptr)
            builder.call(self._f_putchar, [a])
        elif cell.content == ':':
            self._peek_to(builder, self._v_a_ptr)
            self._push_from(builder, self._v_a_ptr)
        elif cell.content == '\\':
            self._pop_to(builder, self._v_a_ptr)
            self._pop_to(builder, self._v_b_ptr)
            self._push_from(builder, self._v_a_ptr)
            self._push_from(builder, self._v_b_ptr)
        elif cell.content == '!':
            self._pop_to(builder, self._v_a_ptr)
            a = builder.load(self._v_a_ptr)
            prep = builder.icmp_unsigned('==', i64(0), a)
            with builder.if_else(prep) as (then, otherwise):
                with then:
                    self._push_value(builder, i64(1))
                with otherwise:
                    self._push_value(builder, i64(0))
        elif cell.content in '_|':
            # Branches
            if cell.content == '_':
                then_code = cell.next.left
                else_code = cell.next.right
            else:
                then_code = cell.next.up
                else_code = cell.next.down

            self._pop_to(builder, self._v_a_ptr)
            a = builder.load(self._v_a_ptr)

            prep = builder.icmp_unsigned('!=', i64(0), a)
            with builder.if_else(prep) as (then_block, else_block):
                with then_block:
                    self._build_branch(builder, then_code)
                with else_block:
                    self._build_branch(builder, else_code)
            builder.unreachable()
        elif cell.content == '?':
            up = self._add_block(builder, f"{cell.label}_UP")
            self._build_branch(up, cell.next.up)
            down = self._add_block(builder, f"{cell.label}_DOWN")
            self._build_branch(down, cell.next.down)
            left = self._add_block(builder, f"{cell.label}_LEFT")
            self._build_branch(left, cell.next.left)
            right = self._add_block(builder, f"{cell.label}_RIGHT")
            self._build_branch(right, cell.next.right)

            a = builder.call(self._f_random, [])

            a = builder.srem(a, i64(4))  # TODO: prove no bias
            switch = builder.switch(a, right.block)
            switch.add_case(i64(0), up.block)
            switch.add_case(i64(1), down.block)
            switch.add_case(i64(2), left.block)
        elif cell.content == '$':
            self._pop_to(builder)
        elif cell.content == '@':
            try:
                builder.ret(i64(0))
            except AssertionError:
                # Closed already?
                print(f"; CLOSED {cell.x} {cell.y}")
        elif cell.content in 'pg':
            raise ValueError('p & g are not allowed')
        else:
            print("; Skipping %r" % cell.content)

    def _build_branch(self, builder, tree):
        if isinstance(tree, CODE):
            if tree.cell in self.tree.destinations:
                newbuilder = self._add_block(builder, tree.cell.label)
                try:
                    builder.branch(self.blocks[tree.cell.label])  # Implicit jump
                except AssertionError:
                    # Closed already?
                    print(f"; CLOSED {tree.cell.x} {tree.cell.y}")
                builder = newbuilder
            self._build_instruction(builder, tree.cell)
            if not isinstance(tree.cell.next, BRANCH):
                # Because is already built by instruction
                self._build_branch(builder, tree.cell.next)
        elif isinstance(tree, JUMP):
            try:
                builder.branch(self.blocks[tree.cell.label])
            except:
                pass
        elif tree is None:
            pass
        else:
            raise ValueError('Invalid continuation %r' % type(tree))


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as fp:
        code = fp.read()
        grid = Grid(code)
        tree = CodeTree(grid)
        # with open(sys.argv[1] + '.tree', 'wb') as tdump:
        #     pickle.dump(tree.tree, tdump)
        builder = LLVMBuilder(tree, 'mymodule', safe_stack=False, stack_size=128)
        print(builder.module)
