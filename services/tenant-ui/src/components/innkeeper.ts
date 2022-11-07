import axios from "axios";
import config from "config";
const TRACURL: string = config.get("server.tractionUrl");

/**
 * @function login
 * Use the configured Inkeeper Admin key to get the token
 * @returns {string} The inkeeper token
 */
export const login = async () => {
  //config these
  const username = 'innkeeper';
  const password = 'vOQnXutMYVjBfDOuqK9rC2dgEDfU1Mpv';
  const loginUrl: string = `${TRACURL}innkeeper/token`;
  const payload = `username=${username}&password=${password}`;
  const res = await axios({
    method: "post",
    url: loginUrl,
    headers: {
      accept: "application/json",
      "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    },
    data: payload,
  });

  return res.data;
};
