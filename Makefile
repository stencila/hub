all: setup run

setup:
	make -C director setup

run:
	make -C director run

lint:
	make -C director lint

test:
	make -C director test

cover:
	make -C director cover

build:
	make -C director build
	make -C router build
