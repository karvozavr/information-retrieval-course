#!/bin/bash

cd $1
for file in $(ls); do cat $file | wc -w; done

