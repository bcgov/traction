import { API_PATH } from '@/helpers/constants';
import axios from 'axios';
import { defineStore, storeToRefs } from 'pinia';
import { ref, Ref } from 'vue';
import { useConfigStore } from './configStore';
import { RESERVATION_STATUSES } from '@/helpers/constants';

export const useReservationStore = defineStore('reservation', () => {
  const { config } = storeToRefs(useConfigStore());
  // A raw api call without using the interceptors from the acapyApiStore
  // Needed for the open call to reservation at this point
  const api = axios.create({
    baseURL: config.value.frontend.tenantProxyPath,
  });

  // A different axios instance with a basepath just of the tenant UI backend
  const backendApi = axios.create({
    baseURL: config.value.frontend.apiPath,
  });

  // state
  const loading: any = ref(false);
  const error: any = ref(null);
  const reservation: any = ref(null);
  const status: Ref<string> = ref('');
  const walletId: Ref<string> = ref('');
  const walletKey: Ref<string> = ref('');

  // actions
  function resetState() {
    reservation.value = null;
    status.value = '';
    walletId.value = '';
    walletKey.value = '';
  }

  async function makeReservation(payload: any = {}) {
    console.log('> reservationStore.makeReservation');
    error.value = null;
    loading.value = true;
    reservation.value = null;

    // Send the request to the API to create the reservation
    await api
      .post(API_PATH.MULTITENANCY_RESERVATIONS, payload)
      .then((res) => {
        console.log('res from creating a res', res);
        reservation.value = res.data;
      })
      .catch((err) => {
        error.value = err;
        console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }

    // Separately dispatch a non-blocking call to send the contact emails
    // If these fail we won't raise any error to the UI
    const emailPayload = {
      contactEmail: payload.contact_email,
      reservationId: reservation.value.reservation_id,
    };
    backendApi
      .post(API_PATH.EMAIL_CONFIRMATION, emailPayload)
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        console.error(`Error while trying to send confirmation email: ${err}`);
      });

    console.log('< reservationStore.makeReservation');

    // return data so $onAction.after listeners can add their own handler
    return reservation.value;
  }

  async function checkReservation(reservationId: string, email: string) {
    console.log('> reservationStore.checkReservation');
    resetState();
    error.value = null;
    loading.value = true;

    await api
      .get(API_PATH.MULTITENANCY_RESERVATION(reservationId))
      .then((res) => {
        if (res.data) {
          // The API doesn't check email address against res ID but we can do it on the front end at least
          if (res.data.contact_email !== email) {
            status.value = RESERVATION_STATUSES.NOT_FOUND;
          } else {
            reservation.value = res.data;
            status.value = res.data.state;
          }
        }
      })
      .catch((err) => {
        if (err.response && err.response.status === 404) {
          // Handle not founds for this as a status not an exception
          status.value = RESERVATION_STATUSES.NOT_FOUND;
        } else {
          error.value = err;
          console.log(error.value);
        }
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< reservationStore.checkReservation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return status.value;
  }

  async function checkIn(reservationId: string, password: string) {
    console.log('> reservationStore.checkIn');
    error.value = null;
    loading.value = true;
    await api
      .post(API_PATH.MULTITENANCY_RESERVATION_CHECK_IN(reservationId), {
        reservation_pwd: password,
      })
      .then((res) => {
        // A successful check in, set the status and display the returned wallet key and ID
        status.value = RESERVATION_STATUSES.SHOW_WALLET;
        walletId.value = res.data.wallet_id;
        walletKey.value = res.data.wallet_key;
      })
      .catch((err) => {
        error.value = err;
        console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< reservationStore.checkIn');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  return {
    reservation,
    loading,
    error,
    status,
    walletId,
    walletKey,
    resetState,
    makeReservation,
    checkReservation,
    checkIn,
  };
});

export default {
  useReservationStore,
};
