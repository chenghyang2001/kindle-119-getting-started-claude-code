// console 管道：demo 用。未來 SendGrid 管道只要提供相同的 send(message) 介面
async function send(message) {
  console.log(`[notify:console] to=${message.to} | ${message.subject} | ${message.body}`);
  return { ok: true, channel: 'console' };
}

module.exports = { name: 'console', send };
