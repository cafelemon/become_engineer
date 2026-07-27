type Identity = { user_id: string; csrf_token: string };

const restoring = document.querySelector<HTMLElement>("#restoring")!;
const loginForm = document.querySelector<HTMLFormElement>("#login")!;
const dashboard = document.querySelector<HTMLElement>("#dashboard")!;
const identity = document.querySelector<HTMLElement>("#identity")!;
const result = document.querySelector<HTMLElement>("#result")!;
const loginError = document.querySelector<HTMLElement>("#login-error")!;
let csrf = "";

function showAnonymous(message = ""): void {
  csrf = "";
  restoring.hidden = true;
  dashboard.hidden = true;
  loginForm.hidden = false;
  loginError.hidden = message.length === 0;
  loginError.textContent = message;
  if (message) loginError.focus();
}

function showReady(data: Identity): void {
  csrf = data.csrf_token;
  restoring.hidden = true;
  loginForm.hidden = true;
  dashboard.hidden = false;
  identity.textContent = `当前主体：${data.user_id}`;
}

async function restore(): Promise<void> {
  const response = await fetch("/api/me");
  if (response.status === 401) return showAnonymous();
  if (!response.ok) return showAnonymous("身份服务暂时不可用");
  showReady(await response.json() as Identity);
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(loginForm);
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: form.get("username"), password: form.get("password") }),
  });
  if (response.status === 401) return showAnonymous("用户名或密码错误");
  if (!response.ok) return showAnonymous("登录服务暂时不可用");
  showReady(await response.json() as Identity);
});

document.querySelector<HTMLButtonElement>("#save")!.addEventListener("click", async () => {
  const note = document.querySelector<HTMLInputElement>("#note")!.value;
  const response = await fetch("/api/study", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify({ note }),
  });
  result.textContent = response.ok ? `已保存：${note}` : `保存失败：${response.status}`;
});

document.querySelector<HTMLButtonElement>("#diagnostic")!.addEventListener("click", async () => {
  const response = await fetch("/api/operator/diagnostic", { method: "POST", headers: { "X-CSRF-Token": csrf } });
  result.textContent = response.status === 403 ? "权限不足：诊断仅对操作员开放" : `诊断结果：${response.status}`;
});

document.querySelector<HTMLButtonElement>("#logout")!.addEventListener("click", async () => {
  const response = await fetch("/api/auth/logout", { method: "POST", headers: { "X-CSRF-Token": csrf } });
  if (response.status === 204) showAnonymous();
});

void restore();
