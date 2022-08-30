import { useTenantApi } from '../tenantApi';
import { Ref } from 'vue';

export async function fetchItem(url: string, id: string, dict: any, error: Ref<any>, loading: Ref<boolean>, params: any = {}) {
    /*
    This method will fetch an item from the api and add it to a dictionary in the store, 
    to be retrieved by the primary key value later.

    TODO: fix dict typing, should be a Ref<object> but my typescript linter doesn't like that.
    */


    const tenantApi = useTenantApi();
    console.log(`> fetchItem(${url})`);
    error.value = null;
    // loading.value = true;
    await tenantApi
        .getHttp(url + id, params)
        .then((res) => {
            dict.value[id] = res.data.item;
            console.log(dict.value[id]);
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
    return dict.value[id];
}
