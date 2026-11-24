#!/usr/bin/env bash
# efbig.sh: show the error a process gets when it writes past a 1 KiB file-size limit.
ulimit -f 1
python3 -c "
with open('data/efbig-test.bin', 'wb') as f:
    f.write(b'x' * 4096)
" 2>&1 | tail -n 1
rm -f data/efbig-test.bin
