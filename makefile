# Makefile

# Compiler
CC = cc

# Compiler flags
CFLAGS = -fPIC -shared -O3

# Target shared library
TARGET = my_functions.so

# Source file
SRC = my_functions.c

# Default rule
all: $(TARGET)

# Rule to create the shared library
$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

# Clean rule to remove the shared library
clean:
	rm -f $(TARGET)
