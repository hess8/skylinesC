#! /usr/bin/env bash
# Allows signal handler to stop processes.  System ignores trapped signals
trap '' SIGTERM SIGTSTP SIGINT SIGQUIT SIGHUP  # ignore signals
echo "$@"
exec "$@"
