<template>
  <Dialog
    v-model:visible="displaySessionWarning"
    :header="$t('session.countdownHeader')"
    :style="{ width: '30vw' }"
  >
    <div style="text-align: center">
      <p>{{ $t('session.countdown', { seconds: countDown }) }}</p>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import Dialog from 'primevue/dialog';
import { onBeforeUnmount, ref } from 'vue';
import { useRoute } from 'vue-router';

import { useConfigStore } from '@/store/configStore';

const {
  config: {
    value: {
      frontend: {
        session: { countdownSeconds, timeoutSeconds },
      },
    },
  },
} = storeToRefs(useConfigStore());

let inactivityCount = 0;
const displaySessionWarning = ref(false);
const countDown = ref(countdownSeconds);
let countDownInterval: string | number | NodeJS.Timeout | undefined;
const route = useRoute();

onBeforeUnmount(() => {
  clearInterval(interval);
  clearInterval(countDownInterval);
});

const createListeners = () => {
  window.addEventListener('mousemove', resetTimer);
  window.addEventListener('mousedown', resetTimer);
  window.addEventListener('keypress', resetTimer);
  window.addEventListener('touchmove', resetTimer);
};

const resetTimer = () => {
  inactivityCount = 0;
};

const inactivityCountInterval = () => {
  checkForRecentActivity();
  inactivityCount += 1;
  createCountDownIfNecessary();
  logoutOnTimeout();
};

const checkForRecentActivity = () => {
  if (inactivityCount === 0) {
    clearInterval(countDownInterval);
    displaySessionWarning.value = false;
    countDown.value = countdownSeconds;
  }
};

const createCountDownIfNecessary = () => {
  if (
    inactivityCount >= timeoutSeconds - countdownSeconds &&
    !displaySessionWarning.value
  ) {
    displaySessionWarning.value = true;
    countDownInterval = setInterval(() => {
      countDown.value -= 1;
    }, 1000);
  }
};

const logoutOnTimeout = () => {
  if (inactivityCount >= timeoutSeconds) {
    localStorage.setItem('inactivity-timeout', 'true');
    if (route.path.includes('innkeeper'))
      window.location.href = '/innkeeper/logout';
    else window.location.href = '/logout';
  }
};

const interval = setInterval(inactivityCountInterval, 1000);

createListeners();
</script>
