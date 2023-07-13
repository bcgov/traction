import { beforeEach, describe, expect, test } from 'vitest';
import {
  filterByStateActive,
  sortByLabelAscending,
  filterMapSortList,
} from '../../../src/store/utils/index';

describe('store utils', () => {
  test('filterByStateActive', () => {
    const mapItem = {
      label: 'label1',
      state: 'active',
    };

    expect(filterByStateActive(mapItem)).toBeTruthy();
    mapItem.state = 'inactive';
    expect(filterByStateActive(mapItem)).toEqual(false);
  });

  test('sortByLabelAscending', () => {
    const mapItem1 = {
      label: 'a',
      state: 'active',
    };
    const mapItem2 = {
      label: 'b',
      state: 'active',
    };

    expect(sortByLabelAscending(mapItem1, mapItem2)).toBe(-1);
    expect(sortByLabelAscending(mapItem2, mapItem1)).toBe(1);
    expect(sortByLabelAscending(mapItem1, mapItem1)).toBe(0);
  });

  test('filterMapSortList', () => {
    const list = [
      {
        label: 'a',
        state: 'active',
      },
      {
        label: 'b',
        state: 'active',
      },
      {
        label: 'c',
        state: 'inactive',
      },
    ];

    const result = filterMapSortList(
      list,
      undefined,
      sortByLabelAscending,
      filterByStateActive
    );
    expect(result.length).toBe(2);
    expect(result[0].label).toBe('a');
    expect(result[1].label).toBe('b');
  });
});
