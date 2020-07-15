import { check, sleep } from "k6";
import http from "k6/http";
import { deleteToken, login, options as baseOptions, URLS } from "./index.ts";

export const options = Object.assign({}, baseOptions, {
  stages: [
    { duration: "5s", target: 2 },
    // { duration: "30s", target: 20 },
    // { duration: "1m30s", target: 10 },
    // { duration: "20s", target: 0 },
  ],
});

export default function () {
  const loginRes = login();

  check(loginRes, {
    "logged in successfully": (r) => {
      return r.status === 201;
    },
  });

  const loginToken = loginRes.json("token");

  const tokenResponse = http.get(URLS.TOKENS + "/" + loginToken);

  const tokenBody = tokenResponse.json("user");

  check(tokenBody, { "verified token": (user) => typeof user === "number" });

  deleteToken(URLS.TOKENS + "/" + loginToken);

  sleep(1);
}
