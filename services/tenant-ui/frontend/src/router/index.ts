import { createWebHistory, createRouter } from 'vue-router';
// 404
import NotFound from '@/views/NotFound.vue';

// Routing sections
import innkeeperRoutes from './innkeeperRoutes';
import tenantRoutes from './tenantRoutes';

import { storeToRefs } from 'pinia';
import {
  useConfigStore,
  useTenantStore,
  useTokenStore,
  useInnkeeperTokenStore,
} from '../store';

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

/**
 * Global router middleware for logout and refresh handling.
 */
router.beforeEach((to, from, next) => {
  const logoutPath = getLogoutPath(to);
  if (logoutPath) return next(logoutPath);
  else resetLoginDataOnRefresh(to.path, from.path);
  next();
});

const getLogoutPath = (to: any) => {
  if (to.path === '/logout') {
    removeLoginData();
    return '/';
  }
  if (to.path === '/innkeeper/logout') {
    removeInnkeeperLoginData();
    return '/innkeeper';
  }
};

const resetLoginDataOnRefresh = (toPath: string, fromPath: string) => {
  if (fromPath !== '/' && fromPath !== '/innkeeper') return;
  if (toPath.includes('/innkeeper')) {
    const innkeeperToken = localStorage.getItem('innkeeper-token');
    if (innkeeperToken) useInnkeeperTokenStore().setToken(innkeeperToken);
  } else {
    const token = localStorage.getItem('token');
    if (token) setLocalStorage(token);
  }
};

const removeLoginData = () => {
  useTokenStore().clearToken();
  useTenantStore().clearTenant();
};

const removeInnkeeperLoginData = () => {
  useInnkeeperTokenStore().clearToken();
};

const setLocalStorage = (token: string) => {
  useTokenStore().setToken(token);
  useTenantStore().setTenantLoginDataFromLocalStorage();
};

export default router;
