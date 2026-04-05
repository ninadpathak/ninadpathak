const fs = require('fs').promises;

let counter = 0;
let lock = Promise.resolve();

async function incrementCounter() {
    // We use a lock mechanism to ensure serial execution and avoid race conditions
    lock = lock.then(async () => {
        const current = counter;
        // Simulate some asynchronous work
        await new Promise(resolve => setTimeout(resolve, Math.random() * 50));
        counter = current + 1;
        
        try {
            await fs.appendFile('log.txt', `Incremented to ${counter}\n`);
        } catch (err) {
            console.error('File write error:', err);
        }
        
        return counter;
    });
    
    return lock;
}

function resetCounter() {
    counter = 0;
}

// Lack of proper async coordination
async function runLoop() {
    const promises = [];
    for (let i = 0; i < 10; i++) {
        promises.push(incrementCounter().then((count) => {
            console.log('Current count:', count);
        }));
    }
    await Promise.all(promises);
}

// Only run the loop if not being required as a module (e.g., during tests)
if (require.main === module) {
    runLoop();
}

module.exports = { incrementCounter, resetCounter };
