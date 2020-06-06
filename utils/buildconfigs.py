#!/usr/bin/env python3

import os
from pathlib import Path
import re
import itertools

basedir = os.path.abspath(os.path.join(os.getcwd(), "configs"))
fragdir = os.path.join(basedir, "fragments")
raw = {}

for p in Path(fragdir).rglob('*.config'):
    with open(p, 'r') as f:
        raw[os.path.relpath(p, fragdir)] = f.readlines()


def scandir(dp):
    dirs = []
    subs = [f.path for f in os.scandir(
        dp) if f.is_dir() and os.path.basename(f) != "common"]
    if len(subs) == 0:
        dirs.append(dp)
    for d in subs:
        dirs += scandir(d)
    return(dirs)


targets = []
targetmatch = "(?P<vendor>[^/]+)/(?P<product>[^/]+)(/(?P<version>[^/]+))?"
for t in [os.path.relpath(p, fragdir) for p in scandir(fragdir)]:
    match = re.search(targetmatch, t)
    target = {}
    target.update([(k, v)
                   for k, v in match.groupdict().items() if v is not None])
    target["configname"] = target["vendor"] + "_" + target["product"] + \
        (target["version"] if "version" in target else "") + "_defconfig"
    target["config"] = []
    targets.append(target)

for t in targets:
    print("Building " + t["configname"])
    matches = []
    # common matches
    # vendor match
    matches.append("^common/[^/]+(/([^/]+_)*"
                   + t["vendor"] + "(_[^/]+)*)?\.config")
    # product match
    matches.append("^" + t["vendor"] + "/common/[^/]+(/([^/]+_)*"
                   + t["product"] + "(_[^/]+)*)?\.config")
    # version match
    if "version" in t:
        matches.append("^" + t["vendor"] + "/" + t["product"] + "/common/[^/]+(/([^/]+_)*"
                       + t["version"] + "(_[^/]+)*)?\.config")
    # specific match
    matches.append("^" + t["vendor"] + "/" + t["product"]
                   + (("/" + t["version"])if "version" in t else "") + "/[^/]+.config")
    t["config"] = list(itertools.chain.from_iterable(
        [raw[fn] for fn in filter(re.compile("|".join(matches)).match, raw.keys())]))
    confpath = os.path.join(basedir, t["configname"])
    with open(confpath, 'w') as f:
        for l in t["config"]:
            f.write(l)
    os.system("cd buildroot; BR2_EXTERNAL=.. make " + t["configname"])
    os.system("cd buildroot; make savedefconfig")
    with open(confpath, 'r') as f:
        reslines = f.readlines()
    for l in [l.strip() for l in set(t["config"]).difference(set(reslines))]:
        if l == "":
            continue
        print("Line was lost somewhere during build:", l)
