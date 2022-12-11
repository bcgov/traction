import { createWebHistory, createRouter } from 'vue-router';
// 404
import NotFound from '@/views/NotFound.vue';

// Routing sections
import innkeeperRoutes from './innkeeperRoutes';
import tenantRoutes from './tenantRoutes';

import { storeToRefs } from 'pinia';
import { useConfigStore } from '../store';

const routes = [
  { path: '/:pathMatch(.*)', component: NotFound },

  // Tenant Routes (base / is Tenant side for this app)
  ...tenantRoutes,

  // Innkeeper routes (base is /innkeeper)
  ...innkeeperRoutes,
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

/**
 * Global router guard to set the page title.
 * Override only if in the non-default tenant UI.
 * In this case, the innkeeper UI is the non-default.
 */
router.afterEach((to) => {
  // The Configuration Store also has to be loaded
  if (useConfigStore().config && to.meta.isInnkeeper === true) {
    const { config } = storeToRefs(useConfigStore());
    document.title = config.value.frontend.ux.appInnkeeperTitle;
  }
});

export default router;
