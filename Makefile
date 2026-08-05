CC := gcc
CFLAGS := -std=c17 -Wall -Wextra -Werror -pedantic
TARGET := build/lab00
SOURCE := src/main.c

.PHONY: all grade clean

all: $(TARGET)

$(TARGET): $(SOURCE)
	mkdir -p build
	$(CC) $(CFLAGS) $(SOURCE) -o $(TARGET)

grade:
	python3 tests/grade.py

clean:
	rm -rf build
