/**
 * See comments in tenantApi.ts, this maybe should be a service rather than a store
 *
 * This is to allow calls to the Innkeeper API with the specific Innkeeper token usage
 */
import { defineStore, storeToRefs } from 'pinia';
import axios, { AxiosRequestConfig } from 'axios';
import { useConfigStore } from '../configStore';
import { useInnkeeperTokenStore } from '../index';

export const useInnkeeperApi = defineStore('innkeeperApi', () => {
  const innkeeperTokenStore = useInnkeeperTokenStore();
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
  const innkeeperApi = createAxios({
    baseURL: config.value.frontend.proxyPath,
  });

  // need to add authorization before we make traction tenant requests...
  innkeeperApi.interceptors.request.use(
    async (config: AxiosRequestConfig) => {
      const result = {
        ...config,
        headers: {
          contentType: 'application/json',
          accept: 'application/json',
          ...config.headers,
          Authorization: `Bearer ${innkeeperTokenStore.token}`,
        },
      };
      return result;
    },
    async (error: any) => {
      console.error('innkeeperApi.request.error');
      console.error(error);
      return Promise.reject(error);
    }
  );

  innkeeperApi.interceptors.response.use(
    (response) => {
      //console.log('tenantApi.response.fulfilled');
      //console.log(response);
      return response;
    },
    (error: any) => {
      console.error('innkeeperApi.response.error');
      console.error(error);
      if (error.response.status == 401) {
        innkeeperTokenStore.clearToken();
        return Promise.reject(`Unauthorized: ${error.response.data.reason}`);
      }
      return Promise.reject(error);
    }
  );

  // private function that calls axios instance configured for innkeeper calls
  async function callInnkeepertApi(
    url: string,
    method: string,
    options = {}
  ): Promise<any> {
    return innkeeperApi({
      method: method.toUpperCase(),
      url: url,
      ...options,
    });
  }

  async function getHttp(
    url: string,
    params: any = {},
    options: any = {}
  ): Promise<any> {
    return callInnkeepertApi(url, 'get', {
      ...options,
      params,
    });
  }

  async function postHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callInnkeepertApi(url, 'post', {
      data,
      ...options,
    });
  }

  async function updateHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callInnkeepertApi(url, 'update', {
      data,
      ...options,
    });
  }

  async function putHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callInnkeepertApi(url, 'put', {
      data,
      ...options,
    });
  }

  async function patchHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callInnkeepertApi(url, 'patch', {
      data,
      ...options,
    });
  }

  async function deleteHttp(
    url: string,
    data: any = {},
    options: any = {}
  ): Promise<any> {
    return callInnkeepertApi(url, 'delete', {
      data,
      ...options,
    });
  }

  return { getHttp, postHttp, updateHttp, putHttp, patchHttp, deleteHttp };
});

export default {
  useInnkeeperApi,
};
