# Usage

Every command on this page runs from the repository root. The sample log at `examples/access.log` holds 12 requests.

## Count every status code

Pass the path of an access log:

```console
$ python3 statuscount.py examples/access.log
200  6
404  3
500  2
301  1
```

Each line holds a status code and the number of requests that returned it, highest count first. Codes with the same count appear lowest code first.

## Count errors only

`--min-status` leaves out every code below the number you give it:

```console
$ python3 statuscount.py --min-status 400 examples/access.log
404  3
500  2
```

## Fix a "cannot read" error

When the file is missing or your user cannot open it, the tool prints one line and exits with status 2:

```console
$ python3 statuscount.py logs/missing.log
statuscount: cannot read logs/missing.log
```

Check the path with `ls -l`, then run the command again.

## Run it on a live log

The path and the count below are an illustration, because your server's traffic decides the numbers:

<!-- check_examples: skip -->
```console
$ python3 statuscount.py /var/log/nginx/access.log
200  48211
```

Back to the [start page](index.md).
