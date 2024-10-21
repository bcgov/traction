<template>
  <div class="grid align-items-start">
    <div class="col-12 md:col-6">
      <strong>{{ $t('about.acaPy.info') }}</strong>
      <p class="mt-0">
        {{
          $t('about.acaPy.acapyVersion', {
            version: acapyVersion,
          })
        }}
      </p>
    </div>
    <div class="col-12 md:col-6 flex justify-content-end pt-0">
      <img src="/img/logo/aries-logo-color.png" class="logo-acapy" />
    </div>
  </div>

  <div class="grid">
    <div class="col-12 md:col-6 lg:col-4">
      <PluginList />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, Ref } from 'vue';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useInnkeeperTenantsStore, useTenantStore } from '@/store';
// PrimeVue
import PluginList from './PluginList.vue';

const route = useRoute();
const innTenantsStore = useInnkeeperTenantsStore();
const tenantsStore = useTenantStore();
const { serverConfig: innServerConfig } = storeToRefs(
  useInnkeeperTenantsStore()
);
const { serverConfig } = storeToRefs(useTenantStore());

const acapyVersion: Ref<string | undefined> = ref('');
const currentRouteName = computed(() => {
  return route.name;
});

onMounted(async () => {
  // Depending on if you're the innkeeper these setttings are different
  if (currentRouteName.value === 'InnkeeperAbout') {
    await innTenantsStore.getServerConfig();
    acapyVersion.value = innServerConfig.value?.config?.version;
  } else {
    await tenantsStore.getServerConfig();
    if (typeof serverConfig.value == 'object' && 'config' in serverConfig.value)
      acapyVersion.value = serverConfig.value.config.version;
  }
});
</script>

<style scoped>
.logo-acapy {
  width: 14em;
}
</style>
