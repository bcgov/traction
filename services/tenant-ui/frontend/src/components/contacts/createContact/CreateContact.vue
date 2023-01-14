<template>
  <div>
    <Button
      :label="
        props.multi
          ? t('connect.invitations.multi')
          : t('connect.invitations.single')
      "
      icon="pi pi-user-edit"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="
        props.multi
          ? t('connect.invitations.multiCreate')
          : t('connect.invitations.singleCreate')
      "
      :modal="true"
      :style="{ minWidth: '400px' }"
      @update:visible="handleClose"
    >
      <CreateContactForm
        :multi="props.multi"
        @success="$emit('success')"
        @closed="handleClose"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref, PropType } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useI18n } from 'vue-i18n';
// Custom Components
import CreateContactForm from './CreateContactForm.vue';

const { t } = useI18n();

defineEmits(['success']);

// Props
const props = defineProps({
  multi: {
    type: Boolean as PropType<boolean>,
    required: true,
  },
});

// Display popup
const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs (if needed)
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
</script>
