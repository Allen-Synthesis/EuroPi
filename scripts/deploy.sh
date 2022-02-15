#!/bin/sh
set -e

while getopts ":a" opt; do
    case $opt in
        a)
            attach=1
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            ;;
    esac
done

src=${1}
dest=${2:-'/pyboard/main.py'}

RESTART_COMMAND='repl ~ import machine ~ machine.soft_reset()'

if [[ $attach -ne 1 ]]; then
    RESTART_COMMAND="${RESTART_COMMAND}~"
fi

rshell cp ${src} ${dest}
rshell $RESTART_COMMAND
