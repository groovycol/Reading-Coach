#!/usr/bin/bash

# drop test db
dropdb testdb

#recreate test db
createdb testdb

#execute test script
python tests.py
