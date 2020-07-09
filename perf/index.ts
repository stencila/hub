// To run:
// 1. install k6 (https://k6.io/docs/getting-started/installation)
// 2. Run a local instance of the Hub
// 3. run in terminal `k6 run -e USERNAME=username -e PASSWORD=password perf/index.ts`

import { check, sleep } from "k6";
import http from "k6/http";
import { Rate } from "k6/metrics";

const CONFIG = {
  URL: __ENV.HUB || "http://127.0.0.1",
  PORT: __ENV.PORT || 8000,
  USERNAME: __ENV.USERNAME,
  PASSWORD: __ENV.PASSWORD,
};

const makeApi = (apiPath) => CONFIG.URL + ":" + CONFIG.PORT + "/api" + apiPath;

const URLS = {
  BASE_URL: CONFIG.URL + ":" + CONFIG.PORT,
  TOKENS: makeApi("/tokens"),
};

export let errorRate = new Rate("errors");

export const options = {
  stages: [
    // { duration: "5s", target: 2 },
    { duration: "30s", target: 20 },
    { duration: "1m30s", target: 10 },
    { duration: "20s", target: 0 },
  ],
  thresholds: {
    errors: ["rate<0.05"], // <5% errors
    http_req_duration: ["p(99)<1500"], // 99% of requests must complete below 1.5s
  },
};

export default function () {
  const res = http.get(URLS.BASE_URL);
  const result = check(res, { "status was 200": (r) => r.status == 200 });
  errorRate.add(!result);

  const loginRes = http.post(
    URLS.TOKENS,
    JSON.stringify({
      username: CONFIG.USERNAME,
      password: CONFIG.PASSWORD,
    }),
    {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    }
  );

  check(loginRes, {
    "logged in successfully": (r) => {
      return r.status === 201;
    },
  });

  const loginToken = loginRes.json("token");

  const tokenResponse = http.get(URLS.TOKENS + "/" + loginToken, {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  });

  const tokenBody = tokenResponse.json('user');

  check(tokenResponse, { "verified token": (user) => typeof user !== 'number' });

  sleep(1);
}
