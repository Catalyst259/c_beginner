# Lab 7 build rules
CC := gcc
CFLAGS := -std=c17 -Wall -Wextra -Werror -pedantic -Iinclude \
	-fsanitize=address,undefined -fno-omit-frame-pointer
TARGET := build/lab07
SOURCES := src/main.c src/lab07.c

.PHONY: all grade clean

all: $(TARGET)

$(TARGET): $(SOURCES) include/lab07.h
	mkdir -p build
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

grade:
	python3 tests/grade.py

clean:
	rm -rf build
