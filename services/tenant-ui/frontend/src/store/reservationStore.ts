import { API_PATH } from '@/helpers/constants';
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAcapyApi } from './acapyApi';

export const useReservationStore = defineStore('reservation', () => {
  // state
  const loading: any = ref(false);
  const error: any = ref(null);
  const reservation: any = ref(null);

  const acapyApi = useAcapyApi();

  // actions
  async function makeReservation(payload: any = {}) {
    console.log('> reservationStore.makeReservation');
    error.value = null;
    loading.value = true;
    console.log(payload);
    await acapyApi
      .putHttp(API_PATH.MULTITENANCY_RESERVATION, payload)
      .then((res) => {
        console.log(res);
        reservation.value = res.data.item;
      })
      .catch((err) => {
        error.value = err;
        console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< reservationStore.makeReservation');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return reservation.value;
  }

  return {
    reservation,
    loading,
    error,
    makeReservation
  };
});

export default {
  useReservationStore,
};
