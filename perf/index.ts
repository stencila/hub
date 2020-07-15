// To run:
// 1. install k6 (https://k6.io/docs/getting-started/installation)
// 2. Run a local instance of the Hub
// 3. run in terminal `k6 run -e USERNAME=username -e PASSWORD=password other/perf/index.ts`

import { check, sleep } from "k6";
import http from "k6/http";
import { Rate } from "k6/metrics";

export const CONFIG = {
  URL: __ENV.HUB || "http://127.0.0.1",
  PORT: __ENV.PORT || 8000,
  USERNAME: __ENV.USERNAME,
  PASSWORD: __ENV.PASSWORD,
};

const makeApi = (apiPath) => CONFIG.URL + ":" + CONFIG.PORT + "/api" + apiPath;

export const URLS = {
  BASE_URL: CONFIG.URL + ":" + CONFIG.PORT,
  TOKENS: makeApi("/tokens"),
  PROJECTS: makeApi("/projects"),
  ACCOUNTS: makeApi("/accounts"),
};

const errorRate = new Rate("errors");

export const options = {
  stages: [
    { duration: "5s", target: 2 },
    // { duration: "30s", target: 20 },
    // { duration: "1m30s", target: 10 },
    // { duration: "20s", target: 0 },
  ],
  thresholds: {
    errors: ["rate<0.05"], // <5% errors
    http_req_duration: ["p(99)<1500"], // 99% of requests must complete below 1.5s
  },
};

export const baseHeaders = {
  "Content-Type": "application/json",
  Accept: "application/json",
};

export const post = (url, body = {}, options = {}) => {
  const h = Object.assign({}, { headers: baseHeaders }, options);
  console.log("HEADERS: ", JSON.stringify(h));
  console.log("Body: ", JSON.stringify(body));
  return http.post(url, JSON.stringify(body), h);
};

export const login = () =>
  post(URLS.TOKENS, {
    username: CONFIG.USERNAME,
    password: CONFIG.PASSWORD,
  });

export const getAuthenticatedHeader = (headers = baseHeaders) => {
  const token = login().json("token");

  return Object.assign({}, headers, {
    Authorization: `Token ${token}`,
  });
};

export const deleteToken = (token) => {
  http.del(URLS.TOKENS + "/" + token);
};

export const cleanup = (headers) => {
  const token = header["Authorization"].replace("Token ", "");
  return deleteToken(token);
};
