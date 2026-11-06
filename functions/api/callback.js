const SITE_ORIGIN = "https://autopet.store";
const CALLBACK_URL = `${SITE_ORIGIN}/api/callback`;

function popupResponse(message, status = 200) {
  const nonce = crypto.randomUUID().replaceAll("-", "");
  const serializedMessage = JSON.stringify(message).replaceAll("<", "\\u003c");
  const html = `<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>GitHub authorization</title></head>
  <body>
    <p>Finishing GitHub authorization. You can close this window if it does not close automatically.</p>
    <script nonce="${nonce}">
      const result = ${serializedMessage};
      window.addEventListener("load", () => {
        if (!window.opener) return;
        window.addEventListener("message", (event) => {
          if (event.source !== window.opener || event.origin !== ${JSON.stringify(SITE_ORIGIN)}) return;
          window.opener.postMessage(result, event.origin);
          window.close();
        });
        window.opener.postMessage("authorizing:github", "*");
      }, { once: true });
    </script>
  </body>
</html>`;

  return new Response(html, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "Content-Security-Policy": `default-src 'none'; script-src 'nonce-${nonce}'; base-uri 'none'; frame-ancestors 'none'`,
      "Content-Type": "text/html; charset=utf-8",
      "Referrer-Policy": "no-referrer",
      "Set-Cookie": "decap_oauth_state=; Path=/api/callback; HttpOnly; Secure; SameSite=Lax; Max-Age=0",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

function errorResponse(message, status = 400) {
  return popupResponse(`authorization:github:error:${JSON.stringify({ message })}`, status);
}

function getCookie(request, name) {
  const cookieHeader = request.headers.get("Cookie") ?? "";
  const cookie = cookieHeader.split(";").map((part) => part.trim()).find((part) => part.startsWith(`${name}=`));
  return cookie ? cookie.slice(name.length + 1) : null;
}

export async function onRequestGet({ request, env }) {
  if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) {
    return new Response("GitHub OAuth is not configured.", { status: 500 });
  }

  const url = new URL(request.url);
  const returnedState = url.searchParams.get("state");
  const savedState = getCookie(request, "decap_oauth_state");
  if (!returnedState || !savedState || returnedState !== savedState) {
    return errorResponse("GitHub authorization could not be verified.");
  }

  const authorizationError = url.searchParams.get("error");
  if (authorizationError) {
    return errorResponse(url.searchParams.get("error_description") || "GitHub authorization was cancelled.");
  }

  const code = url.searchParams.get("code");
  if (!code) {
    return errorResponse("GitHub did not return an authorization code.");
  }

  const tokenResponse = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      client_id: env.GITHUB_CLIENT_ID,
      client_secret: env.GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: CALLBACK_URL,
    }),
  });

  if (!tokenResponse.ok) {
    return errorResponse("GitHub could not complete authorization. Please try again.", 502);
  }

  const tokenResult = await tokenResponse.json();
  if (typeof tokenResult.access_token !== "string" || !tokenResult.access_token) {
    return errorResponse("GitHub did not return an access token.", 502);
  }

  const payload = JSON.stringify({ token: tokenResult.access_token, provider: "github" });
  return popupResponse(`authorization:github:success:${payload}`);
}
