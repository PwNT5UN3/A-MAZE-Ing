#!/bin/bash

for i in {1..10000}
do
  python3 a_maze_ing.py | grep -n File
done

