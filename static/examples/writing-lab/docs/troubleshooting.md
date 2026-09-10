# Choose a recovery action

| Symptom | Check | Action or stop condition |
| --- | --- | --- |
| Connection refused | Compare `LAB_URL` with the running server's terminal | Correct the URL; if the server stopped, its stored state is gone |
| Empty reply after the fixture drop header | Confirm the request key and payload were saved and the same instance remains running | Repeat with that key and format; omit the failure header |
| HTTP 409 | Compare the format with the original request using that key | Restore the original format to recover its result; allocate a new key only for a deliberately separate operation |
| HTTP 400 | Read the `error` field; compare with the reference | Repair the named invalid input before resending |
| Server restarted after an ambiguous response | Confirm the process restart | Stop the recovery experiment: this fixture cannot recover the previous record |

A fresh key is a request for a separate operation. Do not recommend it merely because a response was lost.

Run `node check.mjs` to verify the controlled failure cases. These checks establish fixture behavior, not task-completion results from human readers.
