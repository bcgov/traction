<template>
    <div>
        <h1>Traction</h1>
        <PanelMenu :model="items" />
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PanelMenu from 'primevue/panelmenu';

const items = ref([
    {
        label: 'Dashboard',
        icon: 'pi pi-fw pi-chart-bar',
        to: { name: 'Dashboard' }
    },
    {
        label: 'Connections',
        icon: 'pi pi-fw pi-users',
        items: [
            {
                label: 'My Contacts',
                to: { name: 'MyContacts' }
            },
            {
                label: 'Accept Invitation',
                to: { name: 'AcceptInvitation' }
            }
        ]
    },

    {
        label: 'Issuance',
        icon: 'pi pi-fw pi-wallet',
        items: [
            {
                label: 'Schemas',
                to: { name: 'Schemas' }
            },
            {
                label: 'Offer A Credential',
                to: { name: 'OfferCredential' }
            },
            {
                label: 'My Issued Credentials',
                to: { name: 'MyIssuedCredentials' }
            },
        ]
    },

    {
        label: 'Verification',
        icon: 'pi pi-fw pi-check-square',
        items: [
            {
                label: 'My Presentations',
                to: { name: 'MyPresentations' }
            },
            {
                label: 'Create A Presentation Request',
                to: { name: 'CreatePresentation' }
            },
            {
                label: 'Presentation Templates',
                to: { name: 'PresentationTemplates' }
            },
        ]
    },

    {
        label: 'Holder',
        icon: 'pi pi-fw pi-key',
        items: [
            {
                label: 'My Held Credentials',
                to: { name: 'MyHeldCredentials' }
            },
            {
                label: 'Accept a Credential Offer',
                to: { name: 'AcceptCredential' }
            }
        ]
    },
]); 
</script>