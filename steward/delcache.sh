#!/bin/sh

# Based on https://raw.githubusercontent.com/s3fs-fuse/s3fs-fuse/master/test/sample_delcache.sh
# with some modifications

# s3fs - FUSE-based file system backed by Amazon S3
#
# Copyright 2007-2008 Randy Rizun <rrizun@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


func_usage()
{
    echo ""
    echo "Usage:  $1 <bucket name> <cache path> <limit size> [--silent|--verbose]"
    echo "        $1 -h"
    echo "Sample: $1 mybucket /tmp/s3fs/cache 1073741824"
    echo ""
    echo "  bucket name = bucket name which specified s3fs option"
    echo "  cache path  = cache directory path which specified by"
    echo "                use_cache s3fs option."
    echo "  limit size  = limit for total cache files size."
    echo "                specify by BYTE"
    echo "  --silent    = silent mode"
    echo "  --verbose   = verbose mode"
    echo ""
}

PRGNAME=`basename $0`

if [ "X$1" = "X-h" -o "X$1" = "X-H" ]; then
    func_usage $PRGNAME
    exit 0
fi
if [ "X$1" = "X" -o "X$2" = "X" -o "X$3" = "X" ]; then
    func_usage $PRGNAME
    exit 1
fi

BUCKET=$1
CDIR="$2"
LIMIT=$3
SILENT=0
if [ "X$4" = "X--silent" ]; then
    SILENT=1
fi
VERBOSE=0
if [ "X$4" = "X--verbose" ]; then
    VERBOSE=1
fi

FILES_CDIR="${CDIR}/${BUCKET}"
STATS_CDIR="${CDIR}/.${BUCKET}.stat"

#
# Check cache exists
#
if [ ! -d $FILES_CDIR ]; then
    if [ $VERBOSE -eq 1 ]; then
        echo "Cache directory does not yet exist"
    fi
    exit 0
fi

#
# Check total size
#
CURRENT_CACHE_SIZE=`du -sb "$FILES_CDIR" | awk '{print $1}'`
if [ $LIMIT -ge $CURRENT_CACHE_SIZE ]; then
    if [ $VERBOSE -eq 1 ]; then
        echo "Cache directory is below limit: $CURRENT_CACHE_SIZE bytes"
    fi
    exit 0
fi

#
# Remove loop
#
TMP_ATIME=0
TMP_STATS=""
TMP_CFILE=""
#
# Make file list by sorted access time
#
find "$STATS_CDIR" -type f -exec stat -c "%X:%n" "{}" \; | sort | while read part
do
    TMP_ATIME=`echo "$part" | cut -d: -f1`
    TMP_STATS="`echo "$part" | cut -d: -f2`"
    TMP_CFILE=`echo "$TMP_STATS" | sed s/\.$BUCKET\.stat/$BUCKET/`

    if [ `stat -c %X "$TMP_STATS"` -eq $TMP_ATIME ]; then
        rm -f "$TMP_STATS" "$TMP_CFILE" > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            if [ $SILENT -ne 1 ]; then
                echo "ERROR: Could not remove files $TMP_CFILE $TMP_STATS"
            fi
            exit 1
        else
            if [ $SILENT -ne 1 ]; then
                echo "Removed file $TMP_CFILE"
            fi
        fi
    fi
    if [ $LIMIT -ge `du -sb "$FILES_CDIR" | awk '{print $1}'` ]; then
        if [ $SILENT -ne 1 ]; then
            echo "Finished removing files"
        fi
        break
    fi
done

if [ $VERBOSE -eq 1 ]; then
    TOTAL_SIZE=`du -sb "$FILES_CDIR" | awk '{print $1}'`
    echo "Done. $FILES_CDIR total size is $TOTAL_SIZE"
fi

exit 0
