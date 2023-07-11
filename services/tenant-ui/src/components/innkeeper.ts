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

/**
 * @function createReservation
 * Create a reservation in Traction
 * @returns {object} the reservation object
 */
export const createReservation = async (req: any, token: string) => {
  try {
    const auth = `Bearer ${token}`;
    const reservationUrl = `${TRACURL}/innkeeper/reservations`;
    const payload = req.body;

    const res = await axios({
      method: "post",
      url: reservationUrl,
      data: payload,
      headers: {
        Authorization: auth,
      },
    });
    return res.data;
  } catch (error) {
    return error;
  }
};
