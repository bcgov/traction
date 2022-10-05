import { useTenantApi } from '../tenantApi';
import { Ref } from 'vue';

export async function fetchList(
  url: string,
  list: Ref<any>,
  error: Ref<any>,
  loading: Ref<boolean>,
  params: any = {}
) {
  const tenantApi = useTenantApi();
  console.log(`> fetchList(${url})`);
  list.value = null;
  error.value = null;
  loading.value = true;
  //console.log(params);
  params = { ...params, page_num: 1, page_size: 100 };
  //console.log(params);
  await tenantApi
    .getHttp(url, params)
    .then((res) => {
      //console.log(res);
      list.value = res.data.items;
      //console.log(list.value);
    })
    .catch((err) => {
      error.value = err;
      // console.log(error.value);
    })
    .finally(() => {
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
