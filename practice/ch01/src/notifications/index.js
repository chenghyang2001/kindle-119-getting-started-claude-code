const { bus, EVENTS } = require('../shared/events');
const { buildMessage } = require('./templates');
const consoleChannel = require('./channels/console.channel');

const SUBSCRIBED_EVENTS = [EVENTS.USER_CREATED, EVENTS.ORDER_CREATED];
const listeners = new Map();
const sentLog = [];

// 通知失敗只記錄，不往外拋——建單成功不能因為寄信失敗而變成失敗
async function deliver(channel, eventName, payload) {
  try {
    const message = buildMessage(eventName, payload);
    if (message === null) return;
    const result = await channel.send(message);
    sentLog.push({ eventName, message, result });
  } catch (err) {
    console.error(`[notify] ${eventName} 通知失敗：${err.message}`);
    sentLog.push({ eventName, error: err.message });
  }
}

function unregisterNotifications() {
  for (const [eventName, listener] of listeners) bus.off(eventName, listener);
  listeners.clear();
}

// 冪等：重複呼叫（例如測試多次 createApp）不會重複通知
function registerNotifications({ channel = consoleChannel } = {}) {
  unregisterNotifications();
  for (const eventName of SUBSCRIBED_EVENTS) {
    const listener = (payload) => { deliver(channel, eventName, payload); };
    bus.on(eventName, listener);
    listeners.set(eventName, listener);
  }
}

function getSentLog() {
  return [...sentLog];
}

module.exports = { registerNotifications, unregisterNotifications, getSentLog };
