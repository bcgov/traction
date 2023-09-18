<template>
  <Dialog
    v-model:visible="displaySessionTimeoutMessage"
    :header="$t('session.timeoutHeader')"
    :style="{ width: '30vw' }"
  >
    <div style="text-align: center">
      <i class="pi pi-info-circle" style="font-size: 2rem"></i>
    </div>
    <div>
      <p>{{ $t('session.timeoutMessage') }}</p>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog';
import { ref } from 'vue';

const displaySessionTimeoutMessage = ref(false);

if (localStorage.getItem('inactivity-timeout')) {
  localStorage.removeItem('inactivity-timeout');
  displaySessionTimeoutMessage.value = true;
}
</script>
