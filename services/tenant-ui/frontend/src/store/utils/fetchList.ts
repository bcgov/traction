import { useAcapyApi } from '../acapyApi';
import { AxiosRequestConfig } from 'axios';
import { Ref } from 'vue';

export async function fetchList<T>(
  url: string,
  list: Ref<T[]>,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: object = {},
  options?: object
) {
  const acapyApi = useAcapyApi();
  return fetchListFromAPI(acapyApi, url, list, error, loading, params, options);
}

export async function fetchListFromAPI<T>(
  api: any,
  url: string,
  list: Ref<T[]>,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: object = {},
  options?: object
): Promise<T[]> {
  console.log(`> fetchList(${url})`);
  list.value = [];
  error.value = null;
  loading.value = true;
  params = { ...params };
  await api
    .getHttp(url, params, options)
    .then((res: AxiosRequestConfig): void => {
      if (res.data.results) {
        list.value = res.data.results;
      } else if (res.data.result) {
        // Some lists have it singular
        list.value = res.data.result;
      }
    })
    .catch((err: string): void => {
      error.value = err;
    })
    .finally((): void => {
      loading.value = false;
    });
  console.log(`< fetchList(${url})`);
  if (error.value != null) {
    // throw error so $onAction.onError listeners can add their own handler
    throw error.value;
  }
  // return data so $onAction.after listeners can add their own handler
  return list.value;
}
