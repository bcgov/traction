<template>
    <div>
        <Toast />

        <h5>Inline</h5>
        <Menu :model="items" />

        <h5>Overlay</h5>
        <Button type="button" label="Toggle" @click="toggle" aria-haspopup="true" aria-controls="overlay_menu" />
        <Menu id="overlay_menu" ref="menu" :model="items" :popup="true" />
    </div>
</template>

<script>
import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';

export default {
    setup() {
        const toast = useToast();
        const menu = ref();
        const items = ref([
            {
                label: 'Options',
                items: [{
                    label: 'Update',
                    icon: 'pi pi-refresh',
                    command: () => {
                        toast.add({ severity: 'success', summary: 'Updated', detail: 'Data Updated', life: 3000 });
                    }
                },
                {
                    label: 'Delete',
                    icon: 'pi pi-times',
                    command: () => {
                        toast.add({ severity: 'warn', summary: 'Delete', detail: 'Data Deleted', life: 3000 });
                    }
                }
                ]
            },
            {
                label: 'Navigate',
                items: [{
                    label: 'Vue Website',
                    icon: 'pi pi-external-link',
                    url: 'https://vuejs.org/'
                },
                {
                    label: 'Router',
                    icon: 'pi pi-upload',
                    command: () => {
                        window.location.hash = "/fileupload"
                    }
                }
                ]
            }
        ]);

        const toggle = (event) => {
            menu.value.toggle(event);
        };
        const save = () => {
            toast.add({ severity: 'success', summary: 'Success', detail: 'Data Saved', life: 3000 });
        };

        return { items, menu, toggle, save }
    }
}
</script>