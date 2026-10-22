// 領域事件匯流排：業務模組只負責 emit，不需要知道誰在監聽
const { EventEmitter } = require('events');

const EVENTS = Object.freeze({
  USER_CREATED: 'user.created',
  ORDER_CREATED: 'order.created',
});

const bus = new EventEmitter();

module.exports = { bus, EVENTS };
