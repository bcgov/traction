import axios from 'axios';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useConfigStore } from '../configStore';
import {
  UserManager,
  WebStorageStateStore,
  User,
  UserManagerEvents,
} from 'oidc-client-ts';

export const useInnkeeperOidcStore = defineStore('innkeeperOidcStore', () => {
  // private (move to other file maybe?)
  let _userManager: UserManager;
  const _settings: any = {
    authority: 'https://dev.loginproxy.gov.bc.ca/auth/realms/digitaltrust-nrm',
    client_id: 'vue3-frontend-local',
    redirect_uri: 'http://localhost:5173/innkeeper',
    response_type: 'code',
    automaticSilentRenew: true,
    post_logout_redirect_uri: 'localhost',
    loadUserInfo: true,
  };
  _userManager = new UserManager(_settings);

  async function login() {
    return _userManager.signinRedirect();
  }

  _userManager
    .signinRedirectCallback()
    .then(function (user) {
      console.log('signed in', user);
    })
    .catch(function (err) {
      console.error(err);
      console.log(err);
    });

  _userManager.events.addUserLoaded(() => {
    console.log('USER LOADED');
    debugger;
    _userManager.getUser().then((usr) => {
      console.log('USER LOADED');
      user.value = usr;
      axios
      .get('/api/innkeeperLogin')
      .then((res) => {
        console.log(res);
        debugger;
        alert(JSON.stringify(res.data));
      })
    });
  });

  // state
  const token: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);
  const user: any = ref(null);

  // getters
  const innkeeperReady = computed(() => {
    return token.value != null;
  });

  // actions

  return {
    token,
    loading,
    error,
    innkeeperReady,
    login,
    user
  };
});

export default {
  useInnkeeperOidcStore,
};
