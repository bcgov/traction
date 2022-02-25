import axios from 'axios';

import { ApiRoutes } from '@/utils/constants';
/**
 * @function appAxios
 * Returns an Axios instance with any preconfiguration
 * @param {integer} [timeout=10000] Number of milliseconds before timing out the request
 * @returns {object} An axios instance
 */
export function appAxios(timeout = 60000) {
  const axiosOptions = { timeout: timeout };
  axiosOptions.baseURL = `${process.env.VUE_APP_BASE_API}${ApiRoutes.BASEPATH}`;


  // Put auth header here if we make this app secured

  const instance = axios.create(axiosOptions);

  return instance;
}
