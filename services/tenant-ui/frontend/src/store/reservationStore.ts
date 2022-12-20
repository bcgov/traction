import { API_PATH } from '@/helpers/constants';
import axios from 'axios';
import { defineStore, storeToRefs } from 'pinia';
import { ref } from 'vue';
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

  // actions
  async function makeReservation(payload: any = {}) {
    console.log('> reservationStore.makeReservation');
    error.value = null;
    loading.value = true;
    console.log(payload);

    // Send the request to the API to create the reservation
    await api
      .post(API_PATH.MULTITENANCY_RESERVATION, payload)
      .then((res) => {
        console.log(res);
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

  return {
    reservation,
    loading,
    error,
    makeReservation,
  };
});

export default {
  useReservationStore,
};
