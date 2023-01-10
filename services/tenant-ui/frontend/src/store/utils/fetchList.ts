import { useAcapyApi } from '../acapyApi';
import { AxiosRequestConfig } from 'axios';
import { Ref } from 'vue';

export async function fetchList(
  url: string,
  list: Ref<any>,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: object = {}
) {
  const acapyApi = useAcapyApi();
  return fetchListFromAPI(acapyApi, url, list, error, loading, params);
}

export async function fetchListFromAPI(
  api: any,
  url: string,
  list: Ref<any[]>,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: object = {}
) {
  console.log(`> fetchList(${url})`);
  list.value = [];
  error.value = null;
  loading.value = true;
  params = { ...params };
  await api
    .getHttp(url, params)
    .then((res: AxiosRequestConfig): void => {
      // console.log(res);
      list.value = res.data.results;
      // console.log(list.value);
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
