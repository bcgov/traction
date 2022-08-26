<template>
  <h3 class="mt-0">PresentationDetails</h3>

    {{presentations}}

</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useToast } from 'vue-toastification';

import { useVerifierStore } from '../../store';
import { storeToRefs } from 'pinia';

const verifierStore = useVerifierStore();
const { loading, presentations, selectedPresentation } = storeToRefs(useVerifierStore());


onMounted(async () => {
  console.log("mounted")
  console.log(presentations)
});

</script>
