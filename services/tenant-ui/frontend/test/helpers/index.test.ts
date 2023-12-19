import { configStringToObject } from '@/helpers';
import { expect, test, describe } from 'vitest';

describe('helpers/index.ts', () => {
  describe('configStringToObject', () => {
    test('returns a parsed object from the format a cfg value comes in', async () => {
      expect(configStringToObject('{"abc": {"xyz": 123}}')).toEqual({
        abc: { xyz: 123 },
      });
    });

    test('returns a blank object for non parsed strings', async () => {
      expect(configStringToObject('testz')).toEqual({});
      // @ts-expect-error
      expect(configStringToObject(undefined)).toEqual({});
    });

    test('returns back objects if object type is supplied', async () => {
      // @ts-expect-error
      expect(configStringToObject({ abc: '123' })).toEqual({ abc: '123' });
      // @ts-expect-error
      expect(configStringToObject(null)).toEqual(null);
    });
  });
});
