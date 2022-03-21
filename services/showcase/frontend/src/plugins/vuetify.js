import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';

Vue.use(Vuetify);

// Note below the "dark theme" is overloaded to be the optional "BC Gov" theme
// So it's not really "dark" and as such has been normalized to the same base as the light theme, see scss/variables.scss
export default new Vuetify({
  defaultAssets: {
    font: true,
    icons: 'md'
  },
  icons: {
    iconfont: 'md',
  },
  theme: {
    options: {
      customProperties: true
    },
    themes: {
      light: {
        primary: '#003366',
        secondary: '#FCBA19',
        anchor: '#1A5A96',
        accent: '#82B1FF',
        error: '#D8292F',
        info: '#2196F3',
        success: '#2E8540',
        warning: '#FFC107'
      },
      dark: {
        primary: '#003366',
        anchor: '#1A5A96',
      }
    }
  }
});

