CFLAGS=-g
LDFLAGS=-g

%.ll: %.bf
	pipenv run python compiler.py $< | tee $@
	# pipenv run python compiler.py $< > $@

%.s: %.ll
	llc -march=x86-64 -o $@ $<
