<template>
  <div v-if="loading || loadingOca" class="grid">
    <div class="col-12 md:col-6 xl:col-3">
      <SkeletonCard />
    </div>
  </div>

  <div v-else-if="credentials && credentials.length" class="grid">
    <div
      v-for="(cred, index) in credentials"
      :key="index"
      class="col-12 md:col-6 xl:col-3"
    >
      <OcaCard :credential="cred" />
    </div>
  </div>

  <span v-else> There are no credentials in your Wallet </span>
</template>

<script setup lang="ts">
// Types
import {
  CredAttrSpec,
  V10CredentialExchange,
} from '@/types/acapyApi/acapyInterface';

// Vue
import { onMounted } from 'vue';
// PrimeVue etc
import { useToast } from 'vue-toastification';
// State
import { useHolderStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import OcaCard from './credentialOcaCard/OcaCard.vue';
import SkeletonCard from '@/components/common/SkeletonCard.vue';

// The emits it can do (common things between table and card view handled in parent)
// defineEmits(['accept', 'delete', 'reject']);

const toast = useToast();

// State
const { loading, loadingOca, credentials } = storeToRefs(useHolderStore());
const holderStore = useHolderStore();

onMounted(async () => {
  holderStore.listCredentials();
  // Get the oca list avaliable, each card will fetch it's OCA though
  holderStore.listOcas().catch((err) => {
    console.error(err);
    toast.error(`Failed to load Credentials from your wallet: ${err}`);
  });
});
</script>
