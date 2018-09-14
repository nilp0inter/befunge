#pragma once
#define STACK_SIZE 128

typedef struct {
	signed long int content[STACK_SIZE];
	int top;
} tStack;

void stack_init(tStack *);

inline signed long int stack_pop(tStack * st)
{
	if (st->top == 0) {
		return 0;
	} else {
		return st->content[--st->top];
	}
}

inline void stack_push(tStack * st, signed long int value)
{
	if (st->top < sizeof(st->content)) {
		st->content[st->top++] = value;
	}
}

inline signed long int stack_peek(tStack * st)
{
	if (st->top == 0) {
		return 0;
	} else {
		return st->content[st->top - 1];
	}
}

void stack_print(tStack *);
