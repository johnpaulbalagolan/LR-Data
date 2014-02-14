#! /bin/sh

usage="usage: $(basename "$0") [-w worker_count] [-h] -- start celeryd workers\n
\n
Options:\n
    -h show this help text\n
    -w number of workers to start\n"

WORKERS=3


while getopts ":w:h" opt; do
    case $opt in
        w)
            WORKERS="$OPTARG"
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            echo -e $usage >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument" >&2
            echo -e $usage >&2
            exit 1;;
        h)
            echo -e $usage;
            exit
    esac
done

# Create a file to record number of workers we are starting (for stop script)
echo $WORKERS > .celery_workers

celeryd-multi start $WORKERS -l INFO -Q:1 harvest,image -Q:2 validate,parse -Q save
