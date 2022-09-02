import { Ref } from 'vue';
import { fetchItem } from './fetchItem';

export async function getItem(
  url: string,
  id: string,
  dict: any,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: any = {},
  forceFetch = false
) {
  /*
    This method will fetch an item from the api and add it to a dict object provided, 
    to be retrieved by the primary key value later.

    TODO: fix dict typing, should be a Ref<object> but my typescript linter doesn't like that.
    */
  if (forceFetch || !dict.value[id]) {
    dict.value[id] = await fetchItem(url, id, error, loading, params);
  }
  const result = dict.value[id];
  console.log(dict.value);

  return result;
}
