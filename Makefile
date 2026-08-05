# Lab 8 build rules
CC := gcc
CFLAGS := -D_POSIX_C_SOURCE=200809L -std=c17 -Wall -Wextra -Werror \
	-pedantic -Iinclude -fsanitize=address,undefined \
	-fno-omit-frame-pointer
TARGET := build/lab08
SOURCES := src/main.c src/lab08.c

.PHONY: all grade clean

all: $(TARGET)

$(TARGET): $(SOURCES) include/lab08.h
	mkdir -p build
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

grade:
	python3 tests/grade.py

clean:
	rm -rf build
