import axios from "axios";
import config from "config";
const TRACTION_URL: string = config.get("server.tractionUrl");
const INNKEEPER_USER = config.get("server.innkeeper.user");
const INNKEEPER_KEY = config.get("server.innkeeper.key");

/**
 * @function login
 * Use the configured Inkeeper Admin key to get the token
 * @returns {string} The inkeeper token
 */
export const login = async () => {
  const loginUrl = `${TRACTION_URL}/multitenancy/tenant/${INNKEEPER_USER}/token`;
  const payload = { wallet_key: INNKEEPER_KEY };
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
    const reservationUrl = `${TRACTION_URL}/innkeeper/reservations`;
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
