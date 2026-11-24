# Troubleshooting SQLite from the command line

Applies to: The `sqlite3` command-line shell 3.45.1 and the `sqlite3` module in Python 3.12.3, on Ubuntu 24.04. No other version was tested.
Last reproduced: 2026-11-23

Every entry below was triggered and fixed on a scratch database made with this command:

```bash
sqlite3 shop.db "create table customers (id integer primary key, email text not null unique);
create table orders (id integer primary key, customer_id integer not null references customers(id), total_cents integer not null);
insert into customers (id, email) values (1, 'ada@example.com');
insert into orders (customer_id, total_cents) values (1, 4200);"
```

The first three Symptom blocks show the same failure three ways, because the text around the message depends on how the SQL reaches SQLite: as an argument to `sqlite3`, piped to `sqlite3`, or run from Python.

## `no such table`

Symptom:

```text
$ sqlite3 shops.db "select count(*) from orders;"
Error: in prepare, no such table: orders

$ echo "select count(*) from orders;" | sqlite3 shops.db
Parse error near line 1: no such table: orders

$ python3 -c "import sqlite3; sqlite3.connect('shops.db').execute('select count(*) from orders')"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
sqlite3.OperationalError: no such table: orders
```

### The path names a file that did not exist, so SQLite created an empty database

Why: `sqlite3` and Python's `sqlite3.connect()` create the database file when the path does not exist. A misspelled name (`shops.db` for `shop.db`) or a different working directory gives you a new database with no tables in it.

Check:

```bash
ls -l shops.db
```

Your cause if: The file is 0 bytes, as in `-rw-r--r-- 1 dev dev 0 Nov 23 19:18 shops.db`.

Fix:

```bash
rm shops.db
sqlite3 "file:shop.db?mode=rw" "select count(*) from orders;"
```

The first command deletes the empty file SQLite created. The second opens the real database with `mode=rw`, which opens an existing file and never creates one.

Verify:

```bash
sqlite3 "file:shop.db?mode=rw" "select count(*) from orders;"
sqlite3 "file:shops.db?mode=rw" "select count(*) from orders;"
```

Fixed when: The first command prints the row count, `1`. The second, with the misspelled name, now fails with `Error: unable to open database "file:shops.db?mode=rw": unable to open database file` and leaves no new file behind.

## `database is locked`

Symptom:

```text
$ sqlite3 shop.db "insert into orders (customer_id, total_cents) values (1, 1900);"
Error: stepping, database is locked (5)

$ echo "insert into orders (customer_id, total_cents) values (1, 1900);" | sqlite3 shop.db
Runtime error near line 1: database is locked (5)

$ python3 -c "import sqlite3; sqlite3.connect('shop.db', timeout=0).execute('insert into orders (customer_id, total_cents) values (1, 1900)')"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
sqlite3.OperationalError: database is locked
```

### Another connection is in the middle of a write, and yours does not wait

Why: SQLite allows one writer at a time. A new `sqlite3` shell connection has a busy timeout of 0 milliseconds (`pragma busy_timeout;` prints `0`), so a write that meets another connection's lock fails at once instead of waiting.

Check:

```bash
lsof -w shop.db
```

Your cause if: `lsof` lists a process other than your own that has `shop.db` open, as in `sqlite3 1114425  dev    3ur  REG    8,1    16384 568430 shop.db`.

Fix:

```bash
sqlite3 -cmd ".timeout 10000" shop.db "insert into orders (customer_id, total_cents) values (1, 1900);"
```

`.timeout 10000` makes the shell wait up to 10 seconds for the lock. In Python the same setting is the `timeout` argument of `sqlite3.connect()`, in seconds.

Verify:

```bash
sqlite3 shop.db "select id, customer_id, total_cents from orders;"
```

Fixed when: The insert returns with no output once the other write commits, which took 4.5 seconds in this run, and the list includes the new row `2|1|1900`.

### A connection began a transaction and never ended it

Why: A write lock lasts until the transaction that took it commits or rolls back. A session left open after `begin immediate;` blocks every other writer for as long as it runs, and a timeout helps only when that transaction ends before the timeout does.

Check:

```bash
sqlite3 -cmd ".timeout 3000" shop.db "insert into orders (customer_id, total_cents) values (1, 3100);"
lsof -w shop.db
ps -o pid,etime,args -p 1114581
```

Your cause if: The insert prints `Error: stepping, database is locked (5)` again after the 3-second wait, and `ps` shows that the process `lsof` listed will not finish soon. In this run it was `sqlite3 shop.db begin immediate; insert into orders (customer_id, total_cents) values (1, 7700); .shell sleep 300 commit;`, five seconds into a 300-second sleep.

Fix:

```bash
kill 1114581
```

Use the PID that `lsof` printed for you. If someone owns that session, ask them to type `commit;` or `rollback;` in it, because `kill` ends it with no commit and SQLite rolls its changes back. In this run the order for 7700 that the open transaction had inserted was gone afterwards.

Verify:

```bash
lsof -w shop.db
sqlite3 shop.db "insert into orders (customer_id, total_cents) values (1, 3100);"
```

Fixed when: `lsof` prints nothing, and the insert returns with no output.

## `attempt to write a readonly database`

Symptom:

```text
$ sqlite3 shop.db "insert into orders (customer_id, total_cents) values (1, 2500);"
Error: stepping, attempt to write a readonly database (8)

$ echo "insert into orders (customer_id, total_cents) values (1, 2500);" | sqlite3 shop.db
Runtime error near line 1: attempt to write a readonly database (8)

$ python3 -c "import sqlite3; sqlite3.connect('shop.db').execute('insert into orders (customer_id, total_cents) values (1, 2500)')"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
sqlite3.OperationalError: attempt to write a readonly database
```

### Your user cannot write to the database file

Why: SQLite can still read a file that your user has no permission to write, so `select count(*) from orders;` printed `3` on this file, and the first insert failed.

Check:

```bash
ls -l shop.db
```

Your cause if: The permissions show no `w` for your user, as in `-r--r--r-- 1 dev dev 16384 Nov 23 19:18 shop.db`.

Fix:

```bash
chmod u+w shop.db
```

Verify:

```bash
sqlite3 shop.db "insert into orders (customer_id, total_cents) values (1, 2500);"
sqlite3 shop.db "select count(*) from orders;"
```

Fixed when: The insert returns with no output and the count goes up by one, from `3` to `4` in this run.

### Your user cannot write to the directory that holds the database

Why: Before it changes the database, SQLite creates a rollback journal named `shop.db-journal` in the same directory. When your user cannot create files in that directory, SQLite reports the database as read-only, even though the database file is writable.

Check:

```bash
ls -l shop.db
ls -ld .
```

Your cause if: The file shows `w` for your user (`-rw-r--r--`) and the directory does not, as in `dr-xr-xr-x 2 dev dev 4096 Nov 23 19:18 .`.

Fix:

```bash
chmod u+w .
```

Verify:

```bash
sqlite3 shop.db "insert into orders (customer_id, total_cents) values (1, 2600);"
sqlite3 shop.db "select count(*) from orders;"
```

Fixed when: The insert returns with no output and the count goes up by one, from `4` to `5` in this run.

## A row that points at a missing parent row is inserted with no error

Symptom:

```text
$ sqlite3 shop.db "insert into orders (customer_id, total_cents) values (99, 500);"
$ sqlite3 shop.db "select id, customer_id from orders where customer_id not in (select id from customers);"
6|99
```

The `orders` table declares `customer_id integer not null references customers(id)`, no customer has the id 99, and the insert printed nothing.

### Foreign key enforcement is off for the connection

Why: SQLite keeps foreign key enforcement off unless a connection turns it on, and the setting lasts only for that connection. The `references customers(id)` clause is stored in the schema and ignored on every connection that has not run `pragma foreign_keys = on;`.

Check:

```bash
sqlite3 shop.db "pragma foreign_keys;"
```

Your cause if: It prints `0`.

Fix:

```bash
sqlite3 shop.db "pragma foreign_key_check;"
sqlite3 shop.db "delete from orders where customer_id not in (select id from customers);"
```

The first command lists the rows that already break the rule, and in this run it printed `orders|6|customers|0`. Decide what to do with each row it lists before you run the second command, which deletes the orders that have no customer. Then start every connection with `pragma foreign_keys = on;`, which in the shell is `-cmd "pragma foreign_keys = on"`.

Verify:

```bash
sqlite3 shop.db "pragma foreign_key_check;"
sqlite3 -cmd "pragma foreign_keys = on" shop.db "insert into orders (customer_id, total_cents) values (99, 500);"
```

Fixed when: The first command prints nothing, and the insert now fails with `Error: stepping, FOREIGN KEY constraint failed (19)`.

## Still stuck?

Collect: The failing command and its full output, plus the output of `sqlite3 --version; ls -ld . shop.db; lsof -w shop.db`.
Contact: Search the SQLite forum at https://sqlite.org/forum/ for the error text first. If no thread matches, post there with what you collected.
