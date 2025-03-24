#!/bin/bash
# send_data.sh - Script to collect and send system metrics

# Create directory and pipe if they don't exist
mkdir -p ~/stress-testing
[ -p ~/stress-testing/stress_pipe ] || mkfifo ~/stress-testing/stress_pipe

exec 3<>$PIPE

while true; do
    # Collect system stats
    cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
    mem=$(free -m | awk '/Mem:/ {print $3/$2 * 100}')
    disk=$(df -h / | awk '/\// {print $5}' | tr -d '%')
    network=$(sar -n DEV 1 1 | grep "Average.*eth0" | awk '{print $5+$6}' || echo "0")
    io=$(iostat -d -x 1 1 | awk '/^[0-9]/ {print $10}' | head -1 || echo "0")
    
    # Format as JSON
    json="{\"CPU Usage\":$cpu,\"Memory Usage\":$mem,\"Disk Usage\":$disk,\"Network Activity\":$network,\"I/O Activity\":$io}"
    
    # Send to named pipe
    echo "$json" > ~/stress-testing/stress_pipe > /dev/null
    
    # Sleep for a bit
    sleep 3
done

