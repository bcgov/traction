<template>
  <div class="surface-section">
    <div class="font-medium text-3xl text-900 mb-3">About</div>
    <div class="text-500 mb-5">
      Maybe we need some boilerplate text describing what this app is about?
    </div>
    <ul class="list-none p-0 m-0">
      <li
        class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap"
      >
        <div class="text-500 w-6 md:w-2 font-medium">Traction URL</div>
        <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
          {{ config.server.tractionUrl }}
        </div>
        <div class="w-6 md:w-2 flex justify-content-end">&nbsp;</div>
      </li>
      <li
        class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap"
      >
        <div class="text-500 w-6 md:w-2 font-medium">ACA-Py Admin URL</div>
        <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
          {{ config.server.acapyAdminUrl }}
        </div>
        <div class="w-6 md:w-2 flex justify-content-end">&nbsp;</div>
      </li>
      <li
        class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap"
      >
        <div class="text-500 w-6 md:w-2 font-medium">Image Tag</div>
        <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
          {{ config.image.tag }}
        </div>
        <div class="w-6 md:w-2 flex justify-content-end">&nbsp;</div>
      </li>
      <li
        class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap"
      >
        <div class="text-500 w-6 md:w-2 font-medium">Image Version</div>
        <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
          {{ config.image.version }}
        </div>
        <div class="w-6 md:w-2 flex justify-content-end">&nbsp;</div>
      </li>
      <li
        class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap"
      >
        <div class="text-500 w-6 md:w-2 font-medium">Image Created At</div>
        <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
          {{ config.image.buildtime }}
        </div>
        <div class="w-6 md:w-2 flex justify-content-end">&nbsp;</div>
      </li>
      <li
        class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap"
      >
        <div class="text-500 w-6 md:w-2 font-medium">Copyright</div>
        <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
          {{ config.frontend.ux.copyright }}
        </div>
        <div class="w-6 md:w-2 flex justify-content-end">&nbsp;</div>
      </li>
      <li
        class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap"
      >
        <div class="text-500 w-6 md:w-2 font-medium">Owner / Operator</div>
        <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
          {{ config.frontend.ux.owner }}
        </div>
        <div class="w-6 md:w-2 flex justify-content-end">&nbsp;</div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useConfigStore } from '../store/configStore';
const { config } = storeToRefs(useConfigStore());
</script>
