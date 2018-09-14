#include <stdio.h>

#include "stack.h"


void stack_init(tStack *st) 
{
	st->top = 0;
}


signed long int stack_pop(tStack *st)
{
	if (st->top == 0) {
		return 0;
	} else {
		return st->content[--st->top];
	}
}


void stack_push(tStack *st, signed long int value)
{
	if (st->top < sizeof(st->content)) {
		st->content[st->top++] = value;
	}
}


signed long int stack_peek(tStack *st)
{
	if (st->top == 0) {
		return 0;
	} else {
		return st->content[st->top - 1];
	}
}


void stack_print(tStack *st)
{
    fprintf(stderr, "(%d) [", st->top);
    for(int i=0; i < st->top; i++) fprintf(stderr, "%li ", st->content[i]);
    fprintf(stderr, "]\n");
}
