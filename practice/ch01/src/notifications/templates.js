const { EVENTS } = require('../shared/events');

// 純函式：事件 → 訊息；不認得的事件回傳 null（不通知）
function buildMessage(eventName, payload) {
  if (eventName === EVENTS.USER_CREATED) {
    return {
      to: payload.email,
      subject: '歡迎加入！',
      body: `${payload.name} 您好，您的帳號已建立。`,
    };
  }
  if (eventName === EVENTS.ORDER_CREATED) {
    const { order, user } = payload;
    return {
      to: user.email,
      subject: `訂單 #${order.id} 已成立`,
      body: `${user.name} 您好，您的訂單金額為 ${order.total}。`,
    };
  }
  return null;
}

module.exports = { buildMessage };
