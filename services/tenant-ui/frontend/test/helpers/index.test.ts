import {
  configStringToObject,
  toKebabCase,
  formatGuid,
  stringOrBooleanTruthy,
  isJsonString,
  formatUnixDate,
} from '@/helpers';
import { expect, test, describe } from 'vitest';

describe('helpers/index.ts', () => {
  describe('formatUnixDate', () => {
    test('formats correctly with formatUnixDate', async () => {
      expect(formatUnixDate(1703027241)).toEqual('December 19 2023');
    });
  });

  describe('toKebabCase', () => {
    test('formats correctly with toKebabCase', async () => {
      expect(toKebabCase('abc')).toEqual('abc');
      expect(toKebabCase('AbcXyz123')).toEqual('abc-xyz123');
    });
  });

  describe('formatGuid', () => {
    test('formats correctly with formatGuid', async () => {
      expect(formatGuid('d9cfa0d1ed514a4e9c63f6f620bbd360')).toEqual(
        'd9cfa0d1-ed51-4a4e-9c63-f6f620bbd360'
      );
      expect(formatGuid('d9cfa0d1-ed51-4a4e-9c63-f6f620bbd360')).toEqual(
        'd9cfa0d1-ed51-4a4e-9c63-f6f620bbd360'
      );
    });
  });

  describe('stringOrBooleanTruthy', () => {
    test('returns the right boolean for boolean supplied', async () => {
      expect(stringOrBooleanTruthy(true)).toEqual(true);
      expect(stringOrBooleanTruthy(false)).toEqual(false);
    });

    test('returns the right boolean for strings', async () => {
      expect(stringOrBooleanTruthy('true')).toEqual(true);
      expect(stringOrBooleanTruthy('false')).toEqual(false);
      expect(stringOrBooleanTruthy('True')).toEqual(false);
    });

    test('returns the false for unexpected types', async () => {
      // @ts-expect-error unit test other types
      expect(stringOrBooleanTruthy(undefined)).toEqual(false);
      // @ts-expect-error unit test other types
      expect(stringOrBooleanTruthy(1)).toEqual(false);
      // @ts-expect-error unit test other types
      expect(stringOrBooleanTruthy(null)).toEqual(false);
      // @ts-expect-error unit test other types
      expect(stringOrBooleanTruthy({ a: 1 })).toEqual(false);
    });
  });

  describe('isJsonString', () => {
    test('returns true for valid object strings', async () => {
      expect(isJsonString('{ "abc": {"xyz": 123}}')).toEqual(true);
      expect(isJsonString('{ }')).toEqual(true);
    });

    test('returns false for invalid object strings', async () => {
      expect(isJsonString('test')).toEqual(false);
    });

    test('returns false for undefined', async () => {
      // @ts-expect-error unit test other types
      expect(isJsonString(undefined)).toEqual(false);
    });

    test('returns true for null object', async () => {
      // @ts-expect-error unit test other types
      expect(isJsonString(null)).toEqual(true);
    });
  });

  describe('configStringToObject', () => {
    test('returns a parsed object from the format a cfg value comes in', async () => {
      expect(configStringToObject('{"abc": {"xyz": 123}}')).toEqual({
        abc: { xyz: 123 },
      });
    });

    test('returns a blank object for non parsed strings', async () => {
      expect(configStringToObject('testz')).toEqual({});
      // @ts-expect-error unit test other types
      expect(configStringToObject(undefined)).toEqual({});
    });

    test('returns back objects if object type is supplied', async () => {
      // @ts-expect-error unit test other types
      expect(configStringToObject({ abc: '123' })).toEqual({ abc: '123' });
      // @ts-expect-error unit test other types
      expect(configStringToObject(null)).toEqual(null);
    });
  });
});
