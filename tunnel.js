const localtunnel = require('localtunnel');

(async () => {
  try {
    console.log('Requesting localtunnel...');
    const tunnel = await localtunnel({ port: 3000 });
    console.log('>>> READY_PUBLIC_LINK:', tunnel.url);
    tunnel.on('close', () => {
      console.log('Tunnel closed.');
    });
  } catch (err) {
    console.error('Tunnel error:', err);
  }
})();
