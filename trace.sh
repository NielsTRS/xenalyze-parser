#!/bin/bash

# Start Phoronix in background on Dom1
sshpass -p "vm" ssh vm@10.132.0.2 "timeout 75 phoronix-test-suite batch-run compress-gzip" &

# Sleep before tracing
sleep 50

# Start xentrace for 10 seconds
sudo timeout 10 xentrace -D > traces/trace.bin &
XENTRACE_PID=$!

# Wait for xentrace to finish
wait $XENTRACE_PID

echo ">>> xentrace finished"
