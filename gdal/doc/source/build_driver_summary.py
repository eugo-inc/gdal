#!/usr/bin/env python

import glob
import os
import sys

dirname = sys.argv[1]
anchor = sys.argv[2]
outfile = sys.argv[3]

res = []

for filename in glob.glob(os.path.join(dirname, '*.rst')):
    if 'driver_summary' in filename:
        continue
    with open(filename, 'rt') as f:
        shortnames = []
        longname = None
        supports_create = False
        supports_createcopy = False
        supports_georeferencing = False
        supports_virtualio = False
        built_in_by_default = False
        build_dependencies = None
        link = None
        last_line = None
        for l in f.readlines():
            l = l.rstrip('\n')
            if not link:
                assert l.startswith('.. _') and l.endswith(':')
                link = l[len('.. _'):-1]
            elif l.startswith('.. shortname:: '):
                shortnames.append(l[len('.. shortname:: '):])
            elif longname is None and last_line != '' and l.startswith('=' * len(last_line)):
                longname = last_line
                pos = longname.find(' -- ')
                if pos > 0:
                    longname = longname[pos + len(' -- '):]
                pos = longname.find(' - ')
                if pos > 0 and not 'oapif' in link:
                    longname = longname[pos + len(' - '):]
                line_before_long_name = False
            elif l.startswith('.. supports_createcopy::'):
                supports_createcopy = True
            elif l.startswith('.. supports_create::'):
                supports_create = True
            elif l.startswith('.. supports_georeferencing::'):
                supports_georeferencing = True
            elif l.startswith('.. supports_virtualio::'):
                supports_virtualio = True
            elif l.startswith('.. built_in_by_default::'):
                built_in_by_default = True
            elif l.startswith('.. build_dependencies:: '):
                build_dependencies = l[len('.. build_dependencies:: '):]
            last_line = l
        for shortname in shortnames:
            res.append([link, shortname, longname, built_in_by_default, build_dependencies, supports_create, supports_createcopy, supports_georeferencing, supports_virtualio])

res = sorted(res, key=lambda row: row[0].lower())

with open(outfile, "wt") as f:
    f.write('.. %s:\n\n' % anchor)
    f.write('..\n')
    f.write('  This file is generated by build_driver_summary.py. DO NOT EDIT !!!\n')
    f.write('  Do not put in git !!!\n')
    f.write('..\n')
    f.write(".. list-table::\n")
    f.write("   :widths: 10 35 10 10 10 25\n")
    f.write("   :header-rows: 1\n")
    f.write("\n")
    f.write("   * - Short name\n")
    f.write("     - Long name\n")
    f.write("     - Creation\n")
    f.write("     - Copy\n")
    f.write("     - Geo-referencing\n")
    #f.write("     - Virtual I/O\n")
    f.write("     - Build requirements\n")
    for link, shortname, longname, built_in_by_default, build_dependencies, supports_create, supports_createcopy, supports_georeferencing, supports_virtualio in res:
        f.write("   * - :ref:`%s <%s>`\n" % (shortname, link))
        f.write("     - %s\n" % longname)
        f.write("     - %s\n" % ('**Yes**' if supports_create else 'No'))
        f.write("     - %s\n" % ('**Yes**' if supports_createcopy else 'No'))
        f.write("     - %s\n" % ('**Yes**' if supports_georeferencing else 'No'))
        #f.write("     - %s\n" % ('**Yes**' if supports_virtualio else 'No'))
        if built_in_by_default:
            f.write("     - %s\n" % 'Built-in by default')
        elif build_dependencies:
            f.write("     - %s\n" % build_dependencies)
        else:
            f.write("     - %s\n" % '???')
