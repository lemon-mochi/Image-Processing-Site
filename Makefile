# makefile
# used to easily compile the C shared library
my_functions.o: my_functions.c 
	cc -fPIC -shared my_functions.c -O3 my_functions.so

clean:
	rm my_functions.so