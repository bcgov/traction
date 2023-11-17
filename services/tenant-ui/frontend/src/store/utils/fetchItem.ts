import { useAcapyApi } from '../acapyApi';
import { AxiosRequestConfig } from 'axios';
import { Ref } from 'vue';

export async function fetchItem<T>(
  url: string,
  id: string | undefined,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: object = {}
): Promise<T | object | null> {
  const acapyApi = useAcapyApi();
  let dataUrl = url;
  if (id) {
    // Normalize if the caller supplies a trailing slash or not
    dataUrl = `${dataUrl.replace(/\/$/, '')}/${id}`;
  }
  console.log(` > fetchItem(${dataUrl})`);
  error.value = null;
  let result = null;

  await acapyApi
    .getHttp(dataUrl, params)
    .then((res: AxiosRequestConfig): void => {
      if (res?.data?.result) {
        // Some acapy resource item calls put things under "result"
        result = res.data.result;
      } else {
        result = res.data;
      }
      console.log(result);
    })
    .catch((err: string): void => {
      error.value = err;
    })
    .finally((): void => {
      loading.value = false;
    });
  console.log(`< fetchItem(${dataUrl})`);
  if (error.value != null) {
    // throw error so $onAction.onError listeners can add their own handler
    throw error.value;
  }
  // return data so $onAction.after listeners can add their own handler
  return result;
}
