import { useTenantApi } from '../tenantApi';
import { Ref } from 'vue';

export async function fetchItem(
  url: string,
  id: string,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: any = {}
) {
  const tenantApi = useTenantApi();
  const _url = `${url}${id}`;
  console.log(`> fetchItem(${_url})`);
  error.value = null;
  let result = null;

  await tenantApi
    .getHttp(_url, params)
    .then((res) => {
      result = res.data.item;
      console.log(result);
    })
    .catch((err) => {
      error.value = err;
    })
    .finally(() => {
      loading.value = false;
    });
  console.log(`< fetchItem(${_url})`);
  if (error.value != null) {
    // throw error so $onAction.onError listeners can add their own handler
    throw error.value;
  }
  // return data so $onAction.after listeners can add their own handler
  return result;
}
