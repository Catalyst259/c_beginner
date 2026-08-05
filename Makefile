# Lab 3 build rules
CC := gcc
CFLAGS := -std=c17 -Wall -Wextra -Werror -pedantic -Iinclude
TARGET := build/lab03
SOURCES := src/main.c src/lab03.c

.PHONY: all grade clean

all: $(TARGET)

$(TARGET): $(SOURCES) include/lab03.h
	mkdir -p build
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

grade:
	python3 tests/grade.py

clean:
	rm -rf build
