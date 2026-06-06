#!/bin/bash
TS=$(date -r "$(git log -1 --format='%ct' -- AWS_AIF_C01_Learning_Tool.html)" "+%-m/%-d/%Y, %-I:%M:%S %p")
sed -i '' "s|Updated: .*'|Updated: $TS'|" AWS_AIF_C01_Learning_Tool.html
