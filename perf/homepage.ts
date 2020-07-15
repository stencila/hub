// Multiple requests to the homepage
// Intention is to only test for scaling of the `manager` service, without hitting the database or other services.

import { check, sleep } from "k6";
import http from "k6/http";
import { Rate } from "k6/metrics";
import { URLS, options as baseOptions } from "./index.ts";

export const options = Object.assign(
  {},
  baseOptions,
  {
    stages: [
      { duration: "5s", target: 2 },
      // { duration: "30s", target: 20 },
      // { duration: "1m30s", target: 10 },
      // { duration: "20s", target: 0 },
    ],
  }
);

const errorRate = new Rate("errors");

export default function () {
  const res = http.get(URLS.BASE_URL);
  const result = check(res, { "status was 200": (r) => r.status == 200 });
  errorRate.add(!result);

  sleep(1)
}
