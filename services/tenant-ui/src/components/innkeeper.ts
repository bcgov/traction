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
  const loginUrl = `${TRACURL}/multitenancy/tenant/${INN_USER}/token`;
  const payload = { wallet_key: INN_PW };
  const res = await axios({
    method: "post",
    url: loginUrl,
    data: payload,
  });

  return res.data;
};
