<template>
  <h3 class="mt-0">PresentationDetails</h3>
    <div>
        <ul>
        <li>Status: {{props.presentation.status}}</li>
        <li>Updated at: {{props.presentation.updated_at}}</li>
        <li>Contact Alias: {{props.presentation.contact.alias}}</li>
        <li>Aca-py: {{props.presentation.acapy}}</li>
        </ul>
    </div>
    {{props.presentation}}
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useToast } from 'vue-toastification';


onMounted(async () => {
  console.log("mounted")
});

const props = defineProps({
    presentation: {
        type: Object,
        required: true
    }
});

</script>

