.PHONY: clean setup test

clean:
	find . -name '*venv*' | xargs rm -rf
	rm -rf "htmlcov" ".cache" ".coverage"

setup:
	script/setup

test:
	script/test
