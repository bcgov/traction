<template>
    <div class="traction-footer flex justify-content-between flex-wrap">
        <div>Home | Disclaimer | Privacy | Accessibility | Contact Us</div>
        <div>{{ config.ux.copyright }} | {{ config.ux.owner }}</div>
    </div>
</template>

<style>
.traction-footer {
    background-color: white !important;
    font-size: .7em;
    padding: 0 2em;
    border-top: 1px solid grey;
}
</style>
<script setup lang="ts">
import { inject } from "vue";
const config: any = inject("config");
</script>
