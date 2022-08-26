<template>
    <Button icon="pi pi-id-card" class="p-button-text" @click="displayForm = true"
        v-tooltip.top="'Create Credential Template'" />
    <Dialog header="Create Credential Template" v-model:visible="displayForm">
        <CreateCredentialTemplateForm @form-close="displayForm = false;" :schema-template-id="schemaTemplateId" />
    </Dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import Dialog from "primevue/dialog";
import Button from "primevue/button";

import CreateCredentialTemplateForm from "./CreateCredentialTemplateForm.vue";


const props = defineProps({
    schemaTemplateId: {
        type: String,
        required: true
    }
});

const displayForm = ref(false);

</script>