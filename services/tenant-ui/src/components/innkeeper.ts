import axios from "axios";
import config from "config";
const TRACURL: string = config.get("server.tractionUrl");
const INN_USER = config.get("server.innkeeper.user");
const INN_PW = config.get("server.innkeeper.key");

/**
 * @function login
 * Use the configured Inkeeper Admin key to get the token
 * @returns {string} The inkeeper token
 */
export const login = async () => {
  const loginUrl = `${TRACURL}innkeeper/token`;
  const payload = `username=${INN_USER}&password=${INN_PW}`;
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
