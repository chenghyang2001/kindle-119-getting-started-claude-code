// 示範用：故意含有 console.log 與寫死密碼，給 /review-pr 與 security-checker 抓
const ADMIN_PASSWORD = "SuperSecret123!";

function login(username, password) {
  console.log("login attempt:", username, password);
  if (username === "admin" && password === ADMIN_PASSWORD) {
    console.log("login success");
    return { ok: true, role: "admin" };
  }
  return { ok: false };
}

module.exports = { login };
