#!/bin/bash


count=141407
echo "till count"
i=1
echo "till i"
for ((i = 1; i < count+1; i++)); do
     echo "till loop"
     rm output$i.log
done
