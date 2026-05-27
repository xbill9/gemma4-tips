# Root Makefile for managing all subdirectories

# List of subdirectories containing a Makefile
SUBDIRS := gpu-vllm-devops-agent \
           local-devops-agent \
           tpu-vllm-devops-agent

.PHONY: all clean test lint install $(SUBDIRS)

# Default target displays help information
all:
	@echo "========================================================="
	@echo " Gemma-4 DevOps Agents - Root Makefile"
	@echo "========================================================="
	@echo "Available commands:"
	@echo "  make clean   - Run 'make clean' in all subdirectories"
	@echo "  make test    - Run 'make test' in all subdirectories"
	@echo "  make lint    - Run 'make lint' in all subdirectories"
	@echo "  make install - Run 'make install' in all subdirectories"
	@echo "========================================================="

# Target-specific variable assignments
clean: TARGET := clean
clean: $(SUBDIRS)

test: TARGET := test
test: $(SUBDIRS)

lint: TARGET := lint
lint: $(SUBDIRS)

install: TARGET := install
install: $(SUBDIRS)

# Run the specified target in each subdirectory if a Makefile exists
$(SUBDIRS):
	@if [ -f $@/Makefile ]; then \
		if [ -z "$(TARGET)" ]; then \
			echo "⚙️ Executing default target in $@..."; \
			$(MAKE) -C $@; \
		else \
			echo "⚙️ Executing 'make $(TARGET)' in $@..."; \
			$(MAKE) -C $@ $(TARGET); \
		fi \
	fi
