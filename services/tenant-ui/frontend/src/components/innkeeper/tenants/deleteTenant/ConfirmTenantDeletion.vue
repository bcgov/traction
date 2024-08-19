<template>
  <form @submit.prevent="handleDelete">
    <div class="modal-content">
      <h4>
        {{
          $t('tenants.settings.confirmDeletion', {
            tenantName: tenant.tenant_name,
          })
        }}
      </h4>
      <InputText
        v-model.trim="confirmationTenantName"
        type="text"
        placeholder="Type the tenant name here"
        class="w-full mb-4"
      />
      <div>
        <div class="flex items-center">
          <RadioButton v-model="perminant" value="Hard" />
          <label class="ml-2" for="">
            {{ $t('tenants.settings.permanentDelete') }}
          </label>
        </div>
        <div v-if="!props.unsuspendable" class="flex items-center my-2">
          <RadioButton v-model="perminant" value="Soft" />
          <label class="ml-2" for="">
            {{ $t('tenants.settings.softDelete') }}
          </label>
        </div>
      </div>
      <div v-if="displayWarning" class="ml-2 my-2 flex flex-row">
        <i class="pi pi-info-circle mr-2"></i>
        <div class="text-yellow-500 flex flex-row font-bold">
          <div class="font-bold">{{ $t('common.warning') }}</div>
          <div class="font-semibold">
            {{ $t('tenants.settings.tenantDeletionWarning') }}
          </div>
        </div>
      </div>
      <Button
        :disabled="!isTenantNameCorrect"
        label="Delete"
        severity="danger"
        class="w-full my-2"
        type="submit"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, Ref } from 'vue';

import InputText from 'primevue/inputtext';
import RadioButton from 'primevue/radiobutton';
import Button from 'primevue/button';

import { useInnkeeperTenantsStore } from '@/store';
import { TenantRecord } from '@/types/acapyApi/acapyInterface';
import { useTenantStore } from '@/store';

import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
const { t } = useI18n();

type DeletionAPI = 'Innkeeper' | 'Tenant';
const props = defineProps<{
  tenant: TenantRecord;
  api: DeletionAPI;
  unsuspendable?: boolean;
}>();

const emit = defineEmits(['closed', 'success']);

// Using stores
const innkeeperTenantsStore = useInnkeeperTenantsStore();

const confirmationTenantName = ref('');
const isTenantNameCorrect = computed(
  () => confirmationTenantName.value === props.tenant.tenant_name
);
const displayWarning = computed(() => {
  if (perminant.value == 'Hard') return true;
  else return false;
});

const toast = useToast();

type DeletionType = 'Hard' | 'Soft';
const perminant: Ref<DeletionType> = ref(props.unsuspendable ? 'Hard' : 'Soft');

const tenantDelete = async () => {
  const tenantStore = useTenantStore();
  if (perminant.value == 'Hard') {
    tenantStore.deleteTenant();
    window.location.href = '/logout';
  } else {
    tenantStore.softDeleteTenant();
    window.location.href = '/logout';
  }
};
const innkeeperDelete = async () => {
  if (perminant.value == 'Hard') {
    await innkeeperTenantsStore.hardDeleteTenant(props.tenant.tenant_id);
  } else {
    await innkeeperTenantsStore.deleteTenant(props.tenant.tenant_id);
  }
};

async function handleDelete() {
  if (!isTenantNameCorrect.value) {
    toast.error(t('tenants.settings.confirmDeletionIncorrect'));
    return;
  }
  try {
    if (props.api == 'Tenant') {
      await tenantDelete();
    } else {
      await innkeeperDelete();
    }
    toast.success(
      t('tenants.settings.confirmDeletionSuccess', [
        props.tenant.tenant_name,
        t(
          perminant.value == 'Hard'
            ? 'tenants.settings.deleted'
            : 'tenants.settings.suspended'
        ),
      ])
    );
    emit('success');
    emit('closed');
  } catch (err: any) {
    console.error(err);
    toast.error('Failure: ${err}');
  }
}
</script>
