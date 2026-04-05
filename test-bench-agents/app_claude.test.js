const { incrementCounter, resetCounter } = require('./app_claude');

jest.mock('fs', () => ({
    promises: {
        appendFile: jest.fn().mockResolvedValue(undefined),
    },
}));

jest.spyOn(global, 'setTimeout').mockImplementation((fn) => fn());

beforeEach(() => {
    resetCounter();
    jest.clearAllMocks();
});

describe('incrementCounter', () => {
    test('returns 1 on first call', async () => {
        const result = await incrementCounter();
        expect(result).toBe(1);
    });

    test('increments sequentially across multiple awaited calls', async () => {
        const first = await incrementCounter();
        const second = await incrementCounter();
        const third = await incrementCounter();
        expect([first, second, third]).toEqual([1, 2, 3]);
    });

    test('no lost increments under concurrent calls', async () => {
        const results = await Promise.all(
            Array.from({ length: 10 }, () => incrementCounter())
        );
        expect(new Set(results).size).toBe(10);
        expect(Math.max(...results)).toBe(10);
    });

    test('writes to log file for each increment', async () => {
        const { promises: fsMock } = require('fs');
        await incrementCounter();
        expect(fsMock.appendFile).toHaveBeenCalledTimes(1);
        expect(fsMock.appendFile).toHaveBeenCalledWith('log.txt', 'Incremented to 1\n');
    });

    test('resetCounter resets global state and queue', async () => {
        await incrementCounter();
        await incrementCounter();
        resetCounter();
        const result = await incrementCounter();
        expect(result).toBe(1);
    });
});
