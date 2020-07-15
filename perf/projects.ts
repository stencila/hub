// Project creation deletion
// - Authenticate
// - Fetch list of organizations, and filter for ownershipt
// - Get Org/Account id for use in project creation
// - Create permanent project
// - Add source file
// - Delete project

import { check, sleep } from "k6";
import http from "k6/http";
import { Rate } from "k6/metrics";
import { baseOptions, getAuthenticatedHeader, post, URLS } from "./index.ts";

export const options = Object.assign({}, baseOptions, {
  stages: [
    { duration: "5s", target: 2 },
    // { duration: "30s", target: 20 },
    // { duration: "1m30s", target: 10 },
    // { duration: "20s", target: 0 },
  ],
});

const errorRate = new Rate("errors");

export default function () {
  const headers = getAuthenticatedHeader();

  const getAccountId = () => {
    const accounts = http.get(URLS.ACCOUNTS, { headers }).json("results");
    if (Array.isArray(accounts)) {
      const targetAccount = accounts.find(
        (account) => account.role === "OWNER" || account.role === "MANAGER"
      );

      return targetAccount.id;
    }
  };

  const name = "ergonomic-plastic-hat";
  const project = post(
    URLS.PROJECTS,
    {
      account: getAccountId(),
      title: "Gorgeous Granite Pants",
      description: "Dolorem atque nemo amet iste dolorem.",
      name,
      public: false,
    },
    { headers }
  );

  const result = check(project, { "status was 201": (r) => r.status == 201 });
  errorRate.add(!result);

  const projectId = project.json("id");

  // TODO: Check for job completion
  // const source = post(
  //   URLS.PROJECTS + "/" + projectId + "/sources",
  //   {
  //     type: "UrlSource",
  //     url: "https://raw.githubusercontent.com/stencila/test/master/README.md",
  //     path: "README.md",
  //   },
  //   { headers }
  // );

  // const sourceRes = check(source, { "status was 201": (r) => r.status == 201 });
  // errorRate.add(!sourceRes);

  // sleep(5);

  const delProject = http.del(URLS.PROJECTS + "/" + projectId, JSON.stringify({ name }), {
    headers,
  });

  const delProjectRes = check(delProject, { "status was 204": (r) => r.status == 204 });
  errorRate.add(!delProjectRes);

  sleep(1);
}
