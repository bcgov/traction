<template>
  <MainCardContent
    :title="$t('serverConfig.serverConfig')"
    :refresh-callback="loadConfig"
  >
    <ProgressSpinner v-if="loading" />
    <div v-else>
      <p>
        <strong>{{ $t('serverConfig.acapyVersion') }}</strong>
        {{ serverConfig?.config?.version }}
      </p>
      <p>
        <strong>{{ $t('serverConfig.tractionProxy') }}</strong>
        {{ config.frontend.tenantProxyPath }}
        <a :href="swaggerUrl" target="_blank"> <i class="pi pi-external-link ml-2" /> </a>
      </p>

      <div class="grid mt-3">
        <div class="col">
          <Fieldset
            :legend="$t('serverConfig.ledger.ledgerDetails')"
            :toggleable="true"
          >
            <p class="mt-0">
              <strong>{{ $t('serverConfig.ledger.ledgerList') }}</strong>
            </p>
            <DataTable :value="ledgerConfigList" size="small" striped-rows>
              <Column field="id" header="id"></Column>
              <Column field="endorser_alias" header="endorser_alias"></Column>
              <Column field="endorser_did" header="endorser_did"></Column>
            </DataTable>
            <p>
              <strong>{{ $t('serverConfig.ledger.quickConnect') }}</strong>
              {{ config.frontend.quickConnectEndorserName }}
            </p>
            <p>
              <strong>{{ $t('serverConfig.ledger.default') }}</strong>
              {{ serverConfig?.config?.['ledger.write_ledger'] }}
            </p>
          </Fieldset>

          <PluginList class="mt-4" />

          <Accordion class="mt-4">
            <AccordionTab :header="$t('serverConfig.expand')">
              <div v-if="loading" class="flex justify-content-center">
                <ProgressSpinner />
              </div>
              <vue-json-pretty v-else :data="serverConfig" />
            </AccordionTab>
          </Accordion>
        </div>

        <div class="col">
          <Fieldset
            :legend="$t('serverConfig.tenantUi.tenantUi')"
            :toggleable="true"
          >
            <p class="m-0"></p>
          </Fieldset>
        </div>
      </div>
    </div>
    <vue-json-pretty :data="config" />
  </MainCardContent>
</template>

<script setup lang="ts">
// Imports
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Fieldset from 'primevue/fieldset';
import ProgressSpinner from 'primevue/progressspinner';
import { storeToRefs } from 'pinia';
import { computed, onMounted } from 'vue';
import VueJsonPretty from 'vue-json-pretty';
import { useToast } from 'vue-toastification';
// Components
import { useConfigStore, useInnkeeperTenantsStore } from '@/store';
import MainCardContent from '../../layout/mainCard/MainCardContent.vue';
import PluginList from '@/components/about/PluginList.vue';

const toast = useToast();

const { config } = storeToRefs(useConfigStore());
const innkeeperTenantsStore = useInnkeeperTenantsStore();
const { loading, serverConfig } = storeToRefs(useInnkeeperTenantsStore());

onMounted(async () => {
  loadConfig();
});

const loadConfig = async () => {
  innkeeperTenantsStore.getServerConfig().catch((err: string) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};

const ledgerConfigList = computed(() => {
  if (serverConfig.value?.config) {
    return serverConfig.value.config['ledger.ledger_config_list'];
  }
  return [];
});

const swaggerUrl = computed(
  () => `${config.value.frontend.tenantProxyPath}/api/doc`
);
</script>

<style scoped></style>
