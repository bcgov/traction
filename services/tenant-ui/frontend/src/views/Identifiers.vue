<template>
  <MainCardContent
    :title="$t('identifiers.identifiers')"
    :refresh-callback="refreshWebvh"
  >
    <div v-if="pageLoading" class="flex justify-content-center">
      <ProgressSpinner />
    </div>
    <template v-else>
      <DataTable
        v-if="isAnoncredsWallet"
        v-model:filters="didTableFilters"
        :value="webvhDidRows"
        :paginator="true"
        :rows="TABLE_OPT.ROWS_DEFAULT"
        :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
        :global-filter-fields="['alias', 'namespace', 'did', 'status']"
        data-key="did"
        size="small"
        striped-rows
        sort-field="alias"
        :loading="refreshingWebvh || !webvhConfigLoaded"
        removable-sort
      >
        <template #header>
          <div class="table-header">
            <div class="left">
              <Button
                type="button"
                icon="pi pi-plus"
                :label="$t('identifiers.webvh.createButton')"
                class="p-button"
                @click="openCreateDialog"
              />
            </div>
            <IconField icon-position="left" class="search-field">
              <InputIcon><i class="pi pi-search" /></InputIcon>
              <InputText
                v-model="didTableFilters.global.value"
                :placeholder="$t('identifiers.webvh.searchPlaceholder')"
              />
            </IconField>
          </div>
        </template>
        <template #empty>{{ $t('common.noRecordsFound') }}</template>
        <template #loading>{{ $t('common.loading') }}</template>
        <Column
          field="namespace"
          :header="$t('identifiers.webvh.namespace')"
          sortable
        />
        <Column
          field="alias"
          :header="$t('identifiers.webvh.alias')"
          sortable
        />
        <Column
          field="status"
          :header="$t('identifiers.webvh.statusHeader')"
          sortable
        >
          <template #body="{ data }">
            <span :class="['status-chip', data.status]">
              {{ statusLabel(data.status) }}
            </span>
          </template>
        </Column>
        <Column
          field="created"
          :header="$t('identifiers.webvh.createdAt')"
          sortable
        />
        <Column field="did" :header="$t('identifiers.webvh.didHeader')">
          <template #body="{ data }">
            <code>{{ data.did }}</code>
          </template>
        </Column>
      </DataTable>
      <Message
        v-else
        :closable="false"
        severity="warn"
        class="wallet-type-warning"
      >
        {{ $t('identifiers.requiresAnoncredsWallet') }}
      </Message>

      <Dialog
        v-model:visible="showCreateDidDialog"
        modal
        :header="$t('identifiers.webvh.createDialogTitle')"
        :style="{ width: '32rem' }"
        @hide="resetCreateForm"
      >
        <div class="dialog-content">
          <div class="field">
            <label for="dialog-alias" class="required-label">
              {{ $t('identifiers.webvh.alias') }}
            </label>
            <InputText
              id="dialog-alias"
              v-model.trim="newDidAlias"
              autocomplete="off"
              :class="{ 'p-invalid': createFormTouched && !newDidAlias }"
            />
            <small v-if="createFormTouched && !newDidAlias" class="p-error">
              {{ $t('identifiers.webvh.aliasRequired') }}
            </small>
          </div>
          <div class="field">
            <label for="dialog-namespace">{{
              $t('identifiers.webvh.namespace')
            }}</label>
            <InputText
              id="dialog-namespace"
              v-model.trim="newDidNamespace"
              autocomplete="off"
            />
          </div>
        </div>
        <template #footer>
          <Button
            type="button"
            class="p-button-text"
            :disabled="creatingDid"
            :label="$t('common.cancel')"
            @click="closeCreateDialog"
          />
          <Button
            type="button"
            icon="pi pi-plus"
            :disabled="!canCreateDid"
            :loading="creatingDid"
            :label="$t('identifiers.webvh.createButton')"
            @click="submitCreateDid"
          />
        </template>
      </Dialog>
    </template>
  </MainCardContent>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import Dialog from 'primevue/dialog';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
import { useAcapyApi } from '@/store/acapyApi';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import Message from 'primevue/message';

const toast = useToast();
const { t } = useI18n();
const tenantStore = useTenantStore();
const acapyApi = useAcapyApi();
const { tenantWallet, loading, serverConfig } = storeToRefs(tenantStore);
const creatingDid = ref(false);
const refreshingWebvh = ref(false);
const showCreateDidDialog = ref(false);
const createFormTouched = ref(false);
const newDidAlias = ref('');
const newDidNamespace = ref('default');
const webvhConfigData = ref<any | null>(null);
const webvhConfigLoaded = ref(false);
const didTableFilters = ref({
  global: { value: '', matchMode: FilterMatchMode.CONTAINS },
});

const serverWebvhConfig = computed<any | null>(() => {
  const cfg: any = serverConfig.value;
  if (!cfg || typeof cfg !== 'object' || !('config' in cfg)) {
    return null;
  }
  const pluginConfig = cfg.config?.plugin_config ?? {};
  return pluginConfig['did-webvh'] || pluginConfig.webvh || null;
});

const pageLoading = computed(() => {
  if (!isAnoncredsWallet.value) {
    return loading.value;
  }
  if (loading.value) {
    return true;
  }
  if (webvhConfigData.value) {
    return false;
  }
  if (webvhConfigLoaded.value) {
    return false;
  }
  if ('config' in (serverConfig.value ?? {})) {
    return false;
  }
  return true;
});

const isAnoncredsWallet = computed(() => {
  const walletType = tenantWallet.value?.settings?.['wallet.type'];
  return walletType === 'askar-anoncreds';
});

const webvhConfig = computed<any | null>(() => {
  const override = webvhConfigData.value;
  const base = serverWebvhConfig.value;
  if (!override || Object.keys(override).length === 0) {
    return base ?? override ?? null;
  }
  if (!base) {
    return override;
  }
  return {
    ...base,
    ...override,
  };
});

const webvhServerUrl = computed(() => webvhConfig.value?.server_url ?? '');

const webvhWatchers = computed(() => {
  if (!webvhConfig.value) return [] as string[];
  const watchers = webvhConfig.value.watchers ?? [];
  return Array.isArray(watchers) ? watchers : [];
});

const webvhDidRows = computed(() => {
  const scids = webvhConfig.value?.scids;
  if (!scids || typeof scids !== 'object') {
    return [] as Array<{
      scid: string;
      did: string;
      alias: string;
      namespace: string;
      status: string;
      created: string;
    }>;
  }
  const entries = Object.entries(scids as Record<string, string>);
  return entries.map(([scid, did]) => {
    const segments = (did as string).split(':');
    const alias = segments[segments.length - 1] ?? did;
    const namespace =
      segments.length > 2 ? segments[segments.length - 2] : 'default';
    return {
      scid,
      did,
      alias,
      namespace,
      status: 'active',
      created: '—',
    };
  });
});

const statusLabel = (_status: string) =>
  t('identifiers.webvh.statusActive') as string;

const canCreateDid = computed(
  () =>
    isAnoncredsWallet.value &&
    newDidAlias.value.trim().length > 0 &&
    !creatingDid.value
);

const openCreateDialog = () => {
  if (!isAnoncredsWallet.value) {
    return;
  }
  createFormTouched.value = false;
  if (!newDidNamespace.value) {
    newDidNamespace.value = 'default';
  }
  showCreateDidDialog.value = true;
};

const closeCreateDialog = () => {
  showCreateDidDialog.value = false;
};

const resetCreateForm = () => {
  newDidAlias.value = '';
  newDidNamespace.value = 'default';
  createFormTouched.value = false;
};

const submitCreateDid = async () => {
  createFormTouched.value = true;
  if (!newDidAlias.value.trim()) {
    return;
  }
  await createDid();
};

const loadWebvhConfig = async () => {
  if (!isAnoncredsWallet.value) {
    webvhConfigData.value = null;
    webvhConfigLoaded.value = true;
    return;
  }
  webvhConfigLoaded.value = false;
  try {
    const response = await acapyApi.getHttp(API_PATH.DID_WEBVH_CONFIG);
    const configData = response?.data ?? response ?? null;
    const isEmptyConfig =
      !configData ||
      (typeof configData === 'object' && Object.keys(configData).length === 0);
    webvhConfigData.value = isEmptyConfig ? null : configData;
  } catch (_error) {
    webvhConfigData.value = null;
  } finally {
    webvhConfigLoaded.value = true;
  }
};

const refreshWebvh = async () => {
  if (refreshingWebvh.value) {
    return;
  }
  refreshingWebvh.value = true;
  try {
    await tenantStore.getServerConfig();
    await loadWebvhConfig();
  } finally {
    refreshingWebvh.value = false;
  }
};

const createDid = async () => {
  creatingDid.value = true;
  try {
    const alias = newDidAlias.value.trim();
    const namespace = newDidNamespace.value.trim() || 'default';

    const options: Record<string, any> = {
      identifier: alias,
      namespace,
    };
    if (webvhServerUrl.value) {
      options.server_url = webvhServerUrl.value;
    }
    if (webvhWatchers.value.length) {
      options.watchers = webvhWatchers.value;
    }

    const response = await acapyApi.postHttp(API_PATH.DID_WEBVH_CREATE, {
      options,
    });

    const newDid = response?.data?.did ?? response?.data?.did_document?.id;
    toast.success(
      newDid
        ? t('identifiers.webvh.createSuccessWithDid', { did: newDid })
        : t('identifiers.webvh.createSuccess')
    );
    resetCreateForm();
    showCreateDidDialog.value = false;
    await tenantStore.getServerConfig();
    await loadWebvhConfig();
  } catch (error: any) {
    toast.error(
      `Failed to create DID: ${
        error?.response?.data?.message ??
        JSON.stringify(error?.response?.data ?? error)
      }`
    );
  } finally {
    creatingDid.value = false;
  }
};

onMounted(async () => {
  const tasks: Promise<any>[] = [];
  if (!tenantWallet.value) {
    tasks.push(tenantStore.getTenantSubWallet());
  }
  if (!('config' in (serverConfig.value ?? {}))) {
    tasks.push(tenantStore.getServerConfig());
  }
  if (tasks.length) {
    await Promise.allSettled(tasks);
  }
  if (isAnoncredsWallet.value) {
    await loadWebvhConfig();
  }
});
</script>

<style scoped lang="scss">
.wallet-type-check {
  padding: 1rem 0;
}

.webvh-section {
  display: flex;
  flex-direction: column;
}

.webvh-row {
  display: flex;
  margin-bottom: 0.75rem;

  .label {
    min-width: 9rem;
    font-weight: 600;
  }

  .value {
    flex: 1;
    word-break: break-word;
  }

  .icon {
    display: inline-flex;
    align-items: center;
  }
}

.create-form {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;

  .field {
    min-width: 14rem;
  }
}

.status-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.85rem;
  text-transform: capitalize;

  &.pending {
    background: rgba(255, 193, 7, 0.2);
    color: #8a6d1a;
  }

  &.active {
    background: rgba(76, 175, 80, 0.2);
    color: #1b5e20;
  }

  &.error {
    background: rgba(244, 67, 54, 0.2);
    color: #b71c1c;
  }
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;

  .left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .search-field {
    flex: 1;
    max-width: 18rem;
  }
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.required-label::after {
  content: ' *';
  color: $tenant-ui-text-danger;
}

.wallet-type-warning {
  margin-top: 1rem;
}
</style>
