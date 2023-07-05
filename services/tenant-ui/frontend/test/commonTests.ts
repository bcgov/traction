import { expect } from 'vitest';

/**
 * @param store - the store to test
 * @param func - the function to call
 * @param loadingKey - the key to check for loading
 */
const testSuccessResponse = async (
  store: any,
  func: () => void,
  loadingKey: string
) => {
  expect(store[loadingKey]).toEqual(true);
  const response = await func;

  expect(response).not.toBeNull();
  expect(store[loadingKey]).toEqual(false);
  expect(store.error).toBeNull();
};

/**
 * @param store - the store to test
 * @param func - the function to call
 * @param loadingKey - the key to check for loading
 */
const testErrorResponse = async (
  store: any,
  func: () => void,
  loadingKey: string
) => {
  expect(store[loadingKey]).toEqual(true);
  await expect(func).rejects.toThrow();
  expect(store[loadingKey]).toEqual(false);
  expect(store.error).not.toBeNull();
};

export { testErrorResponse, testSuccessResponse };
