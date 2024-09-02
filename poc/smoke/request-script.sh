#!/bin/bash
plat=$platform
APPA="application-${plat}"
APPB="locations-${plat}"
APPC="candidates-${plat}"
APPD="${APPA}"
while true;
do
TIMES=1
p1=$((5 + $RANDOM % 15))
p2=$((5 + $RANDOM % 15))
p3=$((5 + $RANDOM % 15))
p4=$((5 + $RANDOM % 15))
p5=$((5 + $RANDOM % 15))
p6=$((5 + $RANDOM % 15))
p7=$((5 + $RANDOM % 15))

for i in $(eval echo "{1..2}")
do
    siege -c $p1 -r 1 http://$APPD:8000/
    siege -c $p3 -r 5 http://$APPD:8000/io_task
    siege -c $p2 -r 5 http://$APPD:8000/cpu_task
    siege -c $p5 -r 1 http://$APPD:8000/random_sleep
    siege -c $p4 -r 3 http://$APPD:8000/random_status
    siege -c $p6 -r 3 http://$APPD:8000/chain
    siege -c $p7 -r 1 http://$APPD:8000/error_test
    sleep 5
done

for i in $(eval echo "{1..3}")
do
    siege -c 3 -r 10 http://$APPD:8000/
    siege -c 3 -r 5 http://$APPD:8000/io_task
    siege -c 2 -r 5 http://$APPD:8000/cpu_task
    siege -c 5 -r 3 http://$APPD:8000/random_sleep
    siege -c 4 -r 10 http://$APPD:8000/random_status
    siege -c 6 -r 3 http://$APPD:8000/chain
    siege -c 7 -r 1 http://$APPD:8000/error_test
    sleep 25
done


for i in $(eval echo "{1..$TIMES}")
do
    siege -c 1 -r 10 http://$APPA:8000/
    siege -c 3 -r 5 http://$APPA:8000/io_task
    siege -c 2 -r 5 http://$APPA:8000/cpu_task
    siege -c 5 -r 3 http://$APPA:8000/random_sleep
    siege -c 2 -r 10 http://$APPA:8000/random_status
    siege -c 2 -r 3 http://$APPA:8000/chain
    siege -c 1 -r 1 http://$APPA:8000/error_test
    sleep 100
done

for i in $(eval echo "{1..$TIMES}")
do
    siege -c 1 -r 10 http://$APPB:8000/
    siege -c 3 -r 5 http://$APPB:8000/io_task
    siege -c 2 -r 5 http://$APPB:8000/cpu_task
    siege -c 5 -r 3 http://$APPB:8000/random_sleep
    siege -c 2 -r 10 http://$APPB:8000/random_status
    siege -c 2 -r 3 http://$APPB:8000/chain
    siege -c 1 -r 1 http://$APPB:8000/error_test
    sleep 60 
done

for i in $(eval echo "{1..$TIMES}")
do
    siege -c 1 -r 10 http://$APPC:8000/
    siege -c 3 -r 5 http://$APPC:8000/io_task
    siege -c 2 -r 5 http://$APPC:8000/cpu_task
    siege -c 5 -r 3 http://$APPC:8000/random_sleep
    siege -c 2 -r 10 http://$APPC:8000/random_status
    siege -c 2 -r 3 http://$APPC:8000/chain
    siege -c 1 -r 1 http://$APPC:8000/error_test
    sleep 5
done
  sleep 200 
done
