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
import { useTokenStore } from './tokenStore';

export const useTenantApi = defineStore('tenantApi', () => {
  const tokenStore = useTokenStore();
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
  const tenantApi = createAxios({
    baseURL: config.value.frontend.proxyPath,
  });

  // need to add authorization before we make traction tenant requests...
  tenantApi.interceptors.request.use(
    async (config: AxiosRequestConfig) => {
      //console.log('tenantApi.request.fulfilled');
      const result = {
        ...config,
        headers: {
          contentType: 'application/json',
          accept: 'application/json',
          ...config.headers,
          Authorization: `Bearer ${tokenStore.token}`,
        },
      };
      return result;
    },
    async (error: any) => {
      console.error('tenantApi.request.error');
      console.error(error);
      return Promise.reject(error);
    }
  );

  tenantApi.interceptors.response.use(
    (response) => {
      //console.log('tenantApi.response.fulfilled');
      //console.log(response);
      return response;
    },
    (error: any) => {
      console.error('tenantApi.response.error');
      console.error(error);
      // TODO: isolate invalid token/unauthed error
      // not sure if the traction api or the proxy needs fixing, we should expect a 401 but it is 500 right now for invalid token
      tokenStore.clearToken();
      return Promise.reject(error);
    }
  );

  // private function that calls axios instance configured for tenant calls
  async function callTenantApi(url: string, method: string, options = {}): Promise<any> {
    return tenantApi({
      method: method.toUpperCase(),
      url: url,
      ...options,
    });
  }

  async function getHttp(url: string, params: any = {}, options: any = {}): Promise<any> {
    return callTenantApi(url, 'get', {
      ...options,
      params,
    });
  }

  async function postHttp(url: string, data: any = {}, options: any = {}): Promise<any> {
    return callTenantApi(url, 'post', {
      data,
      ...options,
    });
  }

  async function updateHttp(url: string, data: any = {}, options: any = {}): Promise<any> {
    return callTenantApi(url, 'update', {
      data,
      ...options,
    });
  }

  async function putHttp(url: string, data: any = {}, options: any = {}): Promise<any> {
    return callTenantApi(url, 'put', {
      data,
      ...options,
    });
  }

  async function patchHttp(url: string, data: any = {}, options: any = {}): Promise<any> {
    return callTenantApi(url, 'patch', {
      data,
      ...options,
    });
  }

  async function deleteHttp(url: string, data: any = {}, options: any = {}): Promise<any> {
    return callTenantApi(url, 'delete', {
      data,
      ...options,
    });
  }

  return { getHttp, postHttp, updateHttp, putHttp, patchHttp, deleteHttp };
});

export default {
  useTenantApi,
};
