import { useTenantApi } from '../tenantApi';
import { Ref } from 'vue';

export async function fetchItem(url: string, id: string, dict: any, error: Ref<any>, loading: Ref<boolean>, params: any = {}) {
    const tenantApi = useTenantApi();
    console.log(`> fetchItem(${url})`);
    error.value = null;
    // loading.value = true;
    await tenantApi
        .getHttp(url + id, params)
        .then((res) => {
            console.log(res);
            dict.value[id] = res.data.item;
            console.log(dict[id]);
        })
        .catch((err) => {
            error.value = err;
            // console.log(error.value);
        })
        .finally(() => {
            loading.value = false;
        });
    console.log(`< fetchItem(${url})`);
    if (error.value != null) {
        // throw error so $onAction.onError listeners can add their own handler
        throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return dict.value;
}
