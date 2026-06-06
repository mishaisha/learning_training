#!/bin/bash
TS=$(date "+%-m/%-d/%Y, %-I:%M:%S %p")
sed -i '' "s|Updated: .*'|Updated: $TS'|" AWS_AIF_C01_Learning_Tool.html
