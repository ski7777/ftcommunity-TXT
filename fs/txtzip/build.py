#!/usr/bin/env python3

import sys
import os

confpath = sys.argv[1]
fsdir = sys.argv[2]
name = sys.argv[3]
extension = sys.argv[4]
imagedir = sys.argv[5]

workdir = os.path.join(fsdir, name)
zippath = os.path.join(imagedir, name + "." + extension)
outdir = os.path.join(imagedir, name)


print("Cleaning up")
os.system("rm -rf " + workdir + "; mkdir " + workdir)
os.system("rm -rf " + zippath + " " + outdir)

print("Copying files")
conffile = open(confpath, 'r')
for l in conffile.readlines():
    l = l.strip()
    if "->" in l:
        sp = l.split("->")
        s = sp[0]
        t = sp[1]
        s = os.path.expandvars(s)
        f = os.path.basename(s)
        t = os.path.join(workdir, t)

    else:
        s = l
        s = os.path.expandvars(s)
        f = os.path.basename(s)
        t = os.path.join(workdir, f)
    td = os.path.dirname(t)
    os.system("mkdir -p " + td)
    os.system("cp -r " + s + " " + t)

print("Copying output directory")
os.system("cp -r " + workdir + " " + outdir)

print("zipping files")
os.system("cd " + workdir + "; zip -r " + zippath + " *")
