# [2.38.0](https://github.com/stencila/hub/compare/v2.37.0...v2.38.0) (2020-06-28)


### Bug Fixes

* **Jobs:** Animate Dispatched status icon ([f1f2707](https://github.com/stencila/hub/commit/f1f270740c0f2e251b4b3d5450aebb38fe444a36))
* **Jobs:** Refine Job list styles and fix Job ID causing breaking layout ([9c146ca](https://github.com/stencila/hub/commit/9c146caa3f02122868bd047b9ea79bfde8802290))
* **Projects:** Standardize sub-page layouts, icons ([4f50e34](https://github.com/stencila/hub/commit/4f50e346d953811a3f9c8abd02754b8539bda62f))
* **Projects:** Use different icons for Files & Sources ([acf2bdd](https://github.com/stencila/hub/commit/acf2bdd52952ae0afe9e57080a542bb8c8dc98c0))


### Features

* **Projects:** Add empty state views to Files/Sources, extract partials ([464bc29](https://github.com/stencila/hub/commit/464bc2930a88a2f882b184539236359bd674e153))
* **Projects:** Move Snapshot button to be closer to files ([6f7a00a](https://github.com/stencila/hub/commit/6f7a00aac8e7ad60eef7e72ad815cce6902ee54f))
* **Projects:** Use Files list as default view for Projects ([d2389e4](https://github.com/stencila/hub/commit/d2389e40d82d0890ed58bf0b7134db3e02718fa1))
* **Sources:** Add header and info to Sources list ([e8038f2](https://github.com/stencila/hub/commit/e8038f2ff383de54d8738b2a2c26924b62951455))

# [2.37.0](https://github.com/stencila/hub/compare/v2.36.1...v2.37.0) (2020-06-26)


### Bug Fixes

* **Jobs:** Use a local function for id generation ([272cb93](https://github.com/stencila/hub/commit/272cb93ed49d36694ae4bc823681563a7b21dd8a))
* **Source pull:** Add callback to job creation ([3f134a9](https://github.com/stencila/hub/commit/3f134a98f6c3aa5253cae932022b9c501d491022))
* **Worker pull jobs:** Ensure that dirs are present ([0db9d85](https://github.com/stencila/hub/commit/0db9d85c832d5ed6e4bfbfee9c71494bcdf636df))


### Features

* **Files:** Adds files (back) into projects ([8e4425e](https://github.com/stencila/hub/commit/8e4425e923effbd74c8be04ae1b33b8e61920e73))
* **Jobs:** Add callbacks to jobs ([f008c38](https://github.com/stencila/hub/commit/f008c383f6ad76415266b3643755bffb640e7747))
* **Worker:** Pull jobs return a dictionary of file paths with info on each file ([ce37007](https://github.com/stencila/hub/commit/ce37007d1b824bf1b60a113028595e8ae2101a79))

## [2.36.1](https://github.com/stencila/hub/compare/v2.36.0...v2.36.1) (2020-06-26)


### Bug Fixes

* **Manager source pulls:** Allow for no token ([605dfcd](https://github.com/stencila/hub/commit/605dfcdf2f33db24457f61de6a9c67dda2e6cb85))
* **Worker pull jobs:** Do not require token for Github ([dec2f47](https://github.com/stencila/hub/commit/dec2f4767a860fffb9af98aa0481b21e647684ec))

# [2.36.0](https://github.com/stencila/hub/compare/v2.35.1...v2.36.0) (2020-06-26)


### Features

* **Job:** Use a string for job ids ([5be5028](https://github.com/stencila/hub/commit/5be50287160070599fce908a3c83384ab4a08bdd)), closes [#458](https://github.com/stencila/hub/issues/458)
* **Jobs:** Add job description field and summary_string property ([929ec6e](https://github.com/stencila/hub/commit/929ec6ea5c71b7cda32526dea857e8e3ee9db578))

## [2.35.1](https://github.com/stencila/hub/compare/v2.35.0...v2.35.1) (2020-06-25)


### Bug Fixes

* **Jobs:** Display formatted runtime ([fa9b59a](https://github.com/stencila/hub/commit/fa9b59a76ed86ce52a29d7ae52ec4e6fdd70bc0e))

# [2.35.0](https://github.com/stencila/hub/compare/v2.34.0...v2.35.0) (2020-06-25)


### Features

* **Snaps:** Add snapshots for project sources ([da5a156](https://github.com/stencila/hub/commit/da5a156e040724beee011b464bc3a1c1d21d2418))

# [2.34.0](https://github.com/stencila/hub/compare/v2.33.1...v2.34.0) (2020-06-25)


### Bug Fixes

* **CSS:** Fix styling of file upload forms on mobile ([c11692f](https://github.com/stencila/hub/commit/c11692f5823000ee92255f2b042a27c4ca7d6737))
* **CSS:** Fix vertical scroll for sidebar menus on mobile breakpoints ([317e769](https://github.com/stencila/hub/commit/317e7696d382607041f2bc43a99fe82bb0af20df))
* **Dropdowns:** Keep dropdown menus in-line on touch breakpoints ([979a474](https://github.com/stencila/hub/commit/979a4748f94934010d17484fd8d7a261c1a5e3ee))
* **Job:** Allow reuse of previously fetched project ([b19903f](https://github.com/stencila/hub/commit/b19903f4fe8d6c4206cdf6b57a577af7dafce78e))
* **Jobs:** Improve updating of job status; add is_active ([8275ed6](https://github.com/stencila/hub/commit/8275ed6104bda9ddfd325598c98942034b463e8a))
* **Jobs:** Restrict access to jobs to project members ([f2a5621](https://github.com/stencila/hub/commit/f2a56210590c03cd64bc7a1653b06572612801a7))
* **Nav:** Fix link to create new organization ([a55acef](https://github.com/stencila/hub/commit/a55acef32b3b46f9d75c9537761376594af98cff))
* **Projects:** Align sharing view title and toggle ([fea7020](https://github.com/stencila/hub/commit/fea702056bdc6ffff13b59f464fc50397e6d132e))
* **Projects:** Disable links to details view for Uploaded file types ([db89110](https://github.com/stencila/hub/commit/db89110d3a5c0b663775f5cb71773570c9cf31b5))
* **Projects:** Fix file-upload success redirect URL ([7dc6d1e](https://github.com/stencila/hub/commit/7dc6d1e4e005f254fe08cbc8e5d223252376682a))
* **Projects:** Fix project view CTA buttons missing border bottoms ([8d8969f](https://github.com/stencila/hub/commit/8d8969fc567156f26839e1e01af9007d52d25c53))
* **Projects:** Give project title and icons space when line wraps ([cd94673](https://github.com/stencila/hub/commit/cd946736c44bbd3706856f17152f2cd314601ec7))
* **Projects:** Temporarily disable table row links due to bug ([4dfa784](https://github.com/stencila/hub/commit/4dfa784bdea94e97026b15d416695d28501541ad))
* **Snapshots:** Add project parameter to get_object ([23f29fb](https://github.com/stencila/hub/commit/23f29fb09256fdc8d3ef2b63049b46e9859e5442))
* **Snapshots:** Align table header labels to the left ([49955c4](https://github.com/stencila/hub/commit/49955c43331400d10742c390ade4c55971e296ae))
* **Source:** Renable file filter ([fe29dcf](https://github.com/stencila/hub/commit/fe29dcfa67c6da735ff0522fe9ad1ac074fb793f))
* **Sources:** Improve efficiency and consistency of fetching template contexts ([ba20b7d](https://github.com/stencila/hub/commit/ba20b7de82f348f84feca0ab0942cd6ae6a5dc42))
* **Worker:** Add alias for URL source ([8b09c95](https://github.com/stencila/hub/commit/8b09c95a3337cd840c43489ecf32628aa9d80e8f))
* **Worker:** eLife source return list of all files ([927782d](https://github.com/stencila/hub/commit/927782d46564e22dfed2270b29ac9f5c463c291d))


### Features

* **Accounts/Projects:** Add header to "New x" views ([e7746a4](https://github.com/stencila/hub/commit/e7746a4c5d1fd6c3cf97d2b1ba0aede60ee2f52d))
* **eLife source:** Add eLife logo and add snaps for new sources ([b95ed27](https://github.com/stencila/hub/commit/b95ed27e9f4145056cfbf35ca49d33ae2e7f8657))
* **Jobs:** Add job list and show children of compound jobs ([80ded47](https://github.com/stencila/hub/commit/80ded471911f7f874d15ac3eb045380854f56c9a))
* **Jobs:** Add templates and styles for Job items ([f1e1564](https://github.com/stencila/hub/commit/f1e1564f8992d49e5f62e6be7bd5d26b73de5613))
* **Nav:** Move "New X" buttons under respective Projects/Orgs nav items ([19df3a8](https://github.com/stencila/hub/commit/19df3a8a55e47993285d3694c0eec3e84ffe4b94))
* **Projects:** Add templates and styles for Source detail  view ([fe3a9d8](https://github.com/stencila/hub/commit/fe3a9d8403fcde31c3fd030d0f04de55e1aa1f42))
* **Projects:** Make entire Source item row clickable ([9d18922](https://github.com/stencila/hub/commit/9d18922c846d39b31573de2bd00f834a18cf77fa))
* **Projects:** Reorganize "New source" menu, add placeholder sources ([9776d95](https://github.com/stencila/hub/commit/9776d95d1e0b5a2dbcab457b3e6bd1322e749be6))
* **Snapshots:** Add templates and styles ([01df7e8](https://github.com/stencila/hub/commit/01df7e8f62a2d78ab68b06863b04295a4c9a3cd2))
* **Snapshots:** Inital version of job based snapshots ([504f1f8](https://github.com/stencila/hub/commit/504f1f8e66702c87379a3704460d1253f50cde36))
* **Sources:** Add retrieve view for sources ([b2dc63c](https://github.com/stencila/hub/commit/b2dc63c00b3d7b01c62df075c51dceaae558e616))
* **Sources:** Connect jobs for pull and preview ([c9ddfdc](https://github.com/stencila/hub/commit/c9ddfdcffb891831b887bcba158bef28396b0190))
* **User tokens:** Add exception handling for missing social auth token ([2ed6d12](https://github.com/stencila/hub/commit/2ed6d12c88d46aef8b9c076dc79dd027953069e8))

## [2.33.1](https://github.com/stencila/hub/compare/v2.33.0...v2.33.1) (2020-06-23)


### Bug Fixes

* **Deps:** Upgrade HTMX and use extensions ([38b8c0e](https://github.com/stencila/hub/commit/38b8c0e59a86624870650224ecd965c56d8dba55))
* **Projects:** Fix setting of public ([79d5519](https://github.com/stencila/hub/commit/79d551956b0580a1862dea6cd545706fb4d03d39))

# [2.33.0](https://github.com/stencila/hub/compare/v2.32.1...v2.33.0) (2020-06-22)


### Bug Fixes

* **CSS:** Reduce icon size for is-small-mobile controls ([8073e30](https://github.com/stencila/hub/commit/8073e30dd92c0be31ae2a523999eed3dfe0bb1db))
* **Deps:** Upgrade pygithub to v1.51 ([8204e12](https://github.com/stencila/hub/commit/8204e120bc8ef22738220bae822bfbd0b368ddae))
* **Jobs:** Update views to use consistent approach to permissions ([407482d](https://github.com/stencila/hub/commit/407482dbdcb3196d11c051595e4ddd512b7cb25c))
* **Snaps:** Avoid breaking element styles ([49ad39c](https://github.com/stencila/hub/commit/49ad39c1548421860ec88ba8ea0106507a4a1538))


### Features

* **Jobs:** Add jobs app from director ([b32352f](https://github.com/stencila/hub/commit/b32352f8d0d6bd49571bbb7def0ce3baae9e6bbe))
* **Manager:** Use django-storages for media files ([e1ab522](https://github.com/stencila/hub/commit/e1ab522868c0e52b8ebee8961d09763c844fb0dc))
* **Snaps:** Add snips for user signin and signup ([76529df](https://github.com/stencila/hub/commit/76529dfbc2c53b0b3c8160147cd9637298cf0f62))
* **Sources:** Add create forms and validation ([abfb27e](https://github.com/stencila/hub/commit/abfb27eaa8a94c087c00d78f422dbf1d20a3c823))
* **Sources:** Add rename action ([9e91114](https://github.com/stencila/hub/commit/9e91114715c3881c92ae7d2d4691a1f54b57ee40))
* **Sources:** Hide source filter until working ([2d3f2a0](https://github.com/stencila/hub/commit/2d3f2a01681d2a0b5ea8bf89e8c4abacb144d10a))
* **Static files:** Use whitenoise to optimize serving of static files ([59ec3cc](https://github.com/stencila/hub/commit/59ec3cc06d431b43b77b04561b806555252467b1))
* **Upload source:** Add upload source ([65f874b](https://github.com/stencila/hub/commit/65f874bf17938f021be4769c71aa0cec11fb4bd6))

## [2.32.1](https://github.com/stencila/hub/compare/v2.32.0...v2.32.1) (2020-06-19)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.96.0 ([18a9e79](https://github.com/stencila/hub/commit/18a9e799085471c39edc0dc92b930d66fca1dbe1))
* **deps:** update dependency @stencila/thema to v2.10.2 ([ec21c77](https://github.com/stencila/hub/commit/ec21c77b722ef2ade344d6f2e0946e0aa5e012d7))
* **deps:** update dependency amqp to v2.6.0 ([ef6f610](https://github.com/stencila/hub/commit/ef6f6109557f697400e33e29f97ea73bd27e963f))
* **deps:** update dependency celery to v4.4.5 ([cc9dcf5](https://github.com/stencila/hub/commit/cc9dcf5578d9b36605f7de0123343665dbb6c4f1))
* **deps:** update dependency django to v2.2.13 ([ebf529a](https://github.com/stencila/hub/commit/ebf529a7c71a74aba43cac37ff2f6135ff1651e4))
* **deps:** update dependency djangorestframework-camel-case to v1.2.0 ([dac80ce](https://github.com/stencila/hub/commit/dac80cee0671542faf4b32b2817b4c935e8ebd27))
* **deps:** update dependency google-api-python-client to v1.9.3 ([9fd79d3](https://github.com/stencila/hub/commit/9fd79d3dc15d13b6c655147c46d1a5f0eec4d578))
* **deps:** update dependency requests to v2.24.0 ([f95a02a](https://github.com/stencila/hub/commit/f95a02a16f1c9e58bd1508144ed0f3557713141e))
* **deps:** update dependency sentry-sdk to v0.15.1 ([7d1d17d](https://github.com/stencila/hub/commit/7d1d17d2ed5ae31f1a46cb69d62a30db02a971d3))

# [2.32.0](https://github.com/stencila/hub/compare/v2.31.2...v2.32.0) (2020-06-19)


### Bug Fixes

* **Snaps:** Improve highlighting, add drop shadow, more elems ([d225254](https://github.com/stencila/hub/commit/d22525499dccf1fdf10bd9a76df1b79d465a0b92))


### Features

* **Snaps:** Highlight elements when taking screenshots ([7dd4f15](https://github.com/stencila/hub/commit/7dd4f15d88c5d763cb8aae674c5af912a4629846))

## [2.31.2](https://github.com/stencila/hub/compare/v2.31.1...v2.31.2) (2020-06-18)


### Bug Fixes

* **Snaps:** Add project related screenshots ([98841e7](https://github.com/stencila/hub/commit/98841e7a7c9b99ac0f1d6bc3615e578c8f6f6f33))

## [2.31.1](https://github.com/stencila/hub/compare/v2.31.0...v2.31.1) (2020-06-17)


### Bug Fixes

* **Accounts:** Fix end tag ([178aed0](https://github.com/stencila/hub/commit/178aed0e76380902bd1dce4996e3997b007ab736))
* **CI:** Do snapshots as part of release ([6f2e812](https://github.com/stencila/hub/commit/6f2e8127add14e6cedd23d5818dff5bc97b884ec))

# [2.31.0](https://github.com/stencila/hub/compare/v2.30.0...v2.31.0) (2020-06-17)


### Bug Fixes

* Hide CRUD operation buttons for non-authorized users ([48573a7](https://github.com/stencila/hub/commit/48573a7eab227a66d91012f155cb8768992aeee6))
* Refine layouts and title sizes on mobile ([27ac913](https://github.com/stencila/hub/commit/27ac91377610b28331a869393ff9c1e477558726))
* **a11y:** Fix accessibility issues ([451439c](https://github.com/stencila/hub/commit/451439cc5dae8584996102d6db1e01fab2fdc105))
* **Account:** Add link to Thema ([422ba00](https://github.com/stencila/hub/commit/422ba00f65b6a9773de7861955736b99ca43b0c9))
* **Account:** Change the corresponding username ([eacd860](https://github.com/stencila/hub/commit/eacd8609da4f2f80bb044637d60593d28e7a098f))
* **Account:** Display full user name if possible ([dfb07b9](https://github.com/stencila/hub/commit/dfb07b9a53dfe1aaad59f0dceb189c74b40f2c20))
* **Account:** Fix sibling border showing below transparent button ([c6cc780](https://github.com/stencila/hub/commit/c6cc780482f153c353fdc7f4219f874853dd0aa3))
* **Account:** Keep Org links on one line by truncating long texts ([5159c47](https://github.com/stencila/hub/commit/5159c47c3f2ce235298ad8d512db618d30e3ad5e))
* **Account:** Update role name Admin -> Owner ([a31d341](https://github.com/stencila/hub/commit/a31d341ef0c536016c5c68dc41b38dee552697d7))
* **Account names:** Do auto slugify and limit length ([6b0d071](https://github.com/stencila/hub/commit/6b0d071f46d6b5cd7aff32f5e7a7a0377c56b680))
* **Account profile:** Remove link on location ([8011104](https://github.com/stencila/hub/commit/8011104a4939ba28c7259b8fbb088ae361218a38))
* **Account sidebar:** Hide users and teams for personal accounts ([9d0d782](https://github.com/stencila/hub/commit/9d0d782f1f1164a555b06144d88e720423ee8285))
* **Account users:** Do not allow changing self ([9eec64c](https://github.com/stencila/hub/commit/9eec64c6bdafc69c86a08d3a60ee5ba92b0fc117))
* **Accounts:** Change no projects messaged based on user / org ([16f5ef9](https://github.com/stencila/hub/commit/16f5ef933853352e0a45260c740ee57b139f5aa9))
* **Accounts:** Correct the value for owner role. ([13e7dae](https://github.com/stencila/hub/commit/13e7daed533043a9254966156c7960a5157f4fda))
* **Accounts:** Fix Accounts view sidebar links ([dd6b9e8](https://github.com/stencila/hub/commit/dd6b9e80ac264739e8d23bf97a2444f118fe6445))
* **Accounts:** Only show the projects that the current user has access to ([da54a29](https://github.com/stencila/hub/commit/da54a2984c2abe040e20b4bb3d054cf8f5517de3))
* **Accounts:** Produce notice if no projects for account; connect create project button ([1b1e285](https://github.com/stencila/hub/commit/1b1e28591b505dd890f2c33b4d3fa1eaa521a8a0))
* **Accounts:** Redirect to project page on CREATED ([40d4923](https://github.com/stencila/hub/commit/40d492341b6d355a6283c973204d17c9589ba0c0))
* **Accounts:** Remove leading slash ([4969eb7](https://github.com/stencila/hub/commit/4969eb7874c2ae675eb601f2f386deb1154804a1))
* **Accounts:** Use standard response codes and redirections ([11f8d20](https://github.com/stencila/hub/commit/11f8d2008aff954eaf78a4626ffead4379d449fb))
* **Accounts sidebar:** Address todo's and rename files ([10e296c](https://github.com/stencila/hub/commit/10e296c56744e328e5c0b86fd4d58385a5a036ba))
* **Base temlate:** Links to user' acount profile ([24a0bf6](https://github.com/stencila/hub/commit/24a0bf62efc1dd8e64d2c8543570918ce45024d4))
* **Base template:** Go to user's account settings ([aea8d4d](https://github.com/stencila/hub/commit/aea8d4d3af564b30ff2632651052173d5b0fd430))
* **CSS:** Fix color transitions for text-link-hover classes ([44a3179](https://github.com/stencila/hub/commit/44a3179aecce8ccd69f6f108eb836979d24e48b4))
* **CSS:** Fix horizontal scroll "wiggle" on mobile ([4fecb5a](https://github.com/stencila/hub/commit/4fecb5a2ca19ee703cd2385bb630bc7ab1658705))
* **Form fields:** Use the field name as the id ([508e823](https://github.com/stencila/hub/commit/508e823f35c68723c88197ca5469b971b4ded2fd))
* **Home:** Anon users get redirected to projects page ([5496aa3](https://github.com/stencila/hub/commit/5496aa301ef66220cb370b6a9bb23b9a01c05ed3))
* **Home:** Redirect authenticated users to their profile page ([e1a1a0b](https://github.com/stencila/hub/commit/e1a1a0be20b520b3f827e5d36e09d237ec13ec9c))
* **HTMX:** Add method override middleware ([d52b8eb](https://github.com/stencila/hub/commit/d52b8eb333cbcf59d0c0aafe0b88ede9e9f4b4a7))
* **Icon + Link:** Fix vertical alignment of links with icons ([1141e81](https://github.com/stencila/hub/commit/1141e819ea0d8357ddd0594705c5199f3f49d348))
* **JS:** Attach dropdown event listeners to dynamic HTMX elements ([e439498](https://github.com/stencila/hub/commit/e4394986e3ba1ffff1e1d3900ff04229c630c19e))
* **Layout:** Fix horizontal gutter alignment across breakpoints ([d72bd75](https://github.com/stencila/hub/commit/d72bd752cc692304205623f839278c501f7aa8b7))
* **List Views:** Standardize "New X" button sizings ([9edfada](https://github.com/stencila/hub/commit/9edfada5fd57b351a3cb92e7ca36bfb1a0a23cc2))
* **Manager:** Add custom HTMX extension to standardize requests ([668834d](https://github.com/stencila/hub/commit/668834d929a211792cbaccb8beafaed59be30037))
* **Manager:** Implements permissions for accounts and teams ([398c70b](https://github.com/stencila/hub/commit/398c70bb56630d3553b8211e74fa6657b704030d))
* **Manager:** Improve item selection ([dc1d696](https://github.com/stencila/hub/commit/dc1d696e0b40ed03045f88dfb39f4c5fc2ce253f))
* **Manager:** Improve page snapshots ([77fb4c4](https://github.com/stencila/hub/commit/77fb4c475adf1dd032ccfcf44c9c07c3a88ea83a))
* **Manager:** Only make creator admin on created ([f0f6ee9](https://github.com/stencila/hub/commit/f0f6ee9fe53e990f272772c673085ebbe66afe61))
* **Manager:** Refinements to snapshotting ([8b3f3dd](https://github.com/stencila/hub/commit/8b3f3dd0bc2c4b1ac8995228bcc3fd61c3464122))
* **Manager:** Save accounts ([9b347a2](https://github.com/stencila/hub/commit/9b347a20329c7bca1bf99c2391a5be57d8137906))
* **Manager:** Template tweaks ([373cf67](https://github.com/stencila/hub/commit/373cf6781f008cb73eb465ea53be517c80f08cd4))
* **Manager:** Use django-imagefield for alternative image sizes etc ([5b7063f](https://github.com/stencila/hub/commit/5b7063f91d57cc2db9af5b0fc5398ef2dc60b36d))
* **Manager:** Use is-hoverable so result disappear when inactive ([ef2e977](https://github.com/stencila/hub/commit/ef2e9774193f9843cf78c4b157ad54eae0a0e015))
* **Manager:** Use slug patterns in URLs ([1f6b044](https://github.com/stencila/hub/commit/1f6b044db610c07cbdbeb0faecfd6fae5697b77b))
* **Nav:** Fix avatar image proportions and quality ([09b81b2](https://github.com/stencila/hub/commit/09b81b2a93627bfe91f06f87b18a6d4e627662d5))
* **Navbar:** Hide "Create A" menu for anonymous users ([898bf0f](https://github.com/stencila/hub/commit/898bf0f0b35dd71beb862ded30637d08c74039dc))
* **Navbar:** Remove dropdown arrow from "Create a" button ([b36f4ad](https://github.com/stencila/hub/commit/b36f4adeefd443b6f7e432efe58f3506c7722755))
* **Orgs and projects search:** Give anon access but remove buttons ([b9a9f95](https://github.com/stencila/hub/commit/b9a9f957464ae5ba7507b18d0e81748f3801fed4))
* **Orgs list:** Order by role ([30d0639](https://github.com/stencila/hub/commit/30d0639f12aa02038fba0e52fcf91d413c056a55))
* **Password reset:** Link to user's profile page ([5a7c71e](https://github.com/stencila/hub/commit/5a7c71e8dc32a203ec2b5e08c4939d1d78797f72))
* **Project:** Inherit project role from account role ([068ab29](https://github.com/stencila/hub/commit/068ab297a2732ebe05b1cc1937750414718fe5db))
* **Project:** Use title defaulting to name ([f2af9ba](https://github.com/stencila/hub/commit/f2af9baa992ff18778ffb6ae9eb6a364e2fe014a))
* **Project sharing:** Display role of users readonly ([f8cb7ef](https://github.com/stencila/hub/commit/f8cb7efea603beaaf40d5a589e7e16dfdcd6a7e2))
* **Projects:** Add project title to settings form ([3f43737](https://github.com/stencila/hub/commit/3f43737e98a37884c2d33f8fbd14798f270e3669))
* **Projects:** Add role checking on get_object ([b500952](https://github.com/stencila/hub/commit/b500952668e0cea1eeb06a310868c7af48f0f1b5))
* **Projects:** Connect API endoints for project CRUD ([1612b18](https://github.com/stencila/hub/commit/1612b1809dfb2a85e0f9ed1c0dfff7b89642230f))
* **Projects:** Fix Action Bar button alignment on mobile ([a7cde75](https://github.com/stencila/hub/commit/a7cde75c6bc3c66c3d0c324b5a85549517f8ed75))
* **Projects:** On CREATED redirect to the main sources page ([d5987da](https://github.com/stencila/hub/commit/d5987daae5ce478ab980f9415fbe75ac2bf33a54))
* **Projects base:** Fix URLs for links ([461107d](https://github.com/stencila/hub/commit/461107daa81d65d955fba50c4bb0e7ed48aaa61f))
* **Projects List:** Fix clickable target area for each project ([548d08e](https://github.com/stencila/hub/commit/548d08ecd99b2e7acc1b47eb5b1d5edacbd2e116))
* **Sign Out:** Fix sign-out modal button layout ([87852bd](https://github.com/stencila/hub/commit/87852bd576f67ff9a60c06d96119951349ad478d))
* **Sign up:** Provide link to Ts&Cs ([f23ab77](https://github.com/stencila/hub/commit/f23ab77b335c7b87a06e71e5be4e8e7924eafef5))
* **Signin:** If not auth provider cookie make pswd login button solid ([5030d78](https://github.com/stencila/hub/commit/5030d78efad62f1d08b00896f1f70fb443de6c76))
* **Team destroy:** Fix typ in status name ([cc44b39](https://github.com/stencila/hub/commit/cc44b39b4b9ab957629632ec8b7e169c32a7106f))
* **Team list:** Add toolip to membership icon ([35bab69](https://github.com/stencila/hub/commit/35bab69adfa0a3144a176d704ed966b94b566b67))
* **Team names:** Auto slugify names and fix redirection ([d3829fc](https://github.com/stencila/hub/commit/d3829fc2f104d15cfc83cdfcd1b43f1bbdc3875b))
* **Themes:** Add select choices for account and project themese ([78fddc8](https://github.com/stencila/hub/commit/78fddc835fd1bab0e9d35f82e8c9a67ec8785034))
* **User list:** Fix entity name ([c2df15b](https://github.com/stencila/hub/commit/c2df15be3d502cd5ffe57e2255c6e43b6fc3f865))
* **User settings:** Remove separate page and put in user account's settings ([c2b72c7](https://github.com/stencila/hub/commit/c2b72c7cbbe504be463149ad5ab6089b01ed8c69))
* **Users:** Disable browser autocomplete for user search ([1207eb5](https://github.com/stencila/hub/commit/1207eb5e2a293aba49fd6d9b0c711b6141113934))
* **Users:** Hide Users tab for unauthorized users ([87ccfa7](https://github.com/stencila/hub/commit/87ccfa7fc1db4463371864757f30eda29df06b5c))
* **Users:** Remove unused username change form; redirect unmatched /me paths ([8673470](https://github.com/stencila/hub/commit/867347044081e41bfd08431c86458fb9b10e80e6))
* **Users:** Update "remove user" icon to match one in Teams view ([e731e37](https://github.com/stencila/hub/commit/e731e37ced7e523de418991c85b6d9735bb486d2))
* **Users:** Update user permission label Admin -> Owner ([2bc8b5a](https://github.com/stencila/hub/commit/2bc8b5a1c3211611004ea62720ef067957ea9d49))
* **View names:** Use nested names and improve is_active tag ([c1bb25a](https://github.com/stencila/hub/commit/c1bb25a29321e6d4bbda7126c166a2d371480ddf))


### Features

* **Accont quotas:** Add middleware to capture exceptions ([142695f](https://github.com/stencila/hub/commit/142695f264f238c298d9ec52f4ab412f2c42b1a2))
* **Account:** Allow uploading of account image ([6325479](https://github.com/stencila/hub/commit/63254799f10c6a30b69c8ef6df2a26ca5fefd8db))
* **Account forms:** Add more fields to forms ([8383fd6](https://github.com/stencila/hub/commit/8383fd688de3a3f72ab577f7fd36b0a25780e847))
* **Accounts:** Add profile related fields ([4bee30c](https://github.com/stencila/hub/commit/4bee30c7ba6169b87afb5296879a0c7af87c6957))
* **Accounts:** Style Empty State view when Account has no projects ([0ab9415](https://github.com/stencila/hub/commit/0ab9415f743f3409bb9f172f5227e32aa032aeba))
* **CSS:** Add custom toggle switch component ([45478f1](https://github.com/stencila/hub/commit/45478f11cb2167436b7c53a25349f8aaf4237708))
* **CSS:** Animate color transitions for all buttons by default ([6eeeec6](https://github.com/stencila/hub/commit/6eeeec6aa6856bb2c9adfcb6fb3ff985b1fc317e))
* **CSS:** Bump default column gap, giving elements more breathing room ([63e1567](https://github.com/stencila/hub/commit/63e1567bee3694ddc82d1a7755743b90a2873a8e))
* **CSS:** Customize Bulma colour scheme ([9fb63b5](https://github.com/stencila/hub/commit/9fb63b5e6c15d9577ffc2839d184385ad50981cf))
* **CSS:** Use solid button styles when a form has focus ([90e66ff](https://github.com/stencila/hub/commit/90e66ff18e2f29d47e8628c961a919019a90d663))
* **Dropdown:** Use Popper.js for smart positioning of dropdown menus ([a6e2458](https://github.com/stencila/hub/commit/a6e2458ec08520995fa9ee5511a9d109133a888c))
* **Forms:** Allow setting a "disabled" attribute on form buttons ([2ed8198](https://github.com/stencila/hub/commit/2ed819810589e7429a47910fc2a8a0aee1dffde4))
* **Forms:** Fix input accessibility by connecting fields to labels ([7047707](https://github.com/stencila/hub/commit/7047707610c0b04dac89240921ac99b3b86bb37c))
* **HTMX Extension:** Detect if should redirect ([20c6d73](https://github.com/stencila/hub/commit/20c6d737c397c8c6af46725a726e44032f8339c1))
* **i18n:** Use Django translation utilities to set content locale ([3e6aacc](https://github.com/stencila/hub/commit/3e6aaccfa0ef55372ec2db847ee2283b82ca17ae))
* **Manager:** Add a user search ([38d9740](https://github.com/stencila/hub/commit/38d97407dbc45add24f4d9947ee0fe37b87a78aa))
* **Manager:** Add account teams ([6bd16fe](https://github.com/stencila/hub/commit/6bd16fe66fdf6277868c82e6ca0878cd4e003423))
* **Manager:** Add account users and unique constraints ([83fb836](https://github.com/stencila/hub/commit/83fb836585c89a2b2d25fc7cee38174d925dc838))
* **Manager:** Add accounts ([ee45afb](https://github.com/stencila/hub/commit/ee45afb72916b006a52b9ab583770130db401561))
* **Manager:** Add fallback images for accounts ([ed133cf](https://github.com/stencila/hub/commit/ed133cfcffa2a80733c8fa3d2d3ce2ac59ede9b6))
* **Manager:** Add users app ([876e592](https://github.com/stencila/hub/commit/876e592a08ea8415c16279ab2f7c58307715d24e))
* **Manager:** Deduplication of users ([1b95f08](https://github.com/stencila/hub/commit/1b95f082af1468187269a125a5335b4e088e8fd7))
* **Manager:** Implement hx-redirect by status ([b84e431](https://github.com/stencila/hub/commit/b84e43153a081afadf27c1805b8764481d38e543))
* **Manager:** Initial set of account views ([5009b79](https://github.com/stencila/hub/commit/5009b79b1a467aa3d8cfbd05a8b73bfa4ee623d4))
* **Nav:** Add Admin link for Staff/Superuser accounts ([efee3bd](https://github.com/stencila/hub/commit/efee3bd4fa8ebe9596ef0ce21cbdcc77c9be7b52))
* **Nav:** Add icons to Nav items ([06e7efc](https://github.com/stencila/hub/commit/06e7efc4b451053faa48f28d81de4ba053e037d4))
* **Nav:** Adjust Navbar item color ([966817c](https://github.com/stencila/hub/commit/966817c34fa50b8e50d8a4b51c58e112d8ead521))
* **Nav:** Change icon for Organizations ([784231b](https://github.com/stencila/hub/commit/784231bb31f481fd58bf4b90cd458e7d1e4eb38f))
* **Nav:** Conditionally show/hide sign in and sign up buttons ([46f87a2](https://github.com/stencila/hub/commit/46f87a2fb3ef2a4072ecd3ff7cb276f21acd5861))
* **Nav:** Increase font weight of Nav items for better prominence ([8f9e941](https://github.com/stencila/hub/commit/8f9e941e5f0505ec1b8cfe8edbdf7f3ec40d35e1))
* **Nav:** Reduce visual weight of dropdown arrows ([a24578f](https://github.com/stencila/hub/commit/a24578f0e3804d236dbe263fd82c479df7d6c976))
* **Nav:** Use left aligned logo. Show only icon for signed in users ([86c075f](https://github.com/stencila/hub/commit/86c075f388a23c7c904dbdbb5b9dad600326799e))
* **Navbar:** Refine nav bar layout and add top level links ([f6eecc2](https://github.com/stencila/hub/commit/f6eecc21ab40045141af9577aa569b5d3c2e585d))
* **Organizations:** Add search for orgs page ([d3a41cd](https://github.com/stencila/hub/commit/d3a41cd0cc6b0b4ef48d50e146a0e69487eb30c5))
* **Orgs list:** Add role display and filtering ([338d90f](https://github.com/stencila/hub/commit/338d90f65145207e7459a75d752e180e6ca1ebd4))
* **Pojects, Accounts:** Autofocus name fields for improved UX ([773c3f1](https://github.com/stencila/hub/commit/773c3f1438d67581e3141031683e18753ec3122a))
* **Project:** Prompt Author/Managers to add project description ([1814788](https://github.com/stencila/hub/commit/18147885bd9de8b2e53526ed5529a24b6446dedd))
* **Project sharing:** Implement add, change and modify collaborators ([09466d3](https://github.com/stencila/hub/commit/09466d3a782ba880fb553e93832386d488107cd7))
* **Projects:** Add empty state message to Projects view ([6af16df](https://github.com/stencila/hub/commit/6af16dff5284a47557402ddd35f0af7ce0813815))
* **Projects:** Add file filtering ([2330370](https://github.com/stencila/hub/commit/23303707e6941c096646acd9faa4aa7af552e923))
* **Projects:** Add project search and filtering ([3ebbcc6](https://github.com/stencila/hub/commit/3ebbcc620c27358a9aac6c4dbe8419ba934d193c))
* **Projects:** Add project/sharing url ([8ccc632](https://github.com/stencila/hub/commit/8ccc632a7499d3dcd62e1662503c2aff097e7b4d))
* **Projects:** Improved project filtering ([f71ca8a](https://github.com/stencila/hub/commit/f71ca8ac1a049bd416eea2a550aa06c94623d50c))
* **Projects:** Style project overview view ([8f0d0b0](https://github.com/stencila/hub/commit/8f0d0b01ac87662742a6ec94da6d1b4e1b8792a1))
* **Projects:** Style Settings view ([c67c441](https://github.com/stencila/hub/commit/c67c4414c26fa9a20d4ccd594ffdcc9f0660ea21))
* **Projects:** Validate and auto slugify project names ([c05210c](https://github.com/stencila/hub/commit/c05210c6b904f29a1fa0842d929d1e9ed8123bdc))
* **Search:** Add loading indicators to search input fields ([d17d00b](https://github.com/stencila/hub/commit/d17d00be9d3db526dfb504bd39c316b013528401))
* **Serializer:** Add an "autofocus" argument to input serializers ([b6f04e3](https://github.com/stencila/hub/commit/b6f04e34bb6401fd32f6b514b23e6ecddc0ccb25))
* **Settings:** Refine settings UI styles ([555a8f7](https://github.com/stencila/hub/commit/555a8f7b3943a9b087c21a4cbb0d421fac0a23d8))
* **Sign in:** Autofocus username field on page load ([860a4d2](https://github.com/stencila/hub/commit/860a4d26cbe8911cbe7aef68ba614f28c972ac87))
* **Sources:** Move New/Delete Source forms to a styled modal ([8a3170d](https://github.com/stencila/hub/commit/8a3170dca18a497529901ae244a5079b23f46689))
* **Sources modals:** Add cancel button ([fbf0403](https://github.com/stencila/hub/commit/fbf04030d9f1abba1286d8eae80966350927e233))
* **Style:** Add utility class for changing text color on hover ([9c56ae9](https://github.com/stencila/hub/commit/9c56ae94ee8742c544f4ec053cc981608a282bbc))
* **Style:** Reorganize CSS and add color transition utility class ([2e7b254](https://github.com/stencila/hub/commit/2e7b25487ce1256843ba0809e30f982161e4b563))
* **Teams:** Add CRUD for teams ([174ae11](https://github.com/stencila/hub/commit/174ae11b7387b3185f24fe202f365958b5bc3cd9))
* **Teams:** Add listing page ([6839b92](https://github.com/stencila/hub/commit/6839b92448d9a62d0e343f2187379931639c7517))
* **Teams:** Add new team button ([b99066b](https://github.com/stencila/hub/commit/b99066be271cdbbc9158b8c226d37df8392efd8f))
* **Teams:** Style Teams view ([0331955](https://github.com/stencila/hub/commit/033195572cd57611282438b88d3af01c359a0c7f))
* **Teams:** Use tooltip for "more team member count" message ([dedb592](https://github.com/stencila/hub/commit/dedb592ee043cb010da891629648082f263ab37d))
* **Template tags:** Add tags and filters for sugar in templates ([433705a](https://github.com/stencila/hub/commit/433705a8864b0c6482f1abf5d0f6ef5ef376dd0d))
* **Templates:** Add Sidebar template and use for accounts detail view ([c9e6034](https://github.com/stencila/hub/commit/c9e6034424b590a0b7c82ef20e6f39c59fedb351))
* **Tooltips:** Add Bulma extension for tool tips ([3649a3f](https://github.com/stencila/hub/commit/3649a3f0f1612adb18cde3600c1f53f6543fbed1))
* **User search:** Allow for changing the name of the id field ([0678fd0](https://github.com/stencila/hub/commit/0678fd082252371a9d2da23782aec81f8fcc9ae9))
* **Users:** Add CRUD for account users ([e794794](https://github.com/stencila/hub/commit/e794794f0c86c346f21a767cdfd75790e9a8696c))
* **Users:** Add own-role in Org Users list, and show tooltip with info ([124a658](https://github.com/stencila/hub/commit/124a658dd6f08aea9c0ee1de838e12de99484c7e))
* **Users:** Style Users list view ([36a6077](https://github.com/stencila/hub/commit/36a60778f7a2f43ed900dedc34de1165b9d5d4fe))

# [2.30.0](https://github.com/stencila/hub/compare/v2.29.2...v2.30.0) (2020-06-02)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.94.0 ([7d579d1](https://github.com/stencila/hub/commit/7d579d14b39cdb019285762635ba0b995928450a))
* **deps:** update dependency django-allauth to v0.42.0 ([ecf6258](https://github.com/stencila/hub/commit/ecf6258ebb19606a74468a8dda55e2c3c245ffea))
* **deps:** update dependency google-api-python-client to v1.8.4 ([fa26cfe](https://github.com/stencila/hub/commit/fa26cfecf155334e7272c4056a30684dea71034e))
* **deps:** update dependency httpx to v0.13.3 ([6dc9b42](https://github.com/stencila/hub/commit/6dc9b42ea09c23013321c92e87232be9ad7ffef6))
* **deps:** update dependency prometheus_client to v0.8.0 ([5815f29](https://github.com/stencila/hub/commit/5815f29965695ac8d38abd31b282992b6b03c23d))
* **Director:** Link new oauth user by verified email ([2012200](https://github.com/stencila/hub/commit/20122006b1a668af1d1a6b44a204e1bc0344ffe0))
* **Director:** Prefer primary email when matching ([3cd6d34](https://github.com/stencila/hub/commit/3cd6d348c65a2e31b17bfae53e406bd8fc1b439c))
* **Director:** Remember last login provider ([f092c2e](https://github.com/stencila/hub/commit/f092c2e36a8eb82e466c9dec5399de4da3883459))
* **Director:** Save emails from new social account ([a255ea1](https://github.com/stencila/hub/commit/a255ea1ebd1f3b6876902de912d53f0273565215))
* **Director:** Use verified github emails in match ([839d726](https://github.com/stencila/hub/commit/839d726f362bc054adbf96ba4f895563e476a0bb))


### Features

* **Overseer:** Add metrics for jobs and workers per queue ([ac48429](https://github.com/stencila/hub/commit/ac484295c4dd2c9b3e645d0f1b48655df7330c69))

## [2.29.2](https://github.com/stencila/hub/compare/v2.29.1...v2.29.2) (2020-05-26)


### Bug Fixes

* **Worker:** Do not ignore util ([249b7a8](https://github.com/stencila/hub/commit/249b7a8795ebc36d1785a3afbe4bb59f2b9904b4))

## [2.29.1](https://github.com/stencila/hub/compare/v2.29.0...v2.29.1) (2020-05-26)


### Bug Fixes

* **Broker:** Add volume for presistence across restarts ([1a4411a](https://github.com/stencila/hub/commit/1a4411aba4393d4e78182b5a40eaf2cebc5b028c))
* **deps:** update dependency google-api-python-client to v1.8.3 ([551ee4f](https://github.com/stencila/hub/commit/551ee4f9e882dd21899f2a61b0be5748d0c9c1ce))
* **Director:** Add plos source ([fb72b45](https://github.com/stencila/hub/commit/fb72b452be31bf9f213c7de17e2bc10627dcebfe))
* **Director:** Do not force rediret internal API endpoints ([914ba90](https://github.com/stencila/hub/commit/914ba9046dc193d1f34f01956e3d107dd1ed6416))
* **Director:** Trigger gdoc pull job from source ([1efa569](https://github.com/stencila/hub/commit/1efa569226a00b9373ec4f1951333b2d8f4feaa4))
* **Director:** Trigger github pull job from source ([f4c7c8c](https://github.com/stencila/hub/commit/f4c7c8c1a52e5f5c479604b848eb318c0741cc21))
* **Director:** Trigger pull job from GDrive source ([7f37a52](https://github.com/stencila/hub/commit/7f37a52e36122d33c03917a3f23c8da311b3a8bf))
* **Worker:** Google docs pull job ([692ec41](https://github.com/stencila/hub/commit/692ec4163ee48c0927cf34a4a159046f082d206f))
* **Worker:** Pull from github sources ([423c3aa](https://github.com/stencila/hub/commit/423c3aa2f0c8ca6ec83526d1a63254a4b3517d2d))
* **Worker:** Pull into a subdirectory ([cfb2d75](https://github.com/stencila/hub/commit/cfb2d753a2de816f077771812ca9a54a511a370e))
* **Worker:** Pull job for Google Drive folder ([e97efac](https://github.com/stencila/hub/commit/e97efacea885fa6fb8690729107a2bc2a88b8994))
* **Worker:** Pull single file from github ([78b8361](https://github.com/stencila/hub/commit/78b83616927383aba7c75511bf61c574e85dc227))
* **Worker:** Push job for google doc ([06511d7](https://github.com/stencila/hub/commit/06511d7f559fefa43fd528a56464313455052c1d))

# [2.29.0](https://github.com/stencila/hub/compare/v2.28.0...v2.29.0) (2020-05-26)


### Bug Fixes

* **API exception handler:** Handle non-dict exception data ([c7ff9d9](https://github.com/stencila/hub/commit/c7ff9d92f85dcd5aa990430ebd3a6dd0414d9403))
* **Director:** Project serializer to handle both create and update ([a997547](https://github.com/stencila/hub/commit/a9975479d2f9d416f0090298e183eac6d325b86b))
* **Director:** Use form helpers for jobs cancel ([f4336c9](https://github.com/stencila/hub/commit/f4336c926a512376ca7b0ff768fba7c63da90d0d))


### Features

* **Director:** Add section to delete project to settings ([6867f9e](https://github.com/stencila/hub/commit/6867f9e6d549c3fdd6945359fb903a63df84dce6)), closes [#402](https://github.com/stencila/hub/issues/402)
* **Director:** Better handling of errors and success URL ([1d5c5e1](https://github.com/stencila/hub/commit/1d5c5e1769f02e16f1a6dc155b0d6f32466c7d39))
* **Director API:** Add destroy action for projects ([596f4d6](https://github.com/stencila/hub/commit/596f4d600b63e3791ace52b2c65c9f6789e5eed9))

# [2.28.0](https://github.com/stencila/hub/compare/v2.27.2...v2.28.0) (2020-05-24)


### Bug Fixes

* **jobs:** update to css modifiers ([3da5682](https://github.com/stencila/hub/commit/3da56828aba366bdcc0c5ded2247d4fd614b2a4a))
* **projects:** adjusted padding on form as per [#434](https://github.com/stencila/hub/issues/434) ([741e47e](https://github.com/stencila/hub/commit/741e47e4888f09493414812a143d590fe9a5fe17))


### Features

* **Director:** UI updates to jobs listing ([6742d85](https://github.com/stencila/hub/commit/6742d8584d64cc12ccff68cc395e32ff603b07b9))
* **Director:** updating job filters ([b879d92](https://github.com/stencila/hub/commit/b879d928084bb799ab636d29415461aab9fb3b83))
* **job:** updates to job filtering [#453](https://github.com/stencila/hub/issues/453) ([fb0728d](https://github.com/stencila/hub/commit/fb0728d8df83afdfdbe34746be38e98e1561a841))
* **jobs:** job cancel action added. ([be50f4c](https://github.com/stencila/hub/commit/be50f4cf4f1f27710a3609f7f63ff56fc733f433))

## [2.27.2](https://github.com/stencila/hub/compare/v2.27.1...v2.27.2) (2020-05-24)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.93.11 ([79b650e](https://github.com/stencila/hub/commit/79b650ed049644ed6d57d2f025c33b9087362798))
* **deps:** update dependency @stencila/thema to v2.10.1 ([5ccce01](https://github.com/stencila/hub/commit/5ccce0121db93ded7bd8be463d454cebda72e566))
* **deps:** update dependency httpx to v0.13.1 ([ec63eca](https://github.com/stencila/hub/commit/ec63eca5a109c72334feb13f8efb07f1005af72a))
* **deps:** update dependency lxml to v4.5.1 ([28eeefa](https://github.com/stencila/hub/commit/28eeefa8d423354c188632ad930c86864b54cc67))
* **deps:** update dependency stencila-schema to v0.43.1 ([0fe218f](https://github.com/stencila/hub/commit/0fe218ff6648dee1e79ca0c152734226c278497c))

## [2.27.1](https://github.com/stencila/hub/compare/v2.27.0...v2.27.1) (2020-05-19)


### Bug Fixes

* **Director:** Fix API for cancelling a job [skip ci] ([43a6920](https://github.com/stencila/hub/commit/43a69204819c442d87d7b4666d42a2a6f5c17d4e))
* **Director:** Fix API job retrieve view [skip ci] ([393310c](https://github.com/stencila/hub/commit/393310c38313934d5c143df4254eb6e437687645))
* **Director:** Jobs API: use permissions guard ([a6034dd](https://github.com/stencila/hub/commit/a6034ddae84204ede43d62c50a173b889b3ee1c4))

# [2.27.0](https://github.com/stencila/hub/compare/v2.26.0...v2.27.0) (2020-05-19)


### Bug Fixes

* **Director:** merge conflict errors ([decad48](https://github.com/stencila/hub/commit/decad482f2b3ed292ac5e9b84eddd2b873476fea))
* **jobs:** lint error ([adcc625](https://github.com/stencila/hub/commit/adcc6251dafaf1b17536913fbb5d5f286c51da82))
* **jobs:** Updates to PR [#448](https://github.com/stencila/hub/issues/448) ([ded1cdf](https://github.com/stencila/hub/commit/ded1cdf858e229c2439a0d2c3f9fcc962cf9904c))


### Features

* **Director:** added jobs details template/view ([1f39400](https://github.com/stencila/hub/commit/1f394009646f4db9c4778e25a43f848f6c656a27))
* **Director:** added jobs to main dropdown nav ([1e73ec1](https://github.com/stencila/hub/commit/1e73ec192634e39e143df884fa7f475f3666bec9))
* **Director:** adding jobs view ([52c4abf](https://github.com/stencila/hub/commit/52c4abf8cbd0f3ff12bd2324fa4283f2f433cab6))
* **Director:** completion of jobs list template ([43e3ad7](https://github.com/stencila/hub/commit/43e3ad749b12b8302ee4fe74baa06f0c6bb34765))
* **Director:** removing jobs script for now ([b54164c](https://github.com/stencila/hub/commit/b54164cb3856a58565af6eaf7138c15a0eb15033))
* **Director:** removing jobs script for now ([e583825](https://github.com/stencila/hub/commit/e583825f1cd0cb657ba12d69a40c70cd55301ac5))
* **Director:** rollback of unecessary Docker/npm changes ([4880a61](https://github.com/stencila/hub/commit/4880a6127fc2953b1bc6a4da2f03dc00484706d6))
* **Director:** Setting up jobs urls and views ([e3f90b5](https://github.com/stencila/hub/commit/e3f90b58807e65afcb2ca38a32adda936f38949f))
* **Director:** wip - adding job creation script ([6888b11](https://github.com/stencila/hub/commit/6888b11bfcf1ed58d562d4d5e69e7253d83e58d3))
* **jobs:** wiring up templates to test data ([87c5bdf](https://github.com/stencila/hub/commit/87c5bdf1617bf0ee3a19132e90756ff8aae82b83))

# [2.26.0](https://github.com/stencila/hub/compare/v2.25.2...v2.26.0) (2020-05-17)


### Bug Fixes

* **Director:** Add request_permissions_guard ([e93b417](https://github.com/stencila/hub/commit/e93b417e8eb84d4d656ece7ba5baaa32a7bccec3)), closes [#398](https://github.com/stencila/hub/issues/398)


### Features

* **Director:** Create pull job for sources ([44533ef](https://github.com/stencila/hub/commit/44533efa7f2151b00f4af632933a289e4f90d9a5))
* **Director:** Update job model and API views ([9ba9ac3](https://github.com/stencila/hub/commit/9ba9ac350e5211d5d9005b59268af0698dc82ed9))

## [2.25.2](https://github.com/stencila/hub/compare/v2.25.1...v2.25.2) (2020-05-16)


### Bug Fixes

* **CI:** Remove copy of top package.json ([62d2c32](https://github.com/stencila/hub/commit/62d2c325738bfbceeda242d36b481a505a581126))

## [2.25.1](https://github.com/stencila/hub/compare/v2.25.0...v2.25.1) (2020-05-16)


### Bug Fixes

* **Director:** Change location of Encoda install ([a9277ae](https://github.com/stencila/hub/commit/a9277aed134de12e7a33fcdeffa957d0ceb760d6))

# [2.25.0](https://github.com/stencila/hub/compare/v2.24.1...v2.25.0) (2020-05-15)


### Bug Fixes

* **deps:** update dependency @stencila/thema to v2.7.3 ([2d98e00](https://github.com/stencila/hub/commit/2d98e00ccd42f3634ea5340a3965684b55d65fcb))


### Features

* **CSS:** Colocate Styles package inside Hub ([2f03bb7](https://github.com/stencila/hub/commit/2f03bb7b8822cc2e18e8ae5bc128c0c8578148ec))

## [2.24.1](https://github.com/stencila/hub/compare/v2.24.0...v2.24.1) (2020-05-14)


### Bug Fixes

* **Worker:** plos pull job ([75e682e](https://github.com/stencila/hub/commit/75e682e4d2dbc374ee3d3d0a6179593b4264c617))

# [2.24.0](https://github.com/stencila/hub/compare/v2.23.1...v2.24.0) (2020-05-14)


### Bug Fixes

* **Worker:** Add malicious host test from director ([6a0cd66](https://github.com/stencila/hub/commit/6a0cd669ccc3f6e107fd743d06adc60b7fd1f5e9))
* **Worker:** Decode returned bytes from subprocess ([7be8161](https://github.com/stencila/hub/commit/7be8161160ca8fb7a540c9d4c94b339b4409e793))
* **Worker:** Fix handling on bytes input ([8fa59db](https://github.com/stencila/hub/commit/8fa59dbb283f0f4ba434574fd535c8fbf6edc334))
* **Worker:** Use requests.session for elife pull ([075f7a3](https://github.com/stencila/hub/commit/075f7a3c82ec6d20c4840aa41e2f443c1638867c))


### Features

* **Worker:** Add a Convert job ([7fbb23e](https://github.com/stencila/hub/commit/7fbb23e0f1a30558603c87a849cc7b660d748170))
* **Worker:** Add Decode and Encode jobs ([87dba8c](https://github.com/stencila/hub/commit/87dba8c76870644d9b7603f050ad29f1f97286d0))
* **Worker:** Add SubprocessJob ([10f5536](https://github.com/stencila/hub/commit/10f553666c16be08a91043b61238789bd1bdc306))
* **Worker:** SubprocessJob can accept stdin ([88b3b80](https://github.com/stencila/hub/commit/88b3b805c662ff5ec9c9657292a2a7f4a04de339))

## [2.23.1](https://github.com/stencila/hub/compare/v2.23.0...v2.23.1) (2020-05-13)


### Bug Fixes

* **Scheduler:** Update broker url ([454db11](https://github.com/stencila/hub/commit/454db11280d6ed830d824ca07faf3853aeb09960))
* **Worker:** Fetch figures in elife pull job ([a1331c4](https://github.com/stencila/hub/commit/a1331c4c8deb975d3ca2ed6ab1bff8bb3c11cca6))
* **Worker:** Ignore W503 linting rule ([d402977](https://github.com/stencila/hub/commit/d40297734988c74860d1fd2eb6b7d71a63ba7082))

# [2.23.0](https://github.com/stencila/hub/compare/v2.22.0...v2.23.0) (2020-05-11)


### Bug Fixes

* **Overseer:** Do not handles results (incl exceptions) ([f26f464](https://github.com/stencila/hub/commit/f26f464fcfd07d1628f0c633364d0babf5c63d64))


### Features

* **Worker:** Add KubernetesSession ([60b6f2a](https://github.com/stencila/hub/commit/60b6f2a15a0fb9244a09a07b87f23695cf45042b))

# [2.22.0](https://github.com/stencila/hub/compare/v2.21.2...v2.22.0) (2020-05-09)


### Features

* **Director:** Add queue model and associated API views ([39440c3](https://github.com/stencila/hub/commit/39440c3039cd8e88b1573cc75928fa602e59317e))

## [2.21.2](https://github.com/stencila/hub/compare/v2.21.1...v2.21.2) (2020-05-07)


### Bug Fixes

* **Overseer:** Add monitoring metrics ([42bf0b2](https://github.com/stencila/hub/commit/42bf0b268562846a4b06be2c190418c720686ce9))
* **Overseer:** File super() call; rename metric ([765362b](https://github.com/stencila/hub/commit/765362bc801e7169ac7c0b3c253cccf829619ea1))

## [2.21.1](https://github.com/stencila/hub/compare/v2.21.0...v2.21.1) (2020-05-06)


### Bug Fixes

* **Director:** Do not redirect internal URLs to HTTPS ([0bef198](https://github.com/stencila/hub/commit/0bef198cd68716d2e6f07878aab627446c36a478))

# [2.21.0](https://github.com/stencila/hub/compare/v2.20.7...v2.21.0) (2020-05-05)


### Bug Fixes

* **Monitor:** Specify the retention time and size ([e6dced0](https://github.com/stencila/hub/commit/e6dced0ed7d1236a4b3be142c9f08bafe6231a00)), closes [/github.com/helm/charts/blob/5597f269685b8e3220e2a181fbf002b1b1b819e0/stable/prometheus/values.yaml#L763-L765](https://github.com//github.com/helm/charts/blob/5597f269685b8e3220e2a181fbf002b1b1b819e0/stable/prometheus/values.yaml/issues/L763-L765)
* **Monitor:** Use metric_path so that monitoring self works ([3859a99](https://github.com/stencila/hub/commit/3859a997084c142c362484323f5a1562e453f9f7))


### Features

* **Director:** Enable Prometheus metrics ([1074428](https://github.com/stencila/hub/commit/1074428375c152f3972874b7099ac77bad86d821))
* **Monitor:** Add monitor service ([e8481f7](https://github.com/stencila/hub/commit/e8481f72fae624163f1ad7674f4ca591f85b32a6))
* **Router:** Add route to monitor ([f8dc056](https://github.com/stencila/hub/commit/f8dc0561b510309713395f6c1fd84fd79533eed4))

## [2.20.7](https://github.com/stencila/hub/compare/v2.20.6...v2.20.7) (2020-05-05)


### Bug Fixes

* **Director:** Update Encoda version ([2b1e38d](https://github.com/stencila/hub/commit/2b1e38d3036e90a091d8176da84a977975546d7c))

## [2.20.5](https://github.com/stencila/hub/compare/v2.20.4...v2.20.5) (2020-05-05)


### Bug Fixes

* **CI:** Specify docker-compose file ([269575b](https://github.com/stencila/hub/commit/269575befbe8c9479a0f5e8f210c282eaf1fd204))

## [2.20.4](https://github.com/stencila/hub/compare/v2.20.3...v2.20.4) (2020-05-05)


### Bug Fixes

* **deps:** update dependency @stencila/thema to v2.7.0 ([88648c6](https://github.com/stencila/hub/commit/88648c66e8657e3ca59b63f635ca811d27e60e6d))
* **deps:** update dependency pillow to v7.1.2 ([793a667](https://github.com/stencila/hub/commit/793a66735596dcf0b42b275249e1189ddd2ed57c))
* **Deps:** Upgrade Theme version ([3e63780](https://github.com/stencila/hub/commit/3e63780139fca8620acafb9324e36b0753b5b19c))
* **Router:** Custom error page and reporting for 502 and 504 erors ([20985e6](https://github.com/stencila/hub/commit/20985e649cdcef00e88156826fb0c2aac0ee5ff2))

## [2.20.3](https://github.com/stencila/hub/compare/v2.20.2...v2.20.3) (2020-05-04)


### Bug Fixes

* **Director config:** Add config vars for Google Storage ([14af313](https://github.com/stencila/hub/commit/14af313a796deb98f9fba3d98bafcf323a51d6b7))

## [2.20.2](https://github.com/stencila/hub/compare/v2.20.1...v2.20.2) (2020-05-04)


### Bug Fixes

* **Router:** Make entrypoint.sh executable ([7029ec2](https://github.com/stencila/hub/commit/7029ec22ede787449f2c84af1e408114b72a4051))

## [2.20.1](https://github.com/stencila/hub/compare/v2.20.0...v2.20.1) (2020-05-04)


### Bug Fixes

* **Director:** Add INTERCOM_ACCESS_TOKEN setting ([1c53363](https://github.com/stencila/hub/commit/1c533631f09d9dbee5829f1f8f887d112865c9e8))

# [2.20.0](https://github.com/stencila/hub/compare/v2.19.0...v2.20.0) (2020-05-03)


### Bug Fixes

* **AccountsJobsViewSet:** Turn on permisson class ([4cf74e7](https://github.com/stencila/hub/commit/4cf74e72a0dbde6ff75ac5df5b22f7fff9ca0fa9))
* **API exception handler:** Output traceback ([90e1d4e](https://github.com/stencila/hub/commit/90e1d4ee526ab2fd09c5be736439165eac797d23))
* **API URLs:** Prefix with carat to avoid clash ([ac4b8df](https://github.com/stencila/hub/commit/ac4b8df6293402562e6b82695116909d934a9038))
* **Director Job API:** Allow for setting of fields during update ([4dd0e9f](https://github.com/stencila/hub/commit/4dd0e9fc713a67a6aca0aeaa6cc5019e6bb10f35))
* **Director settings:** No prefix on env var ([d4e1538](https://github.com/stencila/hub/commit/d4e1538e4daa6364e17c740692cc4ba0d0e5dd8b))
* **Docker compose:** Make router accessible on host ([112d139](https://github.com/stencila/hub/commit/112d139ed45c33270d5553b97066bd05242f963a))
* **Jobs:** Call save on job serializer ([83d04be](https://github.com/stencila/hub/commit/83d04bec78e935fa151e80c2e08cc019fa0bf828))
* **Jobs connect:** Allow for Websockets ([35f33fb](https://github.com/stencila/hub/commit/35f33fb9ae3b0f62c73c36de86254609e117bc25))
* **Overseer:** Allow overseer to use basic auth to connect ([33835cf](https://github.com/stencila/hub/commit/33835cf2bf3f3aa6142ac88b5deab6b803fcb791))
* **Router:** Clear authorization header ([4795620](https://github.com/stencila/hub/commit/47956208e071d1302444578be23a7ed775593d4a))
* **Router:** Disable internal route to broker ([1c88a3f](https://github.com/stencila/hub/commit/1c88a3f9edb6f5784c231aa46da5d18cb60c005f))
* **Schedular Dockerfile:** Run as non-root user ([302bb56](https://github.com/stencila/hub/commit/302bb5626bafd4a5a6734315a1d56fe4846651b7))
* **Scheduler:** Add dockerignore to avoid pid files etc polluting container during development ([fc21b5f](https://github.com/stencila/hub/commit/fc21b5f04d9f0d94dbcbf89d9437c8da63ff945e))
* **Scheduler:** Configure beat_scheduler properly; add time zone awareness setting ([3ab621b](https://github.com/stencila/hub/commit/3ab621b83628b28ed608b3083dcd0718aa1e6938))
* **Scheduler:** Point to dev db ([ddd0abd](https://github.com/stencila/hub/commit/ddd0abd6a35bdc9a550c2bd168a9a743627d52e9))
* **Scheduler:** Specify log level INFO ([959d01d](https://github.com/stencila/hub/commit/959d01d2ce0dd635850e3b0820cf359cfcfae428))
* **Users API:** Differentiate between public and private user fields ([424f401](https://github.com/stencila/hub/commit/424f401fcd9d8337d0ae0ebf1329fce3a3a06f47))
* **Worker:** Ensure all modules are copied to Docker ([9eb568f](https://github.com/stencila/hub/commit/9eb568f9d369a444fe60a9784329a06af5a91857))
* **Worker:** Use Director API instead of Database connection ([67721e8](https://github.com/stencila/hub/commit/67721e83e4068959ce346a20eaeae278219f7100))


### Features

* **Broker:** Move from Redis to RabbitMQ for broker ([8d455bd](https://github.com/stencila/hub/commit/8d455bdec1e8512f4b1deed83e59cfa885c6802c))
* **Broker role:** Add broker role ([768f2e6](https://github.com/stencila/hub/commit/768f2e69fff96c4799228fd9e16e87cc4593b01e))
* **Database role:** Add a (currently) pseudo database role ([21a88d9](https://github.com/stencila/hub/commit/21a88d9d54fb49b309b8c213f6d8d85083b1c00d))
* **Deps:** Add django-celery-beat for periodic jobs ([e2880ca](https://github.com/stencila/hub/commit/e2880ca201ed9a9cd0a818135207aef999c56a71))
* **Job sessions:** Allow for connection to a job session ([fa1e9f1](https://github.com/stencila/hub/commit/fa1e9f1969d428675ff64564c06b7c19d9eece93))
* **Job sessions:** Allow for connection to a job session ([fb7a177](https://github.com/stencila/hub/commit/fb7a177a232d276fe2651b713d1d918f52bd004a))
* **Job zones:** Add zones for jobs to be run in ([fa6b1ff](https://github.com/stencila/hub/commit/fa6b1ff1685219a40d12110e603d79c56b2ac44f))
* **Jobs:** Add models and API endpoints for jobs ([74b516d](https://github.com/stencila/hub/commit/74b516d584f9427870b0c5adf67ca5ac8a523af3))
* **Jobs:** Allow for cancellation of jobs ([383f2f5](https://github.com/stencila/hub/commit/383f2f53a788b69927f1e8f768d4c7142327936b))
* **Jobs:** Record users who have connected to each job ([b6c151e](https://github.com/stencila/hub/commit/b6c151ec5628fddd32441d665e56eabc8d15cab4))
* **Jobs API:** Add endpoint to access per-account job broker ([233d879](https://github.com/stencila/hub/commit/233d879e27750bc130d93132dca9b7122671979e))
* **Monitor:** Add a monitor service ([584c1c8](https://github.com/stencila/hub/commit/584c1c8a4e37a6e919940bbc339829de898f5146))
* **Router:** Allow passing of DIRECTOR_URL as env var ([70999db](https://github.com/stencila/hub/commit/70999db373986cf9dcf7f3d3108323d310973fb4))
* **Scheduler:** Add role for scheduling periodic jobs ([4916405](https://github.com/stencila/hub/commit/491640558136d9193d3adf8ee6994c2713ff3074))
* **Users API:** Return the accounts for a user ([2e69a30](https://github.com/stencila/hub/commit/2e69a306fc7ccc5ec038533b94ae165e5e36eeec))
* **Worker:** Add Worker role for running jobs ([5eba8bd](https://github.com/stencila/hub/commit/5eba8bdd9c853d225e91fcb73ba4e7352c5999cf))
* **Worker:** Use executa base image ([974b734](https://github.com/stencila/hub/commit/974b734bf21b003c6a0818c3918f133586cb4094))
* **Workers:** Add initial API for recording workers and their status ([1074991](https://github.com/stencila/hub/commit/1074991bdf3a5fbe366e810660565f1b58cf053d))
* **Workers API:** Add endpoint to get worker status time series ([05e699b](https://github.com/stencila/hub/commit/05e699b8531f65a0fc833d98d07c95abc0e0a8fb))

# [2.19.0](https://github.com/stencila/hub/compare/v2.18.2...v2.19.0) (2020-04-28)


### Features

* Permissions improvements for AccountPermissionsMixin. Close [#391](https://github.com/stencila/hub/issues/391) ([a621c2c](https://github.com/stencila/hub/commit/a621c2c20a6c54e06c02800bd77200cde68cdbd1))

## [2.18.2](https://github.com/stencila/hub/compare/v2.18.1...v2.18.2) (2020-04-28)


### Bug Fixes

* **deps:** update dependency @stencila/thema to v2.3.0 ([2c0dc4d](https://github.com/stencila/hub/commit/2c0dc4dcd8c3411d6d446bef2ad453b3650a181e))
* **deps:** update dependency dj-stripe to v2.3.0 ([7a8d527](https://github.com/stencila/hub/commit/7a8d527791ce59bf569437f31ef2bc3b97695676))
* **deps:** update dependency google-api-python-client to v1.8.2 ([ce92687](https://github.com/stencila/hub/commit/ce92687864d0ca4bbc222dab0acd322b6e7eb7b6))
* **deps:** update dependency stencila-schema to v0.43.0 ([d036243](https://github.com/stencila/hub/commit/d036243cb3377785af973a5aa717280e37520a7a))
* **Deps:** Update Thema version ([b915bef](https://github.com/stencila/hub/commit/b915befb2497c5f8f078eee961b341857cddf1ae))

## [2.18.1](https://github.com/stencila/hub/compare/v2.18.0...v2.18.1) (2020-04-21)


### Bug Fixes

* Catching ValidationError instead of ValueError on google docs URL parse. Fix [#387](https://github.com/stencila/hub/issues/387) ([03900ba](https://github.com/stencila/hub/commit/03900bacf3e4b814a5c173239a32d71e20a8fed7))
* Limiting Project creation to users' Accounts in API ([66c0a7f](https://github.com/stencila/hub/commit/66c0a7f2549b9ed5df21311dd4c3979e3d19c7c0))
* Removed double project get call in API ([269437c](https://github.com/stencila/hub/commit/269437cf9322a952e04d15539b67b19b22f05124))
* Removed use of base get/post/delte methods on ProjectPermissionsMixin. Fix [#380](https://github.com/stencila/hub/issues/380) ([3d064a9](https://github.com/stencila/hub/commit/3d064a976cb9058f5c06898b46c53e07ec9d417f))
* **deps:** update dependency @stencila/thema to v2.2.7 ([06bb61b](https://github.com/stencila/hub/commit/06bb61bb9dcd1e802199044a64c9047889d1b2e0))

# [2.18.0](https://github.com/stencila/hub/compare/v2.17.0...v2.18.0) (2020-04-16)


### Bug Fixes

* **API:** Exception handler return 500 on error ([0867231](https://github.com/stencila/hub/commit/0867231a630f1e30de70877d99073756d8deb118))
* **API URLs:** Apply consistent approach to routers and trailing slashes ([ecc5023](https://github.com/stencila/hub/commit/ecc50236d54192b9ea09e239afd5c979185464a9))
* **Source models:** Type name in Q must be lower case ([5012229](https://github.com/stencila/hub/commit/5012229a6c8b1afc66a708fa953172f07e68ffb1))


### Features

* **Source models:** Add creator and created fields ([e96ba77](https://github.com/stencila/hub/commit/e96ba77e9fd72a7cb838e7bc10ade01c501e9209))
* **Source models:** Add parse_address and related methods ([0065dbd](https://github.com/stencila/hub/commit/0065dbda8545a8c879ff79ed9c4bcb98b5860c9d))
* **Sources admin:** Add admins for source types ([ae0c391](https://github.com/stencila/hub/commit/ae0c391e92dfbd92381596996d02e02d5ef54ad4))

# [2.17.0](https://github.com/stencila/hub/compare/v2.16.1...v2.17.0) (2020-04-15)


### Features

* **Deps:** Upgrade Encoda and Thema and add Encoda to package.json ([9b211eb](https://github.com/stencila/hub/commit/9b211eb5c39646c2363e32603446df3971aca48b))

## [2.16.1](https://github.com/stencila/hub/compare/v2.16.0...v2.16.1) (2020-04-13)


### Bug Fixes

* **deps:** update dependency psycopg2-binary to v2.8.5 ([c76cfb8](https://github.com/stencila/hub/commit/c76cfb89d9f47f3c7fef34c2998afd0a1026955c))

# [2.16.0](https://github.com/stencila/hub/compare/v2.15.0...v2.16.0) (2020-04-10)


### Bug Fixes

* **Snapshot archive:** Use API view and remove project archiver ([107cbc1](https://github.com/stencila/hub/commit/107cbc128fcc4284bbb70b8ab847d97fa67d3442))


### Features

* **Snapshots API:** Add archive formats for retrieval ([afdccc9](https://github.com/stencila/hub/commit/afdccc91fa75eb8f6e32a6d829bf713b823d307a))

# [2.15.0](https://github.com/stencila/hub/compare/v2.14.1...v2.15.0) (2020-04-10)


### Bug Fixes

* **Snapshots UI:** Provide link to newly created snapshot ([b438640](https://github.com/stencila/hub/commit/b438640fe89becceefaf65ef5be9326e4b391a62))
* **Status API:** Remove pagination ([5618192](https://github.com/stencila/hub/commit/5618192dfee21b7248b8964b0565c400f4cc12b9))


### Features

* **User API:** Add list and "me" user endpoints ([b413702](https://github.com/stencila/hub/commit/b413702ba0769305e8cb7f3eaf37f85cf03c8c88))

## [2.14.1](https://github.com/stencila/hub/compare/v2.14.0...v2.14.1) (2020-04-09)


### Bug Fixes

* **Dependencies:** Upgrade Encoda to 0.93.6 ([005b7ee](https://github.com/stencila/hub/commit/005b7eeae94acc30f419a820b346928e57945333))

# [2.14.0](https://github.com/stencila/hub/compare/v2.13.1...v2.14.0) (2020-04-09)


### Features

* **Accounts:** Add theme and hosts to settings ([786ebc9](https://github.com/stencila/hub/commit/786ebc992ac09cd4b25e90ee2a243447e39c237f))
* **Accounts, Projects:** Add hosts and theme settings ([61f2aca](https://github.com/stencila/hub/commit/61f2acac948daf089ea6c8dbd221dd8051d0eba6))
* **Snapshots API:** Add list, create and retrieve views ([3d7d720](https://github.com/stencila/hub/commit/3d7d72009833a1d86ffae173ddb4f1f9f6b7b3b2))
* **Snapshots API:** Add view to retrieve a view in a particular format. ([4b29071](https://github.com/stencila/hub/commit/4b29071a18eb9bf3b163541f8c2f59ef608e0204))

## [2.13.1](https://github.com/stencila/hub/compare/v2.13.0...v2.13.1) (2020-04-07)


### Bug Fixes

* **Build:** Add !assets/*.py to .dockerignore ([a073486](https://github.com/stencila/hub/commit/a073486927a14dbf7900e0d68e180e120cb06521))
* **Build:** Write thema.py so that black will not format it ([b6448e6](https://github.com/stencila/hub/commit/b6448e6f29c4534f712a5cfd0f2a7810ba0dfa21))

# [2.13.0](https://github.com/stencila/hub/compare/v2.12.0...v2.13.0) (2020-04-07)


### Bug Fixes

* **Build:** Run prepare.js properly; avoid formatting generated files ([6e7c512](https://github.com/stencila/hub/commit/6e7c5125e074d119c1232ec988c76b5cc4882652))
* **Deps:** Upgrade Thema and Encoda version ([5a1c131](https://github.com/stencila/hub/commit/5a1c131d6199bc700d21184901605e811b027e4e))
* **Nodes:** Override default CamelCaseJSONParser ([c7de0c3](https://github.com/stencila/hub/commit/c7de0c3a67704d3ebe0add61e9d9a7f6783d4402))
* **Thema:** Use a specific version of Thema as a dependency. ([34b2460](https://github.com/stencila/hub/commit/34b24607f70f4a006a090e4709d3af806bf470a6)), closes [#367](https://github.com/stencila/hub/issues/367)


### Features

* **Nodes:** Add admin view ([1030ad4](https://github.com/stencila/hub/commit/1030ad4d66db5087a7ade3efa06efd6c43e46d1c))

# [2.12.0](https://github.com/stencila/hub/compare/v2.11.0...v2.12.0) (2020-04-06)


### Bug Fixes

* **Nodes:** Allow for node project being null ([939377a](https://github.com/stencila/hub/commit/939377a6d25b9d7c6174e6801627093b7a123422)), closes [#370](https://github.com/stencila/hub/issues/370)


### Features

* **Nodes:** Default app to api and add creator to complete HTMl view. ([24a1e12](https://github.com/stencila/hub/commit/24a1e1226f44abb6e5a2da3fa756a95793e806d3))

# [2.11.0](https://github.com/stencila/hub/compare/v2.10.0...v2.11.0) (2020-04-06)


### Bug Fixes

* **Account profile:** Revert to using pk ([47d79c0](https://github.com/stencila/hub/commit/47d79c08dd11741a9a2060a550ad31a6c4f5723a)), closes [/github.com/stencila/hub/pull/357#discussion_r403574787](https://github.com//github.com/stencila/hub/pull/357/issues/discussion_r403574787)
* **API URLs:** Place in seperate module ([6b4b840](https://github.com/stencila/hub/commit/6b4b840a3f4a2895e063757fc0e866e5f125c2df))
* **Nodes:** Add Encoda as a node creating app ([182a5a9](https://github.com/stencila/hub/commit/182a5a9e22ad84686a7a6960a4077b079aa12df8))
* **Nodes:** Add simple sign in message ([a9777f8](https://github.com/stencila/hub/commit/a9777f8f05990fda65692de750daafb540c66c54))
* **Pages titles:** Make more consistent ([c1efcf9](https://github.com/stencila/hub/commit/c1efcf9666c1949fdd60edde9c43f1d6619392cf))


### Features

* **Nodes:** Add app and doc fields; make serializers DRYer ([511c9b4](https://github.com/stencila/hub/commit/511c9b4e6c6787827f7db2f4340a451b0dce8537))
* **Nodes:** Add content for complete view ([d873c85](https://github.com/stencila/hub/commit/d873c85703e69651d32f2476e3b5cfb00de3bc28))
* **Nodes:** Add modes and API views for project nodes ([ad250f1](https://github.com/stencila/hub/commit/ad250f14e245d06f4f049e728180cc35d3e0d58c))
* **ProjectPermissionsMixin:** Add is_permitted method ([948a33e](https://github.com/stencila/hub/commit/948a33e20d449060a8392eb8d4d969de1b9b3810))

# [2.10.0](https://github.com/stencila/hub/compare/v2.9.5...v2.10.0) (2020-04-06)


### Bug Fixes

* **API docs:** Fix text and serve docs from /api ([1d4d1c2](https://github.com/stencila/hub/commit/1d4d1c23c87df5512ce59f7d1ca2b20854eb68bb))


### Features

* Passing current directory to GitHub link screen. Close [#366](https://github.com/stencila/hub/issues/366) ([7b3d56c](https://github.com/stencila/hub/commit/7b3d56cb66fcc9744d0a141173322ca7cdf67ec2))

## [2.9.5](https://github.com/stencila/hub/compare/v2.9.4...v2.9.5) (2020-04-05)


### Bug Fixes

* **Sign in:** Should respect the next parameter. Close [#368](https://github.com/stencila/hub/issues/368) ([cb5c1a9](https://github.com/stencila/hub/commit/cb5c1a97065f90ba2729625c8071d4ff9792601a))

## [2.9.4](https://github.com/stencila/hub/compare/v2.9.3...v2.9.4) (2020-04-04)


### Bug Fixes

* Showing message to contact support if Google token can't be refreshed. Fix [#352](https://github.com/stencila/hub/issues/352) ([8eda8e5](https://github.com/stencila/hub/commit/8eda8e5762b3ed1cf4e298f1faa3ec72b6c5ff5e))

## [2.9.3](https://github.com/stencila/hub/compare/v2.9.2...v2.9.3) (2020-04-04)


### Bug Fixes

* **deps:** update dependency django to v2.2.12 ([d3b9b40](https://github.com/stencila/hub/commit/d3b9b40435ba20ef133fb9b9f51c264ea9306373))
* **deps:** update dependency pillow to v7.1.1 ([e72021b](https://github.com/stencila/hub/commit/e72021b68e326e520fe4c4733dd3862d4f2283fd))

## [2.9.2](https://github.com/stencila/hub/compare/v2.9.1...v2.9.2) (2020-04-03)


### Bug Fixes

* Added !/general to .dockerignore ([a92a1a1](https://github.com/stencila/hub/commit/a92a1a1d16ff7784a9ec318d53c7d74de2ccd8f8))

## [2.9.1](https://github.com/stencila/hub/compare/v2.9.0...v2.9.1) (2020-04-03)


### Bug Fixes

* Fix for non-root Sources showing up in root directory, close [#358](https://github.com/stencila/hub/issues/358) ([d516908](https://github.com/stencila/hub/commit/d516908ce87cd5c3d71b8c49b4b8a9e722960c35))

# [2.9.0](https://github.com/stencila/hub/compare/v2.8.0...v2.9.0) (2020-04-02)


### Bug Fixes

* **API status:** Handle db connection error during deployment shutdown ([d24e796](https://github.com/stencila/hub/commit/d24e796e427cf15313eb912bf645ab2ed5641a0e)), closes [#336](https://github.com/stencila/hub/issues/336)


### Features

* **Admin:** Add dates to user admin list display ([f60b1af](https://github.com/stencila/hub/commit/f60b1afefed5662e7287c61b648255e326831ab1))

# [2.8.0](https://github.com/stencila/hub/compare/v2.7.1...v2.8.0) (2020-04-01)


### Bug Fixes

* **Policies:** Link to externally hosted policies ([3777d8b](https://github.com/stencila/hub/commit/3777d8be50302018d26a917bc5e522b4b33eb34c))


### Features

* **Analytics:** Adds PostHog integration ([61513ee](https://github.com/stencila/hub/commit/61513eeacf0ce2a33d9f313d578d84e0175fc89c))

## [2.7.1](https://github.com/stencila/hub/compare/v2.7.0...v2.7.1) (2020-04-01)


### Bug Fixes

* **Open:** Keep media files for JSON too ([0f68047](https://github.com/stencila/hub/commit/0f6804767c73e7e3b101c60e4b265b0458fe8e94))

# [2.7.0](https://github.com/stencila/hub/compare/v2.6.0...v2.7.0) (2020-04-01)


### Bug Fixes

* **Deps:** Upgrade Encoda to 0.94.3 ([6b0f815](https://github.com/stencila/hub/commit/6b0f8150ef67de3b738d03fb5ab7e842a1b2d6d2))
* **Open:** Revert to using main block ([732b045](https://github.com/stencila/hub/commit/732b045d6e2af53a4334b075077e56e23c509f2e))


### Features

* **Open:** Allow repro-PDFs to be uploaded ([660f347](https://github.com/stencila/hub/commit/660f3479dd9c4fd93d5e37e05ed317d48d43d5d6))

# [2.6.0](https://github.com/stencila/hub/compare/v2.5.4...v2.6.0) (2020-04-01)


### Bug Fixes

* Remove Pull Source Button ([bcf9fe7](https://github.com/stencila/hub/commit/bcf9fe764ecfc9097d3ef0876f6a5147a87f1c0e))
* Snapshot files button layout ([0ba06d3](https://github.com/stencila/hub/commit/0ba06d39299d5b30a948bded023dd969ef862cd4))


### Features

* Moved snapshot action into a modal and added tag ([18b2b94](https://github.com/stencila/hub/commit/18b2b9437b736ac890e9ba21fc3cad5cdd15514e))
* Removed standalone archives view and added zip downloading to snapshots ([d29e310](https://github.com/stencila/hub/commit/d29e3107d460b8b361ee0149aa6b53e949fe921a))

## [2.5.4](https://github.com/stencila/hub/compare/v2.5.3...v2.5.4) (2020-03-31)


### Bug Fixes

* **API Status:** Handle db connection error during warmup. ([cbb7f51](https://github.com/stencila/hub/commit/cbb7f511eb943ec967f1a110b0fb24bff05d66b3)), closes [#336](https://github.com/stencila/hub/issues/336)

## [2.5.3](https://github.com/stencila/hub/compare/v2.5.2...v2.5.3) (2020-03-31)


### Bug Fixes

* Fixed fetching of PublishedItem in preview, when the item has been previewed > once in snapshots. Close [#330](https://github.com/stencila/hub/issues/330) ([1a4ac5d](https://github.com/stencila/hub/commit/1a4ac5d143e2dee26b2e3179b9a349360f95fdeb))

## [2.5.2](https://github.com/stencila/hub/compare/v2.5.1...v2.5.2) (2020-03-31)


### Bug Fixes

* Deleting PublishedItem when its Source is deleted, fix [#335](https://github.com/stencila/hub/issues/335) ([838f753](https://github.com/stencila/hub/commit/838f7537476a14652018ec647c8e3e248890f7f8))

## [2.5.1](https://github.com/stencila/hub/compare/v2.5.0...v2.5.1) (2020-03-30)


### Bug Fixes

* **Open:** Replace beta signup with signin ([5bee7c3](https://github.com/stencila/hub/commit/5bee7c3275a41e1dc6013794e22ddb7620a0a33c))
* **Themes:** Upgrade to Thema 1.16 ([0c0b9c0](https://github.com/stencila/hub/commit/0c0b9c0a9c4a941425e89c2533a73820090918b8))

# [2.5.0](https://github.com/stencila/hub/compare/v2.4.1...v2.5.0) (2020-03-30)


### Bug Fixes

* **Deps:** Update Encoda to 0.93.2 ([12a2ea9](https://github.com/stencila/hub/commit/12a2ea928450b1e247810e1b8110dae629f96ab6))


### Features

* **Open:** Add PDF download; improve styling ([29ec6bf](https://github.com/stencila/hub/commit/29ec6bf14d62f85c3a56a4674d1e52fc744feab3))
* **Open:** Allow opening of eLife and PLoS JATS articles ([91af886](https://github.com/stencila/hub/commit/91af88608581645aa071694efebf39eaf37fefc4))
* **Open:** Integrate /open into main app ([67f056f](https://github.com/stencila/hub/commit/67f056fd4803c38e07924171027d11e2d9dc376f))

## [2.4.1](https://github.com/stencila/hub/compare/v2.4.0...v2.4.1) (2020-03-30)


### Bug Fixes

* **Error page:** Fix typo and in the process rewrite text ([6322f71](https://github.com/stencila/hub/commit/6322f71f42ce79f15d8ab0a2777d80125a63b0aa))
* **Error page:** Fix typo and in the process rewrite text [skip ci] ([474f7ff](https://github.com/stencila/hub/commit/474f7ff219db041432c1f4d2246bd6c124773891))
* **Project admin:** Remove obsolete archive field. ([15e4322](https://github.com/stencila/hub/commit/15e432236da2c69a4ad85d1965ede69a2eceee10))

# [2.4.0](https://github.com/stencila/hub/compare/v2.3.5...v2.4.0) (2020-03-29)


### Bug Fixes

* **Error logging:** Upgrade to sentry-sdk; use message for migrations, not exception ([89b64c6](https://github.com/stencila/hub/commit/89b64c61cf613c8feb301146edb23a461f153e3d)), closes [#336](https://github.com/stencila/hub/issues/336) [#350](https://github.com/stencila/hub/issues/350)


### Features

* **Error page:** Improve 500 page and add feedback form ([9c5555c](https://github.com/stencila/hub/commit/9c5555cacbe0a7200530d1c80a9b371bf9bfdbd1)), closes [#69](https://github.com/stencila/hub/issues/69)

## [2.3.5](https://github.com/stencila/hub/compare/v2.3.4...v2.3.5) (2020-03-29)


### Bug Fixes

* **deps:** update dependency django-avatar to v5 ([a7206b9](https://github.com/stencila/hub/commit/a7206b9446d5bb9682730e394ad81e993cbbdbf1))
* **deps:** update dependency pillow to v7 ([2102769](https://github.com/stencila/hub/commit/21027690f651baee722bf56a06495c99b87c1645))
* **deps:** update dependency shortuuid to v1 ([0150a58](https://github.com/stencila/hub/commit/0150a58ac98ae70e64d714d2605e0a408bee39d3))

## [2.3.4](https://github.com/stencila/hub/compare/v2.3.3...v2.3.4) (2020-03-29)


### Bug Fixes

* **deps:** update dependency django-extensions to v2.2.9 ([91636ac](https://github.com/stencila/hub/commit/91636ac2a248f5e9d358d8710569bc74184c8c77))
* **deps:** update dependency pillow to v6.2.2 ([0f3dd8d](https://github.com/stencila/hub/commit/0f3dd8d3e8c7c10be9773c1e1320efebe563e94e))
* **deps:** update dependency psycopg2-binary to v2.8.4 ([e6abb14](https://github.com/stencila/hub/commit/e6abb14d0279b8d39cf337548b4ffa77b2d514ef))
* **deps:** update dependency requests to v2.23.0 ([4458a23](https://github.com/stencila/hub/commit/4458a234cfb4951404a302fadca45e869d5fa4c8))

## [2.3.3](https://github.com/stencila/hub/compare/v2.3.2...v2.3.3) (2020-03-29)


### Bug Fixes

* **File browser:** Improve consistency in delete, unlink and rename modals ([c584c66](https://github.com/stencila/hub/commit/c584c664d910d1336c51393c7e575a45eb994448))
* **File browser:** Open all files in a new window ([626682d](https://github.com/stencila/hub/commit/626682d8ca0d7685e1649e123c4a0f7c0ea19544))
* **File browser:** Simplify filename conflict notif; fade away on rename ([60e2754](https://github.com/stencila/hub/commit/60e2754e23c8c5b15b8af2554cd84cccd30ad01a))
* **File browser:** Simplify Save As modal ([2a89b95](https://github.com/stencila/hub/commit/2a89b95750f7251d21d8fceee6a386056ed23b9d))
* **Open:** Remove Executa as unused. ([faa0bc0](https://github.com/stencila/hub/commit/faa0bc0204b8d38136b438c1482461ca43b26ddb)), closes [#349](https://github.com/stencila/hub/issues/349)
* Redesign file action menu with Save As Other ([752be4b](https://github.com/stencila/hub/commit/752be4bccaea60a1d806d3463cbfee5b2db13504))

## [2.3.2](https://github.com/stencila/hub/compare/v2.3.1...v2.3.2) (2020-03-28)


### Bug Fixes

* Create team view, fix [#337](https://github.com/stencila/hub/issues/337) ([d6b3a95](https://github.com/stencila/hub/commit/d6b3a954038faebd5a46d3d21975f21435ceb26f))

## [2.3.1](https://github.com/stencila/hub/compare/v2.3.0...v2.3.1) (2020-03-26)


### Bug Fixes

* **Open:** Correct elife theme name ([f05f766](https://github.com/stencila/hub/commit/f05f766b528d2ec86ea26fc6ccfe188b65b68ea6))

# [2.3.0](https://github.com/stencila/hub/compare/v2.2.1...v2.3.0) (2020-03-25)


### Bug Fixes

* **Deps:** Upgrade Thema to 1.15.1 ([51abf87](https://github.com/stencila/hub/commit/51abf879fb549bc4860fbb823dba956a95cc883e))


### Features

* **File preview:** Allow theme to be set using query parameter ([4297492](https://github.com/stencila/hub/commit/42974927ab7a867105e8c50f64d34209283da77f))

## [2.2.1](https://github.com/stencila/hub/compare/v2.2.0...v2.2.1) (2020-03-25)


### Bug Fixes

* **Deps:** Upgrade Encoda to 0.92.0 ([944c440](https://github.com/stencila/hub/commit/944c440fe1f258b88b1b630572869695ca372870))

# [2.2.0](https://github.com/stencila/hub/compare/v2.1.0...v2.2.0) (2020-03-25)


### Bug Fixes

* **API docs:** Improve  styling of docs ([2cf112a](https://github.com/stencila/hub/commit/2cf112abe55869aa7f1d138e5a85ba55863ec2ba))


### Features

* Account Admin users now get OWN permission on projects in their Account ([e9bb00c](https://github.com/stencila/hub/commit/e9bb00c6912b9ed348f01f90b0d7f6c244ae0298))

# [2.1.0](https://github.com/stencila/hub/compare/v2.0.3...v2.1.0) (2020-03-25)


### Features

* **API:** Add endpoints for managing authentication tokens. ([3ef9233](https://github.com/stencila/hub/commit/3ef9233f36c1167c9364ffcda899249b75f0208a))

## [2.0.3](https://github.com/stencila/hub/compare/v2.0.2...v2.0.3) (2020-03-25)


### Bug Fixes

* **Deps:** Upgrade to using Python 3.7 and Ubuntu 19.10 ([33f5ba1](https://github.com/stencila/hub/commit/33f5ba1e27cac068bb3c807bd6dd7a193cafa8ba))

## [2.0.2](https://github.com/stencila/hub/compare/v2.0.1...v2.0.2) (2020-03-24)


### Bug Fixes

* Manually returning 200 OK for GoogleHC user agents ([765026c](https://github.com/stencila/hub/commit/765026cd78a4e4583c5d3b40333f42e3e97b5528))

## [2.0.1](https://github.com/stencila/hub/compare/v2.0.0...v2.0.1) (2020-03-24)


### Bug Fixes

* **Settings:** Update path to status check ([650c44d](https://github.com/stencila/hub/commit/650c44d68140809be7f74ccffc6b3e09b19f29f5))

# [2.0.0](https://github.com/stencila/hub/compare/v1.1.1...v2.0.0) (2020-03-24)


### Bug Fixes

* **Settings:** Do not require beta token setting in prod ([623aafb](https://github.com/stencila/hub/commit/623aafb2732fc5a01a0691d0c62c78c08148dc50))


### Features

* **API:** Use camel casing; return more user details when granting auth token. ([93c1900](https://github.com/stencila/hub/commit/93c190063927ad903b60f159f7f4ca38b11188ff))


### BREAKING CHANGES

* **API:** change to camelCasing may break existing API clients

## [1.1.1](https://github.com/stencila/hub/compare/v1.1.0...v1.1.1) (2020-03-23)


### Bug Fixes

* **deps:** update dependency google-api-python-client to v1.8.0 ([276935b](https://github.com/stencila/hub/commit/276935bfa5a4701ef72af4b000de82ba07d139c9))

# [1.1.0](https://github.com/stencila/hub/compare/v1.0.0...v1.1.0) (2020-03-23)


### Bug Fixes

* **Settings:** Use unpkg.com CDN in prod ([44177be](https://github.com/stencila/hub/commit/44177be9ba2ec3fa985573c91598f0763bf82209))

# [1.0.0](https://github.com/stencila/hub/compare/v1.0.0...v0.9.2) (2020-03-23)


### Bug Fixes

* **Deps:** Django extensions is prod dep ([4c22046](https://github.com/stencila/hub/commit/4c22046427dc1b22476d4a7d8086a752ad240461))

## [0.9.2](https://github.com/stencila/hub/compare/v0.9.1...v0.9.2) (2020-03-23)


### Bug Fixes

* **deps:** update dependency django to v2.2.11 ([65a3ede](https://github.com/stencila/hub/commit/65a3ede36e0678b63a057e8bb0ad8d9092c88e79))
* **deps:** update dependency django-allauth to v0.41.0 ([924a9fa](https://github.com/stencila/hub/commit/924a9fa0a547c3a154ca1ae96d11336ca99f10fd))
* **deps:** update dependency django-configurations to v2.2 ([2b55b7e](https://github.com/stencila/hub/commit/2b55b7e5d4aca669edf844f9beabdd3c35e61467))
* **deps:** update dependency django-crispy-forms to v1.9.0 ([22be7ab](https://github.com/stencila/hub/commit/22be7ab1a05a9d252488f851d5ca5c5f34f6ffc0))
* **User search:** Account for change in API ([3ed7c73](https://github.com/stencila/hub/commit/3ed7c7303c0f9ba1fa0813a835d850bc362f6d02))
* **User search API:** Add additional fields to result and alter fields searched ([8211723](https://github.com/stencila/hub/commit/8211723c1603ecc6a3ad5cdd853c6342fad5bda2))

## [0.9.1](https://github.com/stencila/hub/compare/v0.9.0...v0.9.1) (2020-03-21)


### Bug Fixes

* **deps:** update dependency dj-stripe to v2.2.3 ([cb0f725](https://github.com/stencila/hub/commit/cb0f72594ef09d57525d93b76fad64d1128f2c96))
* **deps:** update dependency django-debug-toolbar to v2.2 ([ec71452](https://github.com/stencila/hub/commit/ec71452d543175be8feba553e131bd96d214b37c))
* **deps:** update dependency django-extensions to v2.2.8 ([34baf19](https://github.com/stencila/hub/commit/34baf1926e637ab5d09ed918f402a0f28c3011b2))
* **deps:** update dependency django-intercom to v0.1.3 ([1d117f2](https://github.com/stencila/hub/commit/1d117f2269ae1ffeba78bb0e08228ef4c59d4b90))
* **deps:** update dependency django-sendgrid-v5 to v0.8.1 ([3c746e5](https://github.com/stencila/hub/commit/3c746e59acbb01d87856b643901c58a91dc91239))
* **Deps:** Update stencila-schema ([a50bd30](https://github.com/stencila/hub/commit/a50bd3068e97cb6cd26fb61268a9594293e50a80))

# [0.9.0](https://github.com/stencila/hub/compare/v0.8.27...v0.9.0) (2020-03-21)


### Bug Fixes

* **API:** Normalize API errors ([699c190](https://github.com/stencila/hub/commit/699c190c5c94d4f878451b6b1b13f72b1217ce73))
* **API Auth:** Remove JWTs as an authorization option ([a4ab72e](https://github.com/stencila/hub/commit/a4ab72e981c98915bb701c527dcccf1253ad58ba))
* **API docs:** Ensure schema is publically accessible; hide auth buttin in swagger ([fe5a5ad](https://github.com/stencila/hub/commit/fe5a5adcf2005189d2d6ea7115459ab463ddf5bf))
* **API docs:** Hide routes not being reviewed in this round ([787d3c5](https://github.com/stencila/hub/commit/787d3c5ac6d249a25f4026b39f7baf4329c0fef3))
* **API URLs:** Allow optional trailing slash ([c12117d](https://github.com/stencila/hub/commit/c12117d5ba16dfaf9efb78bd1bdddc8f3a9e4e8a))
* **File browser:** Remove reference to removed function ([c019242](https://github.com/stencila/hub/commit/c019242429184ce560757120b8c64cb2e2a49fc9))
* Filtering by project event status ([3cdf138](https://github.com/stencila/hub/commit/3cdf13809828a9a82d9e73f89e22bb2677de4b3e))
* Record status for completed SNAPSHOT events. ([30824b3](https://github.com/stencila/hub/commit/30824b3ffc8599ae4d7c3bb307c8cce36ac8ef08))
* Recording ProjectEvents for anonymous users ([2d479e4](https://github.com/stencila/hub/commit/2d479e43ee81cef085b46a9b5e325299e778445d))
* Remove pesudo-terminal code from page overview ([4ac79e0](https://github.com/stencila/hub/commit/4ac79e01f822ad71acaff59dd3549a0515fc0978))
* **Migrations:** Remove the reference to the deleted checkouts app ([51557d5](https://github.com/stencila/hub/commit/51557d5b2a19d9442c94f6917b81af886ec858a0))


### Features

* **API:** Add and document additional project fields ([8032f6e](https://github.com/stencila/hub/commit/8032f6e366d582dd6c917efced11a129b23dff28))
* **API:** Complete initial OpenID JWT granting ([df224f6](https://github.com/stencila/hub/commit/df224f6adb1e69ffb543946cc2ccf9cfcd339009))
* **API:** Use knox to provide user authentication tokens "UATs" ([e836525](https://github.com/stencila/hub/commit/e836525c784fd12ace1ea9d97771e396c7f4d4b3))
* **API Tokens:** Allow for refreshing and revoking both token types ([edf2f4e](https://github.com/stencila/hub/commit/edf2f4e91aa4f57492d082a2257c2d2505fb3be8))
* **API Tokens:** Generate JWT token from Google auth JWT ([23b0e3e](https://github.com/stencila/hub/commit/23b0e3ea737d6c7e820011c51eabd0d59f9af4b5))
