#!/bin/bash
 
find /tmp/videofetcher/* -mtime +7 -exec rm -f {} \;
