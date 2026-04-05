const fs = require('fs').promises;

let counter = 0;
let queue = Promise.resolve();

async function incrementCounter() {
    // Capture a reference to the counter result for this call.
    // Each call chains onto the queue so increments are serialized,
    // eliminating the race condition present when concurrent callers
    // all read the same stale value before any write completes.
    let resolve, reject;
    const result = new Promise((res, rej) => {
        resolve = res;
        reject = rej;
    });

    queue = queue.then(async () => {
        const current = counter;
        await new Promise(res => setTimeout(res, Math.random() * 50));
        counter = current + 1;

        try {
            await fs.appendFile('log.txt', `Incremented to ${counter}\n`);
        } catch (err) {
            console.error('File write error:', err);
        }

        resolve(counter);
    }).catch((err) => {
        // Swallow chain errors so subsequent queued calls still run.
        reject(err);
    });

    return result;
}

function resetCounter() {
    counter = 0;
    // Reset the queue too, otherwise old promise chains carry over
    // and newly queued calls wait on stale work.
    queue = Promise.resolve();
}

async function runLoop() {
    const promises = [];
    for (let i = 0; i < 10; i++) {
        promises.push(
            incrementCounter().then((count) => {
                console.log('Current count:', count);
            })
        );
    }
    await Promise.all(promises);
}

if (require.main === module) {
    runLoop();
}

module.exports = { incrementCounter, resetCounter };
