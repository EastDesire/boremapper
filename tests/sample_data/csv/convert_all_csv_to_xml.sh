#!/bin/bash

ls ./*.csv | while read fn; do
  echo "Processing $fn"
  fn_xml=$(echo "$fn" | sed 's/\(\.[^.]*\)$/.xml/')
  ./csv_to_xml.py "$fn" > "$fn_xml"
done