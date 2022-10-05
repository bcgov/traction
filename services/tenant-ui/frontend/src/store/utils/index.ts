export { fetchList } from './fetchList';
export { fetchItem } from './fetchItem';

/**
 * Filter, Map and Sort a list.
 * List is filtered, then mapped to new object type, then sorted.
 * By default filter is all items, map does not change the item and sort is the order list is in currently.
 * By default, basically it does nothing.
 *
 * function parameters are order in most likely to override: map, sort, filter
 *
 * example mapFn: (item: any) => { return {'label': `${item.name} (${item.version})`, 'value': item.id, 'status': item.status }; }
 * example sortFn: (a:any, b: any) => { return a.label.localeCompare(b.label); })
 * example filterFn: (item: any) => { return item.status === 'Active'; }
 * @param {Array} list - The current list
 * @param {Function} mapFn - Convert current item into new type of item
 * @param {Function} sortFn - Sort the list according to this function (objects are the mapFn object!)
 * @param {Function} filterFn - Filter items from current list
 */
export function filterMapSortList(
  list: any,
  mapFn: Function = (item: any) => item,
  sortFn: Function = (a: any, b: any) => 0,
  filterFn: Function = (item: any) => true
) {
  let result: any[] = [];
  console.log(list);
  console.log(mapFn);
  console.log(filterFn);
  console.log(sortFn);

  if (list != null) {
    result = list
      .filter(filterFn)
      .map((item: any) => mapFn(item))
      .sort(sortFn);
  }
  console.log(result);
  return result;
}

export function filterByStatusActive(item: any) {
  return item.status === 'Active';
}
export function sortByLabelAscending(a: any, b: any) {
  return a.label.localeCompare(b.label);
}
