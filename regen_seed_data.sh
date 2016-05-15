#!/usr/bin/bash

# drop db
dropdb readcoachdb

#recreate db
createdb readcoachdb

#execute test script
python seed.py
