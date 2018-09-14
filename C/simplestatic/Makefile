
CFLAGS=-Wall -O3 -g -std=gnu99
OBJS=befunge.o grid.o stack.o runtime.o

ALL: $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o befunge

clean:
	rm -f befunge $(OBJS)
