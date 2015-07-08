#!/usr/bin/env bash

## Print header
echo -e "Size\tResid.\tShared\tData\t%"

pageSize=$(getconf PAGE_SIZE)
max=0

while [ 1 ]; do
    ## Get the PID of the process name given as argument 1
    pidno=`pgrep $1`

    ## If the process is running, print the memory usage
    if [ -e /proc/$pidno/statm ]; then
        ## Get the memory info
        vals=`cat /proc/$pidno/statm`

        ## Count totalMemory usage
        totalVM=`echo $vals $pageSize | awk '{print $1*$8}'`

        if [[ $totalVM -gt $max ]]; then
            max=$totalVM
        fi
    ## If the process is not running
    else
        echo -e "$max"
        exit
    fi
done
