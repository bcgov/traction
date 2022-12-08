import { createWebHistory, createRouter } from 'vue-router';
// 404
import NotFound from '@/views/NotFound.vue';

// Routing sections
import innkeeperRoutes from './innkeeperRoutes';
import tenantRoutes from './tenantRoutes';

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
 * TBD: Could move this into a Helm chart value.
 */
router.afterEach((to) => {
  if (to.meta.isInnkeeper === true) {
    document.title = 'Traction Innkeeper Console';
  }
});

export default router;
