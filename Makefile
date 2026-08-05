# Lab 6 build rules
CC := gcc
CFLAGS := -std=c17 -Wall -Wextra -Werror -pedantic -Iinclude \
	-fsanitize=address,undefined -fno-omit-frame-pointer
TARGET := build/lab06
SOURCES := src/main.c src/lab06.c

.PHONY: all grade clean

all: $(TARGET)

$(TARGET): $(SOURCES) include/lab06.h
	mkdir -p build
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

grade:
	python3 tests/grade.py

clean:
	rm -rf build
