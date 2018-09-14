#pragma once
#define STACK_SIZE 128

typedef struct {
	signed long int content[STACK_SIZE];
	int top;
} tStack;

void stack_init(tStack *);
signed long int stack_pop(tStack *);
void stack_push(tStack *, signed long int);
signed long int stack_peek(tStack *);
void stack_print(tStack *);
/* vim: set ts=8 sw=4 tw=79 noet :*/
