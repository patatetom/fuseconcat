# fuseconcat

concatenate multiple files into a single logical file

```sh
$ dd if=/dev/urandom bs=1M count=16 > /tmp/test.file
16+0 records in
16+0 records out
16777216 bytes (17 MB, 16 MiB) copied, 0.0844514 s, 199 MB/s

$ split -db 3M /tmp/test.file /tmp/test.files.

$ ls -lgG /tmp/test.file*
-rw-r--r-- 1 16777216 Jun 21 11:14 /tmp/test.file
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.00
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.01
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.02
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.03
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.04
-rw-r--r-- 1  1048576 Jun 21 11:14 /tmp/test.files.05

$ python fuseconcat.py
usage: fuseconcat.py [-h] [--debug] file [file ...] folder
fuseconcat.py: error: the following arguments are required: file, folder

$ mkdir /tmp/test

$ python fuseconcat.py /tmp/test.files.* /tmp/test/

$ mount | grep /tmp/test
Concatenate on /tmp/test type fuse (ro,nosuid,nodev,relatime,user_id=1000,group_id=1000,allow_other)

$ ls -lgG /tmp/test*
-rw-r--r-- 1 16777216 Jun 21 11:14 /tmp/test.file
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.00
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.01
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.02
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.03
-rw-r--r-- 1  3145728 Jun 21 11:14 /tmp/test.files.04
-rw-r--r-- 1  1048576 Jun 21 11:14 /tmp/test.files.05
/tmp/test:
total 0
-r--r--r-- 1 16777216 Jun 21 11:16 concatenated

$ md5sum /tmp/test.file /tmp/test/concatenated 
68d5d2de47a7f3ac2092dd1d5802ad54  /tmp/test.file
68d5d2de47a7f3ac2092dd1d5802ad54  /tmp/test/concatenated

$ md5sum /tmp/test.files.00 <( dd if=/tmp/test/concatenated count=6144 status=none )
f6adc84c52215ef1a07cbcae64a9ab21  /tmp/test.files.00
f6adc84c52215ef1a07cbcae64a9ab21  /dev/fd/63

$ md5sum /tmp/test.files.01 <( dd if=/tmp/test/concatenated skip=6144 count=6144 status=none )
b024551324dc1d995c1fde859084f747  /tmp/test.files.01
b024551324dc1d995c1fde859084f747  /dev/fd/63

$ md5sum /tmp/test.files.05 <( dd if=/tmp/test/concatenated skip=$((6144*5)) status=none )
88ea81a5bb02941036769a1935b387ae  /tmp/test.files.05
88ea81a5bb02941036769a1935b387ae  /dev/fd/63

$ fusermount -u /tmp/test
```

```sh
$ echo test > /tmp/test.file

$ python fuseconcat.py /tmp/test.file /tmp/test.file /tmp/test.file /tmp/test.file /tmp/test/

$ cat /tmp/test/concatenated 
test
test
test
test

$ fusermount -u /tmp/test
```
