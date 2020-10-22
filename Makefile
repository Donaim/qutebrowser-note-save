
TARGET=
DIRNAME=$(shell dirname $(TARGET))

install:
	@ echo "TARGET: $(TARGET)"
	@ echo "DIRNAME: $(DIRNAME)"
	ln -sf "$(PWD)/note_save.py" "$(DIRNAME)/note_save.py"
	echo "\nimport note_save" >> $(TARGET)
