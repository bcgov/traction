const _paq = ((window as any)._paq = (window as any)._paq || []);
_paq.push(['trackPageView']);
_paq.push(['enableLinkTracking']);
function setup(MATOMO_URL: string) {
  const u = `//${MATOMO_URL}/`;
  _paq.push(['setTrackerUrl', u + 'matomo.php']);
  _paq.push(['setSiteId', 1]);
  const d = document,
    g = d.createElement('script'),
    s: any = d.getElementsByTagName('script')[0];
  g.type = 'text/javascript';
  g.async = true;
  g.src = u + 'matomo.js';
  s.parentNode.insertBefore(g, s);
}
export { setup };
