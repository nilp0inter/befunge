#pragma once
#define ROW_SIZE 80
#define COL_SIZE 25

typedef char tGrid[COL_SIZE][ROW_SIZE];

void grid_init(tGrid);
void grid_print(tGrid);
void grid_put(tGrid, char, unsigned long int, unsigned long int);
void grid_load(FILE *, tGrid);
