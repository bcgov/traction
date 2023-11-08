<template>
  <MainCardContent
    :title="$t('serverConfig.serverConfig')"
    :refresh-callback="loadConfig"
  >
    <ProgressSpinner v-if="loading" />
    <div v-else>
      <p>
        <strong>ACA-Py Version:</strong> {{ serverConfig?.config?.version }}
      </p>

      <div class="grid mt-3">
        <div class="col">
          <Fieldset legend="Ledger Details" :toggleable="true">
            <p class="mt-0">Ledger List</p>
            <DataTable :value="ledgerConfigList" size="small" striped-rows>
              <Column field="id" header="id"></Column>
              <Column field="endorser_alias" header="endorser_alias"></Column>
              <Column field="endorser_did" header="endorser_did"></Column>
            </DataTable>
          </Fieldset>

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
          <Fieldset legend="Header" :toggleable="true">
            <p class="m-0">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
              enim ad minim veniam, quis nostrud exercitation ullamco laboris
              nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
              reprehenderit in voluptate velit esse cillum dolore eu fugiat
              nulla pariatur. Excepteur sint occaecat cupidatat non proident,
              sunt in culpa qui officia deserunt mollit anim id est laborum.
            </p>
          </Fieldset>

          <PluginList class="mt-4" />
        </div>
      </div>
    </div>
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
import { useInnkeeperTenantsStore } from '@/store';
import MainCardContent from '../../layout/mainCard/MainCardContent.vue';
import PluginList from '@/components/about/PluginList.vue';

const toast = useToast();

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

// computed list of the "ledger.ledger_config_list" array in serverConfig
const ledgerConfigList = computed(() => {
  if (serverConfig.value?.config) {
    return serverConfig.value.config['ledger.ledger_config_list'];
  }
  return [];
});
</script>

<style scoped></style>
