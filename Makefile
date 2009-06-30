CFLAGS := -g2 -fPIC -fno-common

#	gcc -fPIC -shared -o libbin1.so bin1.o

libbin1.dylib: bin1.o
	gcc -dynamiclib -undefined dynamic_lookup -single_module -o libbin1.dylib bin1.o

bin1.o: bin1.c

bin1.c: compile.py
	python compile.py bin1

clean:
	rm -f *.o *.so
