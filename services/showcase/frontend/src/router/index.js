import NProgress from 'nprogress';
import Vue from 'vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

/**
 * Constructs and returns a Vue Router object
 * @param {string} [basePath='/'] the base server path
 * @returns {object} a Vue Router object
 */
export default function getRouter(basePath = '/') {
  const router = new VueRouter({
    base: basePath,
    mode: 'history',
    routes: [
      {
        path: '/',
        redirect: { name: 'Home' }
      },
      {
        path: '/',
        name: 'Home',
        component: () => import(/* webpackChunkName: "home" */ '@/views/Home.vue'),
      },
      {
        path: '/innkeeper',
        name: 'Innkeeper',
        component: () => import(/* webpackChunkName: "innkeeper" */ '@/views/Innkeeper.vue'),
      },
      {
        path: '/faber',
        name: 'Faber',
        component: () => import(/* webpackChunkName: "faber" */ '@/views/Faber.vue'),
      },
      {
        path: '/alice',
        name: 'Alice',
        component: () => import(/* webpackChunkName: "alice" */ '@/views/Alice.vue'),
      },
      {
        path: '/acme',
        name: 'Acme',
        component: () => import(/* webpackChunkName: "acme" */ '@/views/Acme.vue'),
      },
      {
        path: '/404',
        alias: '*',
        name: 'NotFound',
        component: () => import(/* webpackChunkName: "not-found" */ '@/views/NotFound.vue'),
      }
    ]
  });

  router.beforeEach((to, _from, next) => {
    NProgress.start();
    next();
  });

  router.afterEach(() => {
    NProgress.done();
  });

  return router;
}
