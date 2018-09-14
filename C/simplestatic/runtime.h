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
void rt_step(tRuntime *);
void rt_exec(tRuntime *);
