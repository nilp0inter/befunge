#pragma once
#include <stdbool.h>

#include "grid.h"
#include "stack.h"

typedef enum { UP, RIGHT, DOWN, LEFT } tDirection;

typedef struct {
	unsigned short int width, height, y, x;
	tDirection direction;
	_Bool stringmode;
	tGrid grid;
	tStack stack;
} tRuntime;

void rt_init(tRuntime *);
int rt_fload(tRuntime *, char const *);
char rt_get_cell(tRuntime *);
char rt_get_cell_at(tRuntime *, unsigned short int, unsigned short int);
void rt_next(tRuntime *);
void rt_step(tRuntime *);
void rt_exec(tRuntime *);
/* vim: set ts=8 sw=4 tw=79 noet :*/
