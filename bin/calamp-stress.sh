#!/bin/bash

for i in $(seq 1 1000);
do
    echo $i
    source bin/calamp_test_client --host localhost --port 20500 data/id_report.dat
done
