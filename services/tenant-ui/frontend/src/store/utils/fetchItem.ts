import { useTenantApi } from '../tenantApi';
import { AxiosRequestConfig } from 'axios';
import { Ref } from 'vue';

export async function fetchItem(
  url: string,
  id: string,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: object = {}
): Promise<object | null | undefined> {
  const tenantApi = useTenantApi();
  const dataUrl = `${url}${id}`;
  console.log(` > fetchItem(${dataUrl})`);
  error.value = null;
  let result = null;

  await tenantApi
    .getHttp(dataUrl, params)
    .then((res: AxiosRequestConfig): void => {
      result = res.data.item;
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
