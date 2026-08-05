# Lab 2 build rules
CC := gcc
CFLAGS := -std=c17 -Wall -Wextra -Werror -pedantic -Iinclude
TARGET := build/lab02
SOURCES := src/main.c src/lab02.c

.PHONY: all grade clean

all: $(TARGET)

$(TARGET): $(SOURCES) include/lab02.h
	mkdir -p build
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

grade:
	python3 tests/grade.py

clean:
	rm -rf build
