module.exports = {
  publicPath: process.env.NODE_ENV === 'production'
    ? './'
    : '/',

  transpileDependencies: [
    'vuetify'
  ]
};
