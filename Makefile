SHELL := /bin/bash

all:
	@echo "Please run 'make list' to see available targets."

.PHONY: pull build restart update

pull:
	git pull

build: | pull
	pushd image && docker compose build

restart: | build
	pushd image && docker compose down && docker compose up -d

update: pull build restart
	@echo "Contact form updated"

list:
	@grep '^[^#[:space:]]*:' Makefile | grep -v -e list -e all -e '\.' | sed -e 's/:.*//g' | sort
