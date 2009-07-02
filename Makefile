CFLAGS := -g2 -O2 -fPIC -fno-common

all: libbin1.dylib libbin2.dylib libbin4.dylib
#all: libbin1.dylib libbin2.dylib

#	gcc -fPIC -shared -o libbin1.so bin1.o

libbin1.dylib: bin1.o
	gcc -dynamiclib -undefined dynamic_lookup -single_module -o libbin1.dylib bin1.o

bin1.o: bin1.c

bin1.c: compile.py
	python compile.py bin1

libbin2.dylib: bin2.o
	gcc -dynamiclib -undefined dynamic_lookup -single_module -o libbin2.dylib bin2.o

bin2.o: bin2.c

bin2.c: compile.py
	python compile.py bin2

clean:
	rm -f *.o *.so


libbin4.dylib: bin4.o
	gcc -dynamiclib -undefined dynamic_lookup -single_module -o libbin4.dylib bin4.o

bin4.o: bin4.c

bin4.c: compile.py
	python compile.py bin4

