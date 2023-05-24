import { test, expect } from 'vitest';

function sum(...nums: number[]) {
  return nums.reduce((a, b) => a + b, 0);
}

test('1 + 1', () => {
  expect(sum(1, 1)).toEqual(2);
});

test('1 + 2 + 3', () => {
  expect(sum(1, 2, 3)).toEqual(6);
});

test('10 numbers', () => {
  expect(sum(...Array(10).keys())).toEqual(45);
});

test('1 number', () => {
  expect(sum(1)).toEqual(1);
});

test('0 numbers', () => {
  expect(sum()).toEqual(0);
});
