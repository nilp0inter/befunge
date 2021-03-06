#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "grid.h"
#include "runtime.h"
#include "stack.h"

void rt_init(tRuntime * rt)
{
	srand(time(NULL));
	rt->width = ROW_SIZE;
	rt->height = COL_SIZE;
	rt->x = rt->y = 0;
	rt->direction = RIGHT;
	rt->stringmode = false;
	rt->halt = false;
	grid_init(rt->grid);
	stack_init(&rt->stack);
}

int rt_fload(tRuntime * rt, char const *path)
{
	FILE *fp = fopen(path, "r");
	if (!fp) {
		printf("Cannot load file.\n");
		return -1;
	}
	grid_load(fp, rt->grid);
	return 0;
}

char rt_get_cell_at(tRuntime * rt, unsigned short int x,
			   unsigned short int y)
{
	return rt->grid[y][x];
}

char rt_get_cell(tRuntime * rt)
{
	return rt->grid[rt->y][rt->x];
}

void rt_next(tRuntime * rt)
{
	switch (rt->direction) {
	case UP:
		--rt->y;
		rt->y %= rt->height;
		break;
	case RIGHT:
		++rt->x;
		rt->x %= rt->width;
		break;
	case DOWN:
		++rt->y;
		rt->y %= rt->height;
		break;
	case LEFT:
		--rt->x;
		rt->x %= rt->width;
		break;
	}
}

void rt_step(tRuntime * rt)
{

#define POP() stack_pop(&rt->stack)
#define PUSH(v) stack_push(&rt->stack, v)

	char op = rt_get_cell(rt);
	unsigned long int a, b;

	if (rt->stringmode) {
		if (op == '"')
			rt->stringmode = false;
		else
			PUSH((signed long int)op);
		rt_next(rt);
	} else {
		switch (op) {
		case ' ':
			break;

			// " (stringmode)
			// Toggles 'stringmode'
		case '"':
			rt->stringmode = true;
			break;

			// $ (pop)         <value>
			// pops <value> but does nothing
		case '$':
			POP();
			break;

			// . (pop)         <value>
			// outputs <value> as integer
		case '.':
			printf("%ld ", POP());
			break;

			// , (pop)         <value>
			// outputs <value> as ASCII
		case ',':
			putchar((char)POP());
			break;

			// + (add)         <value1> <value2>
			// <value1 + value2>
		case '+':
			PUSH(POP() + POP());
			break;

			// - (subtract)    <value1> <value2>
			// <value1 - value2>
		case '-':
			a = POP();
			b = POP();
			PUSH(b - a);
			break;

			// * (multiply)    <value1> <value2>
			// <value1 * value2>
		case '*':
			PUSH(POP() * POP());
			break;

			// / (divide)      <value1> <value2>
			// <value1 / value2> (nb. integer)
		case '/':
			a = POP();
			b = POP();
			assert(a != 0);
			PUSH(b / a);
			break;

			// % (modulo)      <value1> <value2>
			// <value1 mod value2>
		case '%':
			a = POP();
			b = POP();
			assert(a != 0);
			PUSH(b % a);
			break;

			// > (right)
			// PC -> right
		case '>':
			rt->direction = RIGHT;
			break;

			// < (left)
			// PC -> left
		case '<':
			rt->direction = LEFT;
			break;

			// ^ (up)
			// PC -> up
		case '^':
			rt->direction = UP;
			break;

			// v (down)
			// PC -> down
		case 'v':
			rt->direction = DOWN;
			break;

			// _ (horizontal if) <boolean value>
			// PC->left if <value>, else PC->right
		case '_':
			rt->direction = POP()? LEFT : RIGHT;
			break;

			// | (vertical if)   <boolean value>
			// PC->up if <value>, else PC->down
		case '|':
			rt->direction = POP()? UP : DOWN;
			break;

			// : (dup)         <value>
			// <value> <value>
		case ':':
			PUSH(stack_peek(&rt->stack));
			break;

			// \ (swap)        <value1> <value2>
			// <value2> <value1>
		case '\\':
			a = POP();
			b = POP();
			PUSH(a);
			PUSH(b);
			break;

			// # (bridge)
			// 'jumps' PC one farther; skips over next command
		case '#':
			rt_next(rt);
			break;

			// g (get)         <x> <y>
			// <value at (x,y)>
		case 'g':
			a = POP(); // y
			b = POP(); // x
			PUSH((unsigned long int)rt_get_cell_at(rt, b, a));
			break;

			// p (put)         <value> <x> <y>
			// puts <value> at (x,y)
		case 'p':
			a = POP(); // y
			b = POP(); // x
			grid_put(rt->grid, POP(), b, a);
			break;

			// @ (end)
			// ends program
		case '@':
			rt->halt = true;
			return;

			// ! (not)         <value>
			// <0 if value non-zero, 1 otherwise>
		case '!':
			PUSH(POP() ? 0 : 1);
			break;

			// ` (greater)     <value1> <value2>
			// <1 if value1 > value2, 0 otherwise>
		case '`':
			PUSH(POP() > POP());
			break;

			// ? (random)
			// PC -> right? left? up? down? ???
		case '?':
			rt->direction = (tDirection) rand() % 4;
			break;

			// 0-9
		case '0':
		case '1':
		case '2':
		case '3':
		case '4':
		case '5':
		case '6':
		case '7':
		case '8':
		case '9':
			PUSH(op - '0');
			break;
			// & (input value)
			// <value user entered>
		case '&':
			{
				signed long int tmp;
				while (scanf("%ld", &tmp) != 1) {
				}
				PUSH(tmp);
			}
			break;
			// ~ (input character)
			// <character user entered>
		case '~':
			{
				char tmp;
				while (scanf("%c", &tmp) != 1) {
				}
				PUSH((unsigned long int)tmp);
			}
			break;
		}
		rt_next(rt);
	}

}

void rt_exec(tRuntime * rt)
{
	/* grid_print(rt->grid); */
	for (unsigned long int c=0; !rt->halt; c++) {
		rt_step(rt);
		/* if (c % 10000 == 0) { */
		/* 	system("clear"); */
		/* 	grid_print(rt->grid); */
		/* } */
	}
	/* stack_print(&rt->stack); */
}
