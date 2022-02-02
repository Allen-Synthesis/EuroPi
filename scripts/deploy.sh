#!/bin/sh
set -e

rshell cp ${1} /pyboard/main.py
rshell 'repl ~ import machine ~ machine.soft_reset()~'
