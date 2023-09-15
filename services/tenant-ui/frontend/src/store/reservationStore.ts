import {
  API_PATH,
  RESERVATION_STATUSES,
  RESERVATION_STATUS_ROUTE,
} from '@/helpers/constants';
import axios from 'axios';
import { defineStore, storeToRefs } from 'pinia';
import { ref, Ref } from 'vue';
import { useConfigStore } from './configStore';

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
    // If OIDC is enabled, send the request to the tenant UI backend instead of the proxy
    let _axios = api;
    let _axiosConfig = {
      url: API_PATH.MULTITENANCY_RESERVATIONS,
    };
    if (config.value.frontend.showOIDCReservationLogin) {
      _axios = backendApi;
      _axiosConfig = {
        url: API_PATH.OIDC_INNKEEPER_RESERVATION,
      };
    }

    await _axios({ method: 'post', data: payload, ..._axiosConfig })
      .then((res) => {
        console.log('res from creating a res', res);
        reservation.value = res.data;
      })
      .catch((err) => {
        error.value = err;
        console.log(error.value);
      })
      .finally(() => {
        if (!reservation.value?.reservation_pwd) {
          // Keep on loading if we auto accept to the next step
          loading.value = false;
        }
      });

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }

    if (reservation.value?.reservation_pwd) {
      // Auto-approve is on, just check-in for them
      checkIn(
        reservation.value.reservation_id,
        reservation.value.reservation_pwd
      );
    } else {
      // Send the user the reservation ID and details about waiting for the innkeeper to approve
      const trimUrl = window.location.origin;

      // Separately dispatch a non-blocking call to send the contact emails
      // If these fail we won't raise any error to the UI
      const emailPayload = {
        contactEmail: payload.contact_email,
        contactName: payload.tenant_name,
        reservationId: reservation.value.reservation_id,
        serverUrl: trimUrl,
        serverUrlStatusRoute: `${trimUrl}/${RESERVATION_STATUS_ROUTE}`,
      };
      backendApi
        .post(API_PATH.EMAIL_CONFIRMATION, emailPayload)
        .then((res) => {
          console.log(res);
        })
        .catch((err) => {
          console.error(
            `Error while trying to send confirmation email: ${err}`
          );
        });
    }

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
