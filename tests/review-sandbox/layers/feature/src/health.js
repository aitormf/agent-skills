'use strict';

function healthRoute(res) {
  res.setHeader('content-type', 'application/json');
  return res.end(JSON.stringify({ status: 'ok' }));
}

module.exports = { healthRoute };
