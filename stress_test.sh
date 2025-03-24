#!/bin/bash

# Replace this with the internal IP of your logging VM
SERVER_VM_IP="10.3.0.3"

echo "Starting stress test and network activity test..."

# CPU Stress Test (100% load on 4 cores for 60 seconds)
stress-ng --cpu 4 --cpu-load 100 --timeout 60s &

# Memory Stress Test (Allocate and access 1GB memory for 60 seconds)
stress-ng --vm 2 --vm-bytes 1G --timeout 60s &

# Disk I/O Stress Test (Perform heavy disk writes)
stress-ng --hdd 1 --hdd-bytes 1G

# Network Activity Test (Generate 100 Mbps traffic)
iperf3 -c $SERVER_VM_IP -t

# I/O Stress Test (High file open/close activity)
stress-ng --io 4

echo "All stress tests started."

