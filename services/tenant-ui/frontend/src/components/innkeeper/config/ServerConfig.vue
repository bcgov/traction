<template>
  <MainCardContent
    :title="$t('serverConfig.serverConfig')"
    :refresh-callback="loadConfig"
  >
    <ProgressSpinner v-if="loading" />
    <div v-else>
      <!-- Topline version info -->
      <p>
        <strong>{{ $t('serverConfig.acapyVersion') }}</strong>
        {{ serverConfig?.config?.version }}
      </p>
      <p>
        <strong>{{ $t('serverConfig.tractionProxy') }}</strong>
        {{ config.frontend.tenantProxyPath }}
        <a :href="swaggerUrl" target="_blank">
          <i class="pi pi-external-link ml-2" />
        </a>
      </p>

      <div class="grid mt-3">
        <div class="col">
          <!-- Traction cfg - ledger -->
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

          <!-- Traction cfg - storage -->
          <Fieldset
            class="mt-4"
            :legend="$t('serverConfig.storage.title')"
            :toggleable="true"
          >
            <p class="mt-0">
              <strong>{{
                $t('serverConfig.storage.walletStorageConfig')
              }}</strong>
              {{ serverConfig?.config?.['wallet.storage_config'] }}
            </p>
            <p>
              <strong>{{
                $t('serverConfig.storage.walletStorageType')
              }}</strong>
              {{ serverConfig?.config?.['wallet.storage_type'] }}
            </p>
            <p>
              <strong>{{ $t('serverConfig.storage.walletType') }}</strong>
              {{ serverConfig?.config?.['wallet.type'] }}
            </p>
          </Fieldset>

          <!-- Plugins from API call to get them -->
          <PluginList class="mt-4" />

          <!-- Traction cfg - raw json -->
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
          <!-- Details about tenants/reservations -->
          <Fieldset
            :legend="$t('serverConfig.tenants.title')"
            :toggleable="true"
          >
            <p class="mt-0">
              <strong>{{ $t('serverConfig.tenants.token') }}</strong>
              {{
                serverConfig?.config?.plugin_config?.multitenant_provider
                  ?.token_expiry?.amount
              }}
              {{
                serverConfig?.config?.plugin_config?.multitenant_provider
                  ?.token_expiry?.units
              }}
            </p>
            <h3>{{ $t('serverConfig.tenants.reservation') }}</h3>
            <p>
              <strong>{{
                $t('serverConfig.tenants.reservationExpiry')
              }}</strong>
              {{
                serverConfig?.config?.plugin_config?.traction_innkeeper
                  ?.reservation?.expiry_minutes
              }}
            </p>
            <p>
              <strong>{{
                $t('serverConfig.tenants.reservationAutoApprove')
              }}</strong>
              {{
                serverConfig?.config?.plugin_config?.traction_innkeeper
                  ?.reservation?.auto_approve
              }}
            </p>
            <p>
              <strong>{{
                $t('serverConfig.tenants.reservationAutoIssuer')
              }}</strong>
              {{
                serverConfig?.config?.plugin_config?.traction_innkeeper
                  ?.reservation?.auto_issuer
              }}
            </p>
            <p class="">
              <strong>{{ $t('serverConfig.tenants.reservationOidc') }}</strong>
              {{ config.frontend.showOIDCReservationLogin }}
            </p>
            <div class="grid mt-0">
              <div class="col xl:col-8">
                <Accordion>
                  <AccordionTab
                    :header="$t('serverConfig.tenants.reservationForm')"
                  >
                    <div v-if="loading" class="flex justify-content-center">
                      <ProgressSpinner />
                    </div>
                    <vue-json-pretty v-else :data="resFormData" />
                  </AccordionTab>
                </Accordion>
              </div>
            </div>
          </Fieldset>

          <!-- Specific Tenant UI cfg fields -->
          <Fieldset
            class="mt-4"
            :legend="$t('serverConfig.tenantUi.tenantUi')"
            :toggleable="true"
          >
            <p class="mt-0">
              <strong>{{ $t('serverConfig.tenantUi.showWrite') }}</strong>
              {{ config.frontend.showWritableComponents }}
            </p>
            <p>
              <strong>{{ $t('serverConfig.tenantUi.sessionExpiry') }}</strong>
              {{
                $t('serverConfig.tenantUi.sessionExpiryVal', [
                  config.frontend.session?.timeoutSeconds,
                  config.frontend.session?.countdownSeconds,
                ])
              }}
            </p>
            <p>
              <strong>{{ $t('serverConfig.tenantUi.oidc') }}</strong>
              {{ config.frontend.oidc?.authority }}
            </p>
          </Fieldset>

          <!-- Tenant UI config endpoint raw json -->
          <Accordion class="mt-4">
            <AccordionTab :header="$t('serverConfig.tenantUi.expand')">
              <div v-if="loading" class="flex justify-content-center">
                <ProgressSpinner />
              </div>
              <vue-json-pretty v-else :data="config" />
            </AccordionTab>
          </Accordion>
        </div>
      </div>
    </div>
  </MainCardContent>
</template>

<script setup lang="ts">
// Imports
import axios from 'axios';
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

let resFormData: any;

const loadConfig = async () => {
  innkeeperTenantsStore.getServerConfig().catch((err: string) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });

  // use axios to get forms/reservation.json from the root url
  const response = await axios.get('/forms/reservation.json');
  resFormData = response.data;
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
