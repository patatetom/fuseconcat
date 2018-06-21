#!/usr/bin/python
"""
usage: fuseconcat.py [-h] [--debug] file [file ...] folder

attach (mount) concatenated files at folder

positional arguments:
  file        file(s) to be concatenated
  folder      folder where to attach «concatenated» files

optional arguments:
  -h, --help  show this help message and exit
  --debug     debug mode on foreground

«concatenated» file is read-only
"""


from os import getgid, getuid
from time import localtime, mktime
import errno


from fuse import FUSE, FuseOSError, Operations


class Concatenate(Operations):
    def __init__(self, files):
        file_offset = 0
        self.files = []
        # build list of files with global min and max offset
        for file in files:
            with open(file, 'rb') as self.handle:
                file_size = self.handle.seek(0, 2)
                self.files.append((file, (file_offset, (file_offset + file_size))))
                file_offset += file_size
        self.file = None
        self.handle = None
        # file size is last file offset
        self.size = file_offset
        self.ctime = mktime(localtime())
        self.uid = getuid()
        self.gid = getgid()
#        if args.debug:
#            print('\033[93m' + '● files: {}\n● size: {}'.format(self.files, self.size) + '\033[0m')


    def getattr(self, path, fh=None):
        if path == '/':
            # return folder stats
            return {
                'st_mode': 0o40555,
                'st_nlink': 2,
                'st_gid': self.gid,
                'st_uid': self.uid,
                'st_size': 0x1000,
                'st_ctime': self.ctime,
                'st_mtime': self.ctime,
                'st_atime': self.ctime,
                }
        if path != '/concatenated':
            # there is only one file in folder
            raise FuseOSError(errno.ENOENT)
        # return «concatenated» file stats
        return {
            'st_mode': 0o100444,
            'st_nlink': 1,
            'st_gid': self.gid,
            'st_uid': self.uid,
            'st_size': self.size,
            'st_ctime': self.ctime,
            'st_mtime': self.ctime,
            'st_atime': self.ctime,
            }


    def readdir(self, path, fh):
        # there is only one file in folder : the «concatenated» file
        return ('.', '..', 'concatenated')


    def __get_file(self, global_offset):
        # open the "good" file and return the local offset
        if global_offset > self.size:
            raise FuseOSError(errno.EFAULT)
        for file, (min_offset, max_offset) in self.files:
            if min_offset <= global_offset < max_offset:
                if file != self.file:
                    if self.handle:
                        self.handle.close()
#                    if args.debug:
#                        print('\033[93m' + '● opening file: {}'.format(file) + '\033[0m')
                    self.handle = open(file, 'rb')
                    self.file = file
                return global_offset - min_offset
        # return None if global offset is file size
        return None


    def read(self, path, size, offset, fh):
        data = b''
        while size:
            local_offset = self.__get_file(offset)
            if local_offset is None:
                break
#            if args.debug:
#                print('\033[93m' + '● read {} bytes at local offset {} in {})'.format(size, local_offset, self.file) + '\033[0m')
            self.handle.seek(local_offset)
            handled = self.handle.read(size)
            data += handled
            read = len(handled)
            offset += read
            size -= read
#            if read < size and args.debug:
#                print('\033[93m' + '● read only {} bytes'.format(read) + '\033[0m')
        return data


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.description = "attach (mount) concatenated files at folder"
    parser.add_argument("files", nargs='+', metavar='file', help='file(s) to be concatenated')
    parser.add_argument("folder", help='folder where to attach «concatenated» files')
    parser.add_argument("--debug", help='debug mode on foreground', action='store_true')
    parser.epilog = '«concatenated» file is read-only'
    args = parser.parse_args()
    concatenated = Concatenate(args.files)
    FUSE(concatenated, args.folder, ro=True, foreground=args.debug, allow_other=True, nothreads=True, debug=args.debug)

