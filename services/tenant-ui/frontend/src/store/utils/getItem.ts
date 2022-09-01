import { Ref } from 'vue';
import { fetchItem } from './fetchItem';

export async function getItem(
  url: string,
  id: string,
  dict: any,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: any = {},
  forceFetch: boolean = false
) {
  /*
    This method will fetch an item from the api and add it to a dict object provided, 
    to be retrieved by the primary key value later.

    TODO: fix dict typing, should be a Ref<object> but my typescript linter doesn't like that.
    */
  let result = null;

  if (forceFetch || dict.value[id]) {
    result = dict.value[id]; //item already loaded
  } else {
    result = fetchItem(url, id, error, loading, params);
    dict.value[id] = result;
  }

  return dict.value[id];
}
