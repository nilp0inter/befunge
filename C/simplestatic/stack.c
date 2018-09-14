#include <stdio.h>

#include "stack.h"

void stack_init(tStack * st)
{
	st->top = 0;
}

void stack_print(tStack * st)
{
	fprintf(stderr, "(%d) [", st->top);
	for (int i = 0; i < st->top; i++)
		fprintf(stderr, "%li ", st->content[i]);
	fprintf(stderr, "]\n");
}
