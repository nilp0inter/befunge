#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "grid.h"


void grid_init(tGrid grid)
{
	for (int y = 0; y < COL_SIZE; y++)
		for (int x = 0; x < ROW_SIZE; x++)
			grid[y][x] = ' ';
}


void grid_put(tGrid grid, char v, unsigned long int x, unsigned long int y)
{
    grid[y][x] = v;
}


void grid_print(tGrid grid)
{
	for (int y = 0; y < COL_SIZE; y++) {
		for (int x = 0; x < ROW_SIZE; x++) {
			fprintf(stderr, "%c", grid[y][x]);
		}
		fprintf(stderr, "\n");
	}
}


void grid_load(FILE *fp, tGrid grid)
{
    char * line = malloc(COL_SIZE + 2); // \n\0
    size_t len = 0;
    ssize_t read;

    for (int y=0; y < COL_SIZE; y++) {
	len = COL_SIZE;
	read = getline(&line, &len, fp);
	if (read != -1) {
	    if (line[read-1] == '\n') --read;
	    memcpy(grid[y], line, read < ROW_SIZE ? read : ROW_SIZE);
	} else {
	    break;
	}
    }
    free(line);
}
