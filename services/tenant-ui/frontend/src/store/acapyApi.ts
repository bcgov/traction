/**
 * This is weird, that our API wrapper is a store.
 * Honestly, I couldn't figure out do this as a component or factory function.
 * To use the other stores (configuration for proxy path, token for auth), I needed a setup() function.
 *
 * Anyway, if we can figure out a cleaner way to do this, then let's do it!
 *
 * There is no data stored, this is pretty much a factory to make traction tenant api requests.
 */
import { defineStore, storeToRefs } from 'pinia';
import axios, { AxiosRequestConfig } from 'axios';
import { useConfigStore } from './configStore';
import { useTenantStore, useTokenStore } from './index';

export const useAcapyApi = defineStore('acapyApi', () => {
  const tokenStore = useTokenStore();
  const tenantStore = useTenantStore();
  const { config } = storeToRefs(useConfigStore());

  function createAxios(options = {}) {
    console.log('creating axios instance...');
    console.log(options);
    return axios.create({
      ...options,
    });
  }

  // setup our tenant api calls to use the configured proxy path "prefix"
  // now callers can just put in the actual traction api url
  const acapyApi = createAxios({
    baseURL: config.value.frontend.tenantProxyPath,
  });

  // need to add authorization before we make traction tenant requests...
  acapyApi.interceptors.request.use(
    async (dataConfig: AxiosRequestConfig) => {
      // console.log('acapyApi.request.fulfilled');
      const result = {
        ...dataConfig,
        headers: {
          'Content-Type': 'application/json',
          accept: 'application/json',
          ...dataConfig.headers,
          Authorization: `Bearer ${tokenStore.token}`,
        },
      };
      return result;
    },
    async (error: any) => {
      console.error('acapyApi.request.error');
      console.error(error);
      return Promise.reject(error);
    }
  );

  acapyApi.interceptors.response.use(
    (response) => {
      // console.log('acapyApi.response.fulfilled');
      // console.log(response);
      return response;
    },
    (error: any) => {
      console.error('acapyApi.response.error');
      console.error(error);
      if (error.response.status === 401) {
        tokenStore.clearToken();
        tenantStore.clearTenant();
        return Promise.reject(`Unauthorized: ${error.response.data.reason}`);
      }
      return Promise.reject(error);
    }
  );

  // private function that calls axios instance configured for tenant calls
  async function callAcapyApi(
    url: string,
    method: string,
    options = {}
  ): Promise<any> {
    return acapyApi({
      method: method.toUpperCase(),
      url,
      ...options,
    });
  }

  async function getHttp(
    url: string,
    params: any = {},
    options: any = {}
  ): Promise<any> {
    return callAcapyApi(url, 'get', {
      ...options,
      params,
    });
  }

  async function postHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callAcapyApi(url, 'post', {
      data,
      ...options,
    });
  }

  async function updateHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callAcapyApi(url, 'update', {
      data,
      ...options,
    });
  }

  async function putHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callAcapyApi(url, 'put', {
      data,
      ...options,
    });
  }

  async function patchHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callAcapyApi(url, 'patch', {
      data,
      ...options,
    });
  }

  async function deleteHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callAcapyApi(url, 'delete', {
      data,
      ...options,
    });
  }

  return { getHttp, postHttp, updateHttp, putHttp, patchHttp, deleteHttp };
});

export default {
  useAcapyApi,
};
