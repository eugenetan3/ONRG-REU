#!/bin/sh

db_info=$1
tokens=$2
ids=$3
cmds=$4

java -classpath "gson-2.8.6.jar:twitter4j-core-3.0.5.jar:mysql-connector-java-5.1.16-bin.jar:." Collect $1 $2 $3 $4
