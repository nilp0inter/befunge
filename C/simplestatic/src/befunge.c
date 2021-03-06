#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "grid.h"
#include "runtime.h"

int main(int argc, char **argv)
{
	if (argc != 2) {
		printf("%s <filename>\n", argv[0]);
		exit(1);
	}

	tRuntime rt;
	rt_init(&rt);

	if (rt_fload(&rt, argv[1]) != 0) {
		fprintf(stderr, "Cannot load file.\n");
		exit(1);
	}

	rt_exec(&rt);
}
