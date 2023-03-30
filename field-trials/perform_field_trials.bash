#!/usr/bin/bash

i="ros_license_toolkit"
type -P $i &>/dev/null  && echo "$i installed"  || { echo "$i command not found."; exit 1; }

workdir="$(pwd)"
echo "Working directory is $workdir"

if [[ "$workdir" != *field-trials ]]; then
    echo "Please run this script from the field-trials directory"
    exit 1
fi

tmpdir=$(mktemp -d)
echo "Temporary directory is $tmpdir"

for n in $(cat _repos.list); do
    echo "Working on $n repository now"
    cd $tmpdir
    git clone $n
    name_w_ext=$(basename $n)
    name="${name_w_ext%.*}"
    cd $name
    echo "Running license linter on $name"
    ros_license_toolkit . > $workdir/$name.log
done

rm -rf $tmpdir
