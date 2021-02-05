## [4.31.2](https://github.com/stencila/hub/compare/v4.31.1...v4.31.2) (2021-02-05)


### Bug Fixes

* **deps:** update dependency @vizuaalog/bulmajs to v0.12.1 ([3e6b6be](https://github.com/stencila/hub/commit/3e6b6be96a215a0365bc88763bf707cafa1078fa))

## [4.31.1](https://github.com/stencila/hub/compare/v4.31.0...v4.31.1) (2021-02-03)


### Bug Fixes

* **Files admin:** Allow upstreams to be blank in admin ([317ff42](https://github.com/stencila/hub/commit/317ff4201d5fc910e045e2219118621b7b14376a))

# [4.31.0](https://github.com/stencila/hub/compare/v4.30.2...v4.31.0) (2021-02-03)


### Features

* **Project admin:** Add search and filters ([325b4e6](https://github.com/stencila/hub/commit/325b4e6ffd21269aeb602e5d088ec19fee5dfccc))
* **Snapshot and file admin:** Improved filtering and editing ([8ba9db2](https://github.com/stencila/hub/commit/8ba9db26d9e95efbd0b381a77143caf7d7137edd))

## [4.30.2](https://github.com/stencila/hub/compare/v4.30.1...v4.30.2) (2021-02-03)


### Bug Fixes

* **Deps:** Update Stencila Components ([65b8540](https://github.com/stencila/hub/commit/65b8540133ba348be77510e4a73be6db5dec7956))
* **Files:** Add icons classes for file types ([e92c360](https://github.com/stencila/hub/commit/e92c3607e79c07ce844b7f434c8ab0e0e8bc7f33)), closes [#988](https://github.com/stencila/hub/issues/988)

## [4.30.1](https://github.com/stencila/hub/compare/v4.30.0...v4.30.1) (2021-02-02)


### Bug Fixes

* **Account plans:** Listen to `customer.subscription.created` events ([af57eff](https://github.com/stencila/hub/commit/af57efffc0d12cd15d3014d8e57f8844c12e637c)), closes [#986](https://github.com/stencila/hub/issues/986)
* **Plans:** Display as integer ([45d9088](https://github.com/stencila/hub/commit/45d90883a3c525be15f3403199eb3f2ee550221c)), closes [#983](https://github.com/stencila/hub/issues/983)
* **Plans:** Only allow account OWNER to update a plan ([d5ad32d](https://github.com/stencila/hub/commit/d5ad32db49d3ddb2a14ab1eb55f7a512b62b8953)), closes [#985](https://github.com/stencila/hub/issues/985)

# [4.30.0](https://github.com/stencila/hub/compare/v4.29.3...v4.30.0) (2021-02-01)


### Bug Fixes

* **API:** Avoid schema generation warning ([09fbb84](https://github.com/stencila/hub/commit/09fbb84613b2bd611b5c729dfdf8ac6d8d2b46c2))
* **Subscriptions:** It is necessary to create / sync with Stripe directly ([2e998ed](https://github.com/stencila/hub/commit/2e998ed8da30ef0a06a953e5fc044fe165655b42))
* **Webhooks:** Upgrade and downgrade tiers ([d8ece3e](https://github.com/stencila/hub/commit/d8ece3eb357ce519ce46da9c63a3b02feed5d4e7))


### Features

* **Account tiers:** Link tiers to Stripe products ([bc51143](https://github.com/stencila/hub/commit/bc51143d3eab56654743380bf0d31b19e449fb12))
* **Accounts:** Add billing email and link to customer instance ([51aa849](https://github.com/stencila/hub/commit/51aa84971619a23ffcfa1b0f1de3c00e032ac314))
* **Billing:** Redirect user to the customer billing portal ([5826839](https://github.com/stencila/hub/commit/582683966041d5e3a1d82855a7882115c640de14))
* **Subscriptions:** Add subscription page ([4a677c5](https://github.com/stencila/hub/commit/4a677c5a0a1c54fdd1ab7da2848d3c32b7ccb16b))

## [4.29.3](https://github.com/stencila/hub/compare/v4.29.2...v4.29.3) (2021-01-31)


### Bug Fixes

* **deps:** pin dependency pyjwt to ==1.7.1 ([9c56bc5](https://github.com/stencila/hub/commit/9c56bc5c8d03964b568abce9e60d1a075079de4b))
* **deps:** update dependency bulma to v0.9.2 ([e789f79](https://github.com/stencila/hub/commit/e789f796da9d7759377b30f40c550a3e91542064))
* **deps:** update dependency dj-stripe to v2.4.2 ([7f618f1](https://github.com/stencila/hub/commit/7f618f16fbeec9da919a20a033e386d938fa8ad3))
* **deps:** update dependency django-cors-headers to v3.7.0 ([07235ed](https://github.com/stencila/hub/commit/07235ed3c4619532d3d9b142aa9d3c03829c6337))
* **deps:** update dependency setuptools to v52 ([4aa3ce7](https://github.com/stencila/hub/commit/4aa3ce728f52ef7360ae81b9f48a44e892f8b429))
* **deps:** update dependency stencila-schema to v1 ([d634068](https://github.com/stencila/hub/commit/d634068935757727d96e344872860e40cde868c9))
* **deps:** update dependency urllib3 to v1.26.3 ([da28748](https://github.com/stencila/hub/commit/da28748ad258d23332d70ae4b1908ba3d9c84076))

## [4.29.2](https://github.com/stencila/hub/compare/v4.29.1...v4.29.2) (2021-01-30)


### Bug Fixes

* **deps:** update dependency @stencila/executa to v1.15.7 ([455014a](https://github.com/stencila/hub/commit/455014ab9edbe9a086da41fc5fc32be13ab3ba9b))

## [4.29.1](https://github.com/stencila/hub/compare/v4.29.0...v4.29.1) (2021-01-28)


### Bug Fixes

* **UserFlow syncing:** Throttle requests ([3b09766](https://github.com/stencila/hub/commit/3b09766e64b876ff05b8ea6610cc4bc16d7a5955)), closes [#966](https://github.com/stencila/hub/issues/966)

# [4.29.0](https://github.com/stencila/hub/compare/v4.28.1...v4.29.0) (2021-01-27)


### Bug Fixes

* **Account tiers:** Shift down tier prices and summaries ([48e22ec](https://github.com/stencila/hub/commit/48e22ec21fb09f7e7337f2483cd7c8bc90ecf6e0))


### Features

* **Pricing:** Remove notice about Waiting Lists for accounts ([b71de09](https://github.com/stencila/hub/commit/b71de090d25cbad9de6b189942a83867d0c6740e))

## [4.28.1](https://github.com/stencila/hub/compare/v4.28.0...v4.28.1) (2021-01-27)


### Bug Fixes

* **Account settings:** Fix for change in template name ([731f15a](https://github.com/stencila/hub/commit/731f15a737695c6f20e5bb435177042ff47fed5b))
* **Projects:** Undo erroneous renaming of template ([d09711a](https://github.com/stencila/hub/commit/d09711a0f327eaed232eaf64fa976666216fcd64))

# [4.28.0](https://github.com/stencila/hub/compare/v4.27.15...v4.28.0) (2021-01-26)


### Bug Fixes

* **Account settings sub menu:** Avoid double stylization on desktop view ([3656dc5](https://github.com/stencila/hub/commit/3656dc53076765f8059d4706b3dd66c5774790aa))
* **Account settings sub menu:** only show on settings pages ([9ee299e](https://github.com/stencila/hub/commit/9ee299ecfa9a32b68148d0264f2e4cfee1100954))
* **CSS:** Style secondary nav in Profile Settings view ([be72e7a](https://github.com/stencila/hub/commit/be72e7aef20059f0b86e604a34926e6c01352966))
* **deps:** update dependency userflow.js to v2 ([11a67ae](https://github.com/stencila/hub/commit/11a67ae6209cc7b7928cfa19924febdcdceec93f))
* **Orgs:** Update includes with new template name ([166c68e](https://github.com/stencila/hub/commit/166c68e6fe20da16f0fb202f094765b4745e6776))
* **User settings:** Ensure login required; fix tests ([1c75cd9](https://github.com/stencila/hub/commit/1c75cd98a404a511227125ef60ba859ca574e07d))
* **User settings:** Remove semi-bold style ([0df2410](https://github.com/stencila/hub/commit/0df241021d69fc0899ad254fe8e0ffe13c03bcab))
* **User settings:** Use accounts/base.html for user settings pages ([4b13b6c](https://github.com/stencila/hub/commit/4b13b6cbafb0a80770709ece90f97fdce71e1058))
* **Userflow:** Only instantiate Userflow for authenticated users ([ac6968a](https://github.com/stencila/hub/commit/ac6968a63f0f5c626bb5e521849e3801702c024f))


### Features

* **Account settings:** Separate profile and publishing settings ([95dfd37](https://github.com/stencila/hub/commit/95dfd37fd7e19e7473df885e04a8febe4db5a613))

## [4.27.15](https://github.com/stencila/hub/compare/v4.27.14...v4.27.15) (2021-01-26)


### Bug Fixes

* **Project main file:** Allow authors to set the project's main file ([65bd75c](https://github.com/stencila/hub/commit/65bd75ca21dd46cb2920305b1a6b8c381ee167da)), closes [#856](https://github.com/stencila/hub/issues/856)

## [4.27.14](https://github.com/stencila/hub/compare/v4.27.13...v4.27.14) (2021-01-25)


### Bug Fixes

* **deps:** update dependency django-celery-beat to v2.2.0 ([9a04545](https://github.com/stencila/hub/commit/9a04545013d887bb9e4de8e8408ff090d5d6c425))
* **deps:** update dependency django-waffle to v2.1.0 ([d0019fd](https://github.com/stencila/hub/commit/d0019fd97b787dbc89e92915a9d6d70fa0c659c8))
* **deps:** update dependency pyjwt to v2 ([b7f11a0](https://github.com/stencila/hub/commit/b7f11a0dd2f75f976e7cadb3ba7a3291071a5543))
* **deps:** update dependency pytest-cov to v2.11.1 ([8557f0a](https://github.com/stencila/hub/commit/8557f0a84e7e29c33f7282f75c82d6a794e825c9))
* **deps:** update dependency setuptools to v51.3.3 ([fab37b1](https://github.com/stencila/hub/commit/fab37b103e4ee805989d7290dcd68a74a98c1311))
* **OpenId tokens:** Changes for new pyjwt API ([d9c2f83](https://github.com/stencila/hub/commit/d9c2f83448d722f6b3495bfd244f7d0f211b8de5))

## [4.27.13](https://github.com/stencila/hub/compare/v4.27.12...v4.27.13) (2021-01-19)


### Bug Fixes

* **Pricing:** Sort account plans for logged in users ([5e75b9a](https://github.com/stencila/hub/commit/5e75b9aa6f106ccc157a65377047d8bc816671c2))

## [4.27.12](https://github.com/stencila/hub/compare/v4.27.11...v4.27.12) (2021-01-18)


### Bug Fixes

* **Docs:** Fix link to Help documentation ([8b8d69f](https://github.com/stencila/hub/commit/8b8d69f31885ed508360adb3363b83e10c263e68))

## [4.27.11](https://github.com/stencila/hub/compare/v4.27.10...v4.27.11) (2021-01-15)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.104.5 ([ccd82c4](https://github.com/stencila/hub/commit/ccd82c401b67f169d5ed5d9b3c15a626a4ce00b7))
* **deps:** update dependency pygments to v2.7.4 ([766f3b8](https://github.com/stencila/hub/commit/766f3b88d25a19340da57a013445678490796ec7))
* **Invites:** Extract fields from query ([49fcefd](https://github.com/stencila/hub/commit/49fcefd8688214517bf162712fa3edd10390f5cb)), closes [#937](https://github.com/stencila/hub/issues/937)

## [4.27.10](https://github.com/stencila/hub/compare/v4.27.9...v4.27.10) (2021-01-12)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.104.4 ([6ee9ddb](https://github.com/stencila/hub/commit/6ee9ddb7b0a0f9d552baeaf9d6d15a7a16f2619e))
* **deps:** update dependency @stencila/executa to v1.15.6 ([0587b97](https://github.com/stencila/hub/commit/0587b97f95afc34a4f6f6f4006bf0f0842bdf3a7))
* **deps:** update dependency django to v3.1.5 ([df1d734](https://github.com/stencila/hub/commit/df1d7347ec73f7f32b5ed42f0cf261b4479ed20a))
* **deps:** update dependency django-storages to v1.11.1 ([f6f88b0](https://github.com/stencila/hub/commit/f6f88b0c1233349cdfa8aa0f517ed681abb10b17))
* **deps:** update dependency htmx.org to v1.1.0 ([4baab8b](https://github.com/stencila/hub/commit/4baab8b9b68169113b3c649dc4f880e308b567e9))
* **deps:** update dependency pillow to v8.1.0 ([558dc2a](https://github.com/stencila/hub/commit/558dc2a11f3d0224315321ca9f1c53318cffd634))
* **deps:** update dependency pygithub to v1.54.1 ([9b4aa41](https://github.com/stencila/hub/commit/9b4aa4125ad91ebc65464befa669d434d4fa14c1))
* **deps:** update dependency setuptools to v51.1.2 ([2e7f9d7](https://github.com/stencila/hub/commit/2e7f9d7b9a257685404ecdc1ab43d9d9980cac26))

## [4.27.9](https://github.com/stencila/hub/compare/v4.27.8...v4.27.9) (2020-12-21)


### Bug Fixes

* **Manager:** Update dev deps ([a7a172f](https://github.com/stencila/hub/commit/a7a172fac2a145351a9b0af18a8149f992751028))

## [4.27.8](https://github.com/stencila/hub/compare/v4.27.7...v4.27.8) (2020-12-21)


### Bug Fixes

* **Assistant:** Use python:3.9.1 as base image ([0d869e7](https://github.com/stencila/hub/commit/0d869e7ac240346d9a7105d5bfbedbcc4de6de4f))
* **Manager:** Use python:3.9.1 as base image ([50831af](https://github.com/stencila/hub/commit/50831afb0826ba977c11816a9fb2b30bafb29448))
* **Overseer:** Pin to python:3.9.1 ([267a556](https://github.com/stencila/hub/commit/267a5560cfacaa7daa88ce86b4486f3d64f47de9))
* **Scheduler:** Pin to python:3.9.1 ([e80d2ee](https://github.com/stencila/hub/commit/e80d2eee82b3f8eb3b6388c16110f5e2625751a3))
* **Worker:** Remove unused gcsfuse install ([4908ea1](https://github.com/stencila/hub/commit/4908ea13e5d6d90c1274051404405e9966d831a6))

## [4.27.7](https://github.com/stencila/hub/compare/v4.27.6...v4.27.7) (2020-12-21)


### Bug Fixes

* **Cache:** Pin to 6.0.9 ([1463b23](https://github.com/stencila/hub/commit/1463b230b71029d47d041f7f717eefe00e752616))
* **Database:** Pin to 13.1 ([6876f13](https://github.com/stencila/hub/commit/6876f137fdf14b7cc0391fab610087b04b74b1e8))
* **Monitor:** Pin to v2.23.0 ([a366435](https://github.com/stencila/hub/commit/a366435976a781873c2bf6b75e3ee81542191a01))
* **Router:** Pin to 1.19.6 ([3694fc6](https://github.com/stencila/hub/commit/3694fc61c2a909cb07f570300e360ed5a72f5033))

## [4.27.6](https://github.com/stencila/hub/compare/v4.27.5...v4.27.6) (2020-12-21)


### Bug Fixes

* **Broker:** Pin Docker image to minor version ([54c6349](https://github.com/stencila/hub/commit/54c63494891139cfc02e6867446f2e7e30026cf0))

## [4.27.5](https://github.com/stencila/hub/compare/v4.27.4...v4.27.5) (2020-12-20)


### Bug Fixes

* **deps:** update dependency @popperjs/core to v2.6.0 ([7258319](https://github.com/stencila/hub/commit/72583196c5ac13660da09d0544ef65777d75df63))
* **deps:** update dependency @stencila/encoda to v0.104.3 ([2dd4e2b](https://github.com/stencila/hub/commit/2dd4e2b41ebeeae0ea85aaa1c298d8709f5bf13b))
* **deps:** update dependency django-cors-headers to v3.6.0 ([012641b](https://github.com/stencila/hub/commit/012641b811d1d4c23532511f51b94b77382bd62e))
* **deps:** update dependency django-storages to v1.11 ([6ba6bf3](https://github.com/stencila/hub/commit/6ba6bf33105188b8fa146e560110bb6b3f73c7d6))
* **deps:** update dependency google-cloud-storage to v1.35.0 ([2f25546](https://github.com/stencila/hub/commit/2f25546134d6120df7df6c9821518b85a1b5e2e9))
* **deps:** update dependency htmx.org to v1.0.2 ([0be8c8b](https://github.com/stencila/hub/commit/0be8c8b7f863c451826d12b07053f3f1237a233b))
* **deps:** update dependency pytest to v6.2.1 ([2c43569](https://github.com/stencila/hub/commit/2c43569815d7969a6a2317223899424d4cb293a4))

## [4.27.4](https://github.com/stencila/hub/compare/v4.27.3...v4.27.4) (2020-12-15)


### Bug Fixes

* **Convert:** Prevent progress bar animating prematurely ([880a5af](https://github.com/stencila/hub/commit/880a5afa7c7786de2a1bc946f147b3702e38299a))
* **Sources:** Fix fetching of URL sources (Close [#917](https://github.com/stencila/hub/issues/917)) ([b34d8ce](https://github.com/stencila/hub/commit/b34d8ce764f7ac83da9c0b6486c8cab84c686085))

## [4.27.3](https://github.com/stencila/hub/compare/v4.27.2...v4.27.3) (2020-12-14)


### Bug Fixes

* **Jobs:** Handle exceptions when fetching asyn results ([d96509e](https://github.com/stencila/hub/commit/d96509ecf5d7b827313fbf0f5f23acafe16c85ea))

## [4.27.2](https://github.com/stencila/hub/compare/v4.27.1...v4.27.2) (2020-12-14)


### Bug Fixes

* **Convert to GDoc:** Pull the GDoc JSON after creation ([8c4ca0f](https://github.com/stencila/hub/commit/8c4ca0fd9478a44487b37a756a75f0e1e5e6a492))
* **Files:** Replace upload button with open button ([c3bc134](https://github.com/stencila/hub/commit/c3bc13484830c15181994bc9e08dd9f4336f6bb3))
* **Project image:** Handle more than one mathcing file. ([99f520c](https://github.com/stencila/hub/commit/99f520c78a31123ebfff2f0eb754247e83ce6e2b)), closes [#914](https://github.com/stencila/hub/issues/914)
* **Project images:** Make update async ([2c48ff6](https://github.com/stencila/hub/commit/2c48ff68882c0ca2410ae7b08c8d11b49369a2ba))
* **Projects:** Close [#915](https://github.com/stencila/hub/issues/915) ([d0445be](https://github.com/stencila/hub/commit/d0445be5258befcf505b5d76b0acf8a746c647b9))
* **Worker:** Update deps ([a54f3f9](https://github.com/stencila/hub/commit/a54f3f991a2094cdb30ee170bc2e972b2af064ae))
* **Worker:** Upgrade Encoda ([3228367](https://github.com/stencila/hub/commit/32283672f71fb851f257aac9cd8d5c7beb77dbe1))
* **Workers:** Use filter instead of get ([ff13b42](https://github.com/stencila/hub/commit/ff13b4211357e7f97c30a297b54eea67c0cf80b2))

## [4.27.1](https://github.com/stencila/hub/compare/v4.27.0...v4.27.1) (2020-12-12)


### Bug Fixes

* **Project files:** Make file name unique to bust cache ([df6b086](https://github.com/stencila/hub/commit/df6b0860e160d09d5e004f66398f5cc3bd38b60d))
* **Project listing:** Order by title and handle empty descr strings ([e7f46a9](https://github.com/stencila/hub/commit/e7f46a948b991a59e148aea4f6bb34b2065e741f))

# [4.27.0](https://github.com/stencila/hub/compare/v4.26.0...v4.27.0) (2020-12-12)


### Bug Fixes

* **Project images:** Use a unique file name for project ([564bde3](https://github.com/stencila/hub/commit/564bde393317901cf1189a48817aaefc1d815244))
* **Project listing:** Improve ordering ([827dc66](https://github.com/stencila/hub/commit/827dc66d634387336983b1e1ae815604f286a1b9))
* **Project roles:** Rank can only be determined for authed users ([e0f8551](https://github.com/stencila/hub/commit/e0f855196e681896534857246f3cc3c057be1340))
* **Projects:** Fix 3 column grid item sizes ([85516fb](https://github.com/stencila/hub/commit/85516fbfaa3b6a35698c2d3fc9fa77d246a5f9f4))


### Features

* **Project images:** Update image after a pull job ([024cf69](https://github.com/stencila/hub/commit/024cf6952dd8b2de67ba621377140ea5c558282b))

# [4.26.0](https://github.com/stencila/hub/compare/v4.25.2...v4.26.0) (2020-12-12)


### Bug Fixes

* **A11y:** Ensure link hover styles take place for :focus events as well ([68c64b6](https://github.com/stencila/hub/commit/68c64b62d875b0f6705dfdbf87e4e4f43f2de50d))
* **A11y:** Fix accessible title for Profile links ([83c80d4](https://github.com/stencila/hub/commit/83c80d4de5ffa2ca9808df0dd5aff35a4f7ff04c))
* **Account images:** Only allow upload of images ([aad7900](https://github.com/stencila/hub/commit/aad79002a855223b0715db44dff969b50b28876e))
* **Project images:** TO avoid excessive queries update the image file periodically ([6c02e91](https://github.com/stencila/hub/commit/6c02e915191f3787f0776a043ab384fd9a620301))
* **Projects:** Refine project gallery card styles ([d510ebb](https://github.com/stencila/hub/commit/d510ebbf4b32b73600fa57c5a32f1de3ebeee8cc))


### Features

* **API parsers:** Add form and multi-part parsers; remove HTMX JSON extension ([d6ea0a6](https://github.com/stencila/hub/commit/d6ea0a6ff260a919749d79c3bb9e4f2fb78ba03d))
* **CSS:** Add utility CSS class for adding underlines to text ([e85bf0a](https://github.com/stencila/hub/commit/e85bf0a5062e23bc1d53073324bfb8fa8c9a75ce))
* **CSS:** Add utility CSS classes for making elements 50% wide ([d3559ac](https://github.com/stencila/hub/commit/d3559acc9fbbd6680a7081ad528d8a670e3ee15b))
* **Project images:** Add page for setting of a project's image ([71c28e8](https://github.com/stencila/hub/commit/71c28e8f8d7e0b0b3dca10b1b23dcdfd4e9907e2))
* **Projects:** Add a featured field ([abc8f4d](https://github.com/stencila/hub/commit/abc8f4dc151c32115f838f7eb4f943282083f73c))
* **Projects:** Redesign projects listing view ([edea53e](https://github.com/stencila/hub/commit/edea53e18e5a411ae430911402075aff881c2a0b)), closes [#872](https://github.com/stencila/hub/issues/872)

## [4.25.2](https://github.com/stencila/hub/compare/v4.25.1...v4.25.2) (2020-12-11)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.104.1 ([148b827](https://github.com/stencila/hub/commit/148b82768b081fa06ec68e7217accb6064404309))
* **deps:** update dependency @stencila/executa to v1.15.4 ([23a509e](https://github.com/stencila/hub/commit/23a509e56cb9a7dfe85243f4989a35d0e4c24146))
* **deps:** update dependency certifi to v2020.12.5 ([76f4921](https://github.com/stencila/hub/commit/76f49219d0a30ebed38bc6367570c0f26911ae80))
* **deps:** update dependency htmx.org to v1.0.1 ([76dc1a3](https://github.com/stencila/hub/commit/76dc1a30dc77bfaddf98353655efbf5bb8013327))
* **deps:** update dependency pygments to v2.7.3 ([9d62f43](https://github.com/stencila/hub/commit/9d62f433f66dd73c76a92cc016804a6f07cf6665))
* **deps:** update dependency sentry-sdk to v0.19.5 ([ef3ad58](https://github.com/stencila/hub/commit/ef3ad58c548be25ed4ad6cd3d76aba058ceccccb))
* **deps:** update dependency setuptools to v51 ([c0b04d4](https://github.com/stencila/hub/commit/c0b04d4816a396a2ceaefc0171560dce86217b9b))

## [4.25.1](https://github.com/stencila/hub/compare/v4.25.0...v4.25.1) (2020-12-11)


### Bug Fixes

* **Emails:** Make more compact; reduce number of queries ([7ea1c46](https://github.com/stencila/hub/commit/7ea1c46953f432f189ca0da1a2a82435f85081b6))
* **Emails:** Send the correct HTML when signing up versus verifying email address ([079105a](https://github.com/stencila/hub/commit/079105a65a315a52561a759673c826271074832e))
* **Emails:** Tweaks to plain text messages ([804d4e8](https://github.com/stencila/hub/commit/804d4e8a7732f19eeba79a8b1ccbefd776a92e36))
* **Invites:** Tweak wording when no invitations have been sent ([b9c81ac](https://github.com/stencila/hub/commit/b9c81ac80a942d8df69686cff5ed12116b683a3f))

# [4.25.0](https://github.com/stencila/hub/compare/v4.24.4...v4.25.0) (2020-12-09)


### Bug Fixes

* **Google sources:** Get refresh token, handle no refresh token, ability to select a folder. ([8413863](https://github.com/stencila/hub/commit/8413863d867081e14b0dedde540c2700f5a9435b))
* **Google sources:** Print field errors for File selector inputs ([9be209b](https://github.com/stencila/hub/commit/9be209b8363a5b42cb0922095dd0a293678311ae))
* **Router:** Add back orginal `[@account-content](https://github.com/account-content)` location ([6a551f4](https://github.com/stencila/hub/commit/6a551f46aeb55b410e124ef081802652e2c7fe91))
* **Settings:** Reduce the requested scopes from Google ([c55a700](https://github.com/stencila/hub/commit/c55a700ad3d5b937fac9cfca14adb3ebf28bbbdf)), closes [#893](https://github.com/stencila/hub/issues/893)


### Features

* **Google sources:** Use allauth based flow for auth; add to other file types ([58cea41](https://github.com/stencila/hub/commit/58cea41cdd3d44bae8cb2ab7e4ac87003b221f6b))
* **Google sources:** Use Google Picker when creating a Google source ([81e5c00](https://github.com/stencila/hub/commit/81e5c0023cf8f8d435073a096b989dbafa7989a7)), closes [#893](https://github.com/stencila/hub/issues/893)

## [4.24.4](https://github.com/stencila/hub/compare/v4.24.3...v4.24.4) (2020-12-09)


### Bug Fixes

* **CSS:** Improve styling of form fields w/ errors ([6c92164](https://github.com/stencila/hub/commit/6c92164eac9b744505ab1b0ee37845e3c05384cf))
* **Router:** Use custom error page for 500 errors too ([3b4c319](https://github.com/stencila/hub/commit/3b4c31950e2108d968689f18c899f11348bd8984)), closes [/github.com/stencila/hub/issues/895#issuecomment-741391756](https://github.com//github.com/stencila/hub/issues/895/issues/issuecomment-741391756)

## [4.24.2](https://github.com/stencila/hub/compare/v4.24.1...v4.24.2) (2020-12-08)


### Bug Fixes

* **Users:** Fix get_email function ([c87c362](https://github.com/stencila/hub/commit/c87c3620861047b56970cbb605d1cad97fbc0e9c))

## [4.24.1](https://github.com/stencila/hub/compare/v4.24.0...v4.24.1) (2020-12-07)


### Bug Fixes

* **Convert job:** Need to upload GDoc with DOCX extension ([0375753](https://github.com/stencila/hub/commit/0375753e220d749044ae8ec2ab591852570b3407))
* **Files & Sources:** Normalize approach to passing secrets ([32b0855](https://github.com/stencila/hub/commit/32b085578ec278b950eca6d7fe878e3724571469))
* **Jobs:** Temporarily hide parameters ([9866606](https://github.com/stencila/hub/commit/9866606ac4fda9ab93b5baab09189f18269f4715))
* **Sources:** Ensure that super().validate is called to check for duplicates ([173450f](https://github.com/stencila/hub/commit/173450f2fbfd7748555b9478a37f3ac6f74bf5e5)), closes [#892](https://github.com/stencila/hub/issues/892)
* **Sources:** Improve handling of invalid GitHub repo URLs. ([a76f470](https://github.com/stencila/hub/commit/a76f470b6feb0a1780876d57ea4f69a0a9703dc2)), closes [#891](https://github.com/stencila/hub/issues/891)
* **Worker:** Update GDoc related jobs ([28619ed](https://github.com/stencila/hub/commit/28619edc8eded70bdd96a7ea55437467d4445f49))

# [4.24.0](https://github.com/stencila/hub/compare/v4.23.5...v4.24.0) (2020-12-06)


### Bug Fixes

* **Content:** Make external links open in a new window ([3d78ff0](https://github.com/stencila/hub/commit/3d78ff00b2d3e3428a39b2530604bd0aebc665de)), closes [#878](https://github.com/stencila/hub/issues/878)
* **Extract GDrive:** Loosen regex for main comment; avoid duplicate ([6b39049](https://github.com/stencila/hub/commit/6b39049be7a01e916039de2ccd7d43f0d25468f9))
* **Extract job:** Implement filtering ([e77693a](https://github.com/stencila/hub/commit/e77693a08bae6fbebbd26698b15b02f70e03416a))
* **Files:** Only use the current filter when not a snapshot ([71e5133](https://github.com/stencila/hub/commit/71e5133df8e13f9c58ee489a1af93911c6fd68f6))
* **Form field:** Revert to if rather than default filter ([8e9f5d3](https://github.com/stencila/hub/commit/8e9f5d336ce0b6d6aacde62faedcbc82a2c8fe97))
* **Form field rendering:** Implement label and use id instead of field_id ([6389d7e](https://github.com/stencila/hub/commit/6389d7e7b91413f45a2d54636478a1d6d5e97e95))
* **Invites:** Use correct enum value ([a2de707](https://github.com/stencila/hub/commit/a2de7074dcda462143d2822f49786325a78d09c9))
* **Review:** Add project, creator and app to the review node ([a70b032](https://github.com/stencila/hub/commit/a70b032d4a18bb0669b4f99a1a39e99b36c2eb60))
* **Reviews:** Add title and description fields; refresh view while status is EXTRACTING ([144e8cb](https://github.com/stencila/hub/commit/144e8cb96526d1d20d38e55381bf5a8ac3b9261c))
* **Reviews:** Combine filters and assignment of review into single form ([949b748](https://github.com/stencila/hub/commit/949b748cb40cf5e20d41e5f610946eb2a52d41ef))
* **Reviews:** Fix template name ([e98126e](https://github.com/stencila/hub/commit/e98126e2737b404165905504ebb9ee96f76dc919))
* **Reviews:** Only allow project Editors to generate DOIs ([86f817a](https://github.com/stencila/hub/commit/86f817a626ab54f0f86d254fe0c796bbb2e1008e))
* **Reviews:** Refine review styles and layout ([cc18288](https://github.com/stencila/hub/commit/cc1828867a2716989bf486372615c5ea56cc8d0e))
* **Reviews:** Standardize terminology ([5a97d6e](https://github.com/stencila/hub/commit/5a97d6e26bcc0319f5ad0f7fa5b0a80c910b969f))
* **Reviews:** Style review details view/comments ([27dafab](https://github.com/stencila/hub/commit/27dafab098304427cf093cf71e330d9fa83c8544))
* **Reviews:** Tweaks to templates ([608b179](https://github.com/stencila/hub/commit/608b1796266650d65697fd03c032f176e233d34d))
* **Reviews:** Validate reviewer name or id into a user on update ([2a7b2fc](https://github.com/stencila/hub/commit/2a7b2fcb861812e7c00bc542246c2c2c4742289a))
* **Sign in:** Redirect to the current page ([75ff90b](https://github.com/stencila/hub/commit/75ff90b75608dcab09f59dcec7c550fb6e4c34ce))
* **Storage:** Add option to use bucket ([1895ae8](https://github.com/stencila/hub/commit/1895ae80523ef63ccccb19e8ac245cf822d29942))
* **User search:** Do not add value if no value ([043b318](https://github.com/stencila/hub/commit/043b3184f933498aa11ea4a56362b9d2dc1f6188))
* **User search:** Tweaks to enable more reuse ([ffb0fb0](https://github.com/stencila/hub/commit/ffb0fb0973ea7b4b266694209d96eeab98868ca4))
* **User search:** Use hx-swap to avoid it being inherited from parent ([1a074ae](https://github.com/stencila/hub/commit/1a074aec11196ad055e6a4e655bfd5a25297c824))
* **Users:** Make syncing of data to UserFlow more robust to missing emails ([c38812e](https://github.com/stencila/hub/commit/c38812e739dfe67a3c3ecd5fb9a800e7cccf8cf9))
* **Worker:** Enable extract job ([48d33e3](https://github.com/stencila/hub/commit/48d33e392a22928fb017d0365f617927f5446267))
* **Worker:** Iterate over dictionaries properly ([fa1e129](https://github.com/stencila/hub/commit/fa1e129f79da288c79bf6f0797141e3cd0b40554))
* **Worker:** Upgrade Encoda and add necessary env var ([5dcbac6](https://github.com/stencila/hub/commit/5dcbac63acd17d4d8107910bfb8d6044151794b6))


### Features

* **Convert job:** Allow alternative destination storage ([c4ebf83](https://github.com/stencila/hub/commit/c4ebf8360fdefa252eb214915f7e67d1563aa532))
* **Extract GitHub review:** Add job to fetch a review from a GitHub PR ([386c748](https://github.com/stencila/hub/commit/386c748b1a0502401a3315bc655b5550bc649f80))
* **Extract job:** Add a review extraction job for Google Drive comments ([46c35c0](https://github.com/stencila/hub/commit/46c35c0c1476fc7ffb2f3558cbac7a08bd7e366e))
* **Invites:** Add action to accept review; add admin ([901e49b](https://github.com/stencila/hub/commit/901e49bfe56ac9264b91a52c2784bb0aec9b8cd3))
* **Jobs:** Add extract method ([99e52ff](https://github.com/stencila/hub/commit/99e52ff9997fba0fd6cc2e0f6fb9c6dc9cace794))
* **Jobs:** Show job parameters in summary ([13fda97](https://github.com/stencila/hub/commit/13fda9725bd3f45b4590b50a27bd9efd27959aef))
* **Nodes:** Add ability to render the content of nodes ([57f1dd1](https://github.com/stencila/hub/commit/57f1dd1045bedac764abfbae3b8aaf25cf494787))
* **Review:** Allo either username or email to be used on review creation ([b1e4fe2](https://github.com/stencila/hub/commit/b1e4fe26a89060d49c6f27b0f67e055ff89cfae1))
* **Reviews:** Add button to register DOI for extracted reviews ([2998d31](https://github.com/stencila/hub/commit/2998d31358249edf0d839a4877d0be53285ed2ed))
* **Reviews:** Add project reviews ([6e77e5f](https://github.com/stencila/hub/commit/6e77e5f31647f980b903f67b380f638a1700cbb1)), closes [#818](https://github.com/stencila/hub/issues/818)
* **Reviews:** Initial round of styling of Reviews list view ([0234d4d](https://github.com/stencila/hub/commit/0234d4da71e2544eaca810ec465ec4482058eaa7))
* **Reviews:** Place reviews behind feature flag ([834b8a7](https://github.com/stencila/hub/commit/834b8a7b929313e3a27f26ff9b2faa552ef9d6c4))
* **Reviews:** Render content and comments incl replies ([4816f6c](https://github.com/stencila/hub/commit/4816f6ca1620ab7283133f37a8af8c44ad4b0157))

## [4.23.5](https://github.com/stencila/hub/compare/v4.23.4...v4.23.5) (2020-12-05)


### Bug Fixes

* **deps:** update dependency @stencila/executa to v1.15.3 ([0209496](https://github.com/stencila/hub/commit/0209496de42b54c6451776737595ebb9e08a9b77))
* **deps:** update dependency @vizuaalog/bulmajs to v0.12.0 ([2da8170](https://github.com/stencila/hub/commit/2da81702160911afb99b6da8df8e63ec2b927acd))
* **deps:** update dependency bulma-toast to v2.2.0 ([436f416](https://github.com/stencila/hub/commit/436f416fe4c2944fa13f45950f15d965c5be6454))
* **deps:** update dependency dj-stripe to v2.4.1 ([b151676](https://github.com/stencila/hub/commit/b151676bbd64ccfe90e109986a3985c1c99add3f))
* **deps:** update dependency django to v3.1.4 ([830f0bd](https://github.com/stencila/hub/commit/830f0bdbec3b506bb90bdf69d9940c2db6232f06))
* **deps:** update dependency pygithub to v1.54 ([18e64b8](https://github.com/stencila/hub/commit/18e64b8eed3d747a2d8e99b797a029d2d2e2e13a))
* **Pricing:** Ensure Account plans are correctly ordered (Close [#770](https://github.com/stencila/hub/issues/770)) ([1f47631](https://github.com/stencila/hub/commit/1f476312f80f9808e630020f2006f5367654c522))

## [4.23.4](https://github.com/stencila/hub/compare/v4.23.3...v4.23.4) (2020-12-01)


### Bug Fixes

* **Deps:** Update Thema version ([6dafad9](https://github.com/stencila/hub/commit/6dafad955b8544e81afc84aab852ae9190ea9b24))

## [4.23.3](https://github.com/stencila/hub/compare/v4.23.2...v4.23.3) (2020-11-29)


### Bug Fixes

* **deps:** update dependency django-allauth to v0.44.0 ([eabca3d](https://github.com/stencila/hub/commit/eabca3d37906af1045a093c0f98c94c5c4ee5ea3))
* **deps:** update dependency django-extensions to v3.1.0 ([01bdd5e](https://github.com/stencila/hub/commit/01bdd5e8e5885f9470575e50c49817100988ab1e))
* **deps:** update dependency htmx.org to v0.4.1 ([6a08e6c](https://github.com/stencila/hub/commit/6a08e6ce0cb8cf7fd593e188df836b7d378c5110))
* **deps:** update dependency htmx.org to v1 ([9cc85f9](https://github.com/stencila/hub/commit/9cc85f9642e620ddf0205c21c9bd3ec54142ac8a))
* **deps:** update dependency lxml to v4.6.2 ([a65c895](https://github.com/stencila/hub/commit/a65c895ca65e3bd7afd7fff70399ba5e124b1787))
* **deps:** update dependency userflow.js to v1.8.0 ([e1c5440](https://github.com/stencila/hub/commit/e1c54404581b3883d5c339f31469037f1a38ad8b))

## [4.23.2](https://github.com/stencila/hub/compare/v4.23.1...v4.23.2) (2020-11-25)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.103.1 ([1779850](https://github.com/stencila/hub/commit/17798506a024cc1da8922e26677f6e01187e2b40))

## [4.23.1](https://github.com/stencila/hub/compare/v4.23.0...v4.23.1) (2020-11-23)


### Bug Fixes

* **Files:** Add get_latest method ([7e7da2f](https://github.com/stencila/hub/commit/7e7da2fd5cceba001594d1a2ae62d6662e4b1e0c))
* **HTTP pull:** Use mimetype to resolve extension ([d99cb04](https://github.com/stencila/hub/commit/d99cb04025d1e90b365925a3e8cfe13f377d8ca9)), closes [#854](https://github.com/stencila/hub/issues/854)
* **Manager:** Improve presentation of default from email ([3317d65](https://github.com/stencila/hub/commit/3317d6522ed903ca8704885646f2116eed437790))
* **New source menu:** Alphabetical order and other tweaks ([347e15c](https://github.com/stencila/hub/commit/347e15c5255475f60f794d3919651e1fd246a661)), closes [#854](https://github.com/stencila/hub/issues/854)
* **Password change:** Add message about password reset ([9f085b9](https://github.com/stencila/hub/commit/9f085b96888a60ef3f11dfec9946c454694da40c))
* **URL Source:** Attempt to match URL to other source type ([b8024ba](https://github.com/stencila/hub/commit/b8024ba7bec5510cf75fa174ade7b05c2c2645a2)), closes [#854](https://github.com/stencila/hub/issues/854)

# [4.23.0](https://github.com/stencila/hub/compare/v4.22.1...v4.23.0) (2020-11-22)


### Bug Fixes

* **User tasks:** Capture exception info in warning ([c77595a](https://github.com/stencila/hub/commit/c77595a67d48198c495b0e8dd645385f98a0fd27))


### Features

* **Sigin:** Allow sign in with username or email ([aa7c3a3](https://github.com/stencila/hub/commit/aa7c3a308b4687a6480cd8c6ed62244088d0b740)), closes [#830](https://github.com/stencila/hub/issues/830)

## [4.22.1](https://github.com/stencila/hub/compare/v4.22.0...v4.22.1) (2020-11-22)


### Bug Fixes

* **Admin:** Check that project and job exists ([1758f85](https://github.com/stencila/hub/commit/1758f85d08de73bd4e4ae3c54f711de415b0181f))
* **Emails:** Allow for form/multi-part data ([c83309d](https://github.com/stencila/hub/commit/c83309d8e05bd2c4874b07663c47d54bb13c22ea))
* **Register job:** Handle UTF-8 in registered content ([57f4ab0](https://github.com/stencila/hub/commit/57f4ab0b44038e16670ae15676491b09b0658039))

# [4.22.0](https://github.com/stencila/hub/compare/v4.21.1...v4.22.0) (2020-11-22)


### Bug Fixes

* **Files:** Use filter to get files ([1fa5e96](https://github.com/stencila/hub/commit/1fa5e96103f776d4c99987656d0f6400c32f5214)), closes [#852](https://github.com/stencila/hub/issues/852)
* **Snapshots:** Set file.current to False  on bulk_create ([5a0b498](https://github.com/stencila/hub/commit/5a0b49847c32cab1e53057e7457d324f28e8391b))


### Features

* **Admin:** Improve list display and filtering for files and snapshots ([d041d72](https://github.com/stencila/hub/commit/d041d72a3b57567a9f94a6ba565e41cdc0c63ba2))

## [4.21.1](https://github.com/stencila/hub/compare/v4.21.0...v4.21.1) (2020-11-22)


### Bug Fixes

* **Manager:** Do not ignore DOIs folder ([2ffe6c5](https://github.com/stencila/hub/commit/2ffe6c5af5a0d386a22ced91e13d3406f6ab3ca3))

# [4.21.0](https://github.com/stencila/hub/compare/v4.20.3...v4.21.0) (2020-11-22)


### Bug Fixes

* **DOI Admin:** Dispatch jobs ([f86aec0](https://github.com/stencila/hub/commit/f86aec06dcdce9604144e56a60b0a5e073ca7bbd))
* **DOIs:** Redirect to the URL of the registered node ([e456485](https://github.com/stencila/hub/commit/e456485c431c8aa3bfd7da825b455d885385e8f4))
* **Register job:** Allow for specific batch id and custom email. ([c09e8e7](https://github.com/stencila/hub/commit/c09e8e757aa4993b23ab3deca64ad429f507aa6a))


### Features

* **DOIs:** Add account quota for DOIs; check creator permissions ([b454168](https://github.com/stencila/hub/commit/b45416833d250f8c82b2b1cbea5f8bc47caea433))
* **DOIs:** Add API endpoints ([3c772d5](https://github.com/stencila/hub/commit/3c772d5c7a3347e1c98fe35fee20bcf5173c6894))
* **DOIs:** Add model for DOIs ([e1094ef](https://github.com/stencila/hub/commit/e1094ef4440ec30e32fd9ccc9ba311b979efde5d))
* **Worker:** Add a job to register DOIs ([f497612](https://github.com/stencila/hub/commit/f49761215b5b28d5fbf392d62af76378b8f10a27)), closes [#817](https://github.com/stencila/hub/issues/817)

## [4.20.3](https://github.com/stencila/hub/compare/v4.20.2...v4.20.3) (2020-11-20)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.103.0 ([f086cb3](https://github.com/stencila/hub/commit/f086cb36a885da235064d679d5ad842723701778))
* **deps:** update dependency @stencila/executa to v1.15.2 ([8f92c81](https://github.com/stencila/hub/commit/8f92c816cef7c6c4007b645c671277b6bdf4b1fc))
* **deps:** update dependency dj-stripe to v2.4.0 ([d532a66](https://github.com/stencila/hub/commit/d532a660922f995d8e566a579815d683a4692dd6))
* **deps:** update dependency django-meta to v2.0.0 ([405e6ab](https://github.com/stencila/hub/commit/405e6ab90e8968e948ac7c0f8a85d6d93f992da3))
* **deps:** update dependency google-api-python-client to v1.12.8 ([ff808d6](https://github.com/stencila/hub/commit/ff808d6d7c025388bfd42f795614ea49f52dba46))
* **deps:** update dependency google-cloud-storage to v1.33.0 ([fc28b24](https://github.com/stencila/hub/commit/fc28b24c7e1a1b0a4cc972da0cd8fd3d738fa650))
* **deps:** update dependency htmx.org to v0.4.0 ([715c4ef](https://github.com/stencila/hub/commit/715c4efab4d1b2547776a069a2fbf75ddea9737b))
* **deps:** update dependency inflect to v4.1.1 ([d33fd84](https://github.com/stencila/hub/commit/d33fd8472f7096eb1d1324cd38637e5e72e4df2d))
* **deps:** update dependency inflect to v5 ([06eec6c](https://github.com/stencila/hub/commit/06eec6c157bbf47f40aea5a8e250a04b72b4bbe5))
* **deps:** update dependency prometheus_client to v0.9.0 ([da0bfb7](https://github.com/stencila/hub/commit/da0bfb79fd4ca3ce46b1c8bb7d7135b4f7bdd9c3))
* **deps:** update dependency pytest-randomly to v3.5.0 ([49bb5d8](https://github.com/stencila/hub/commit/49bb5d8c6d971c0ef34cc8fa2116309e69715dbf))
* **deps:** update dependency sentry-sdk to v0.19.4 ([5b92943](https://github.com/stencila/hub/commit/5b929438e481c1b926192d8c4cdd60a5652bcdf5))
* **deps:** update dependency stencila-schema to v0.47.2 ([64b92be](https://github.com/stencila/hub/commit/64b92beac58043db9f54d8a0c380c493e25d901c))
* **deps:** update dependency typescript to v4.1.2 ([1124907](https://github.com/stencila/hub/commit/1124907bb222fbf16a7c23607870b64cee658361))
* **Manager:** Use hx-vars instead of include-vals ([7b2ddec](https://github.com/stencila/hub/commit/7b2ddecb9407581fb97662a55581f2e8bde96cd3))

## [4.20.2](https://github.com/stencila/hub/compare/v4.20.1...v4.20.2) (2020-11-19)


### Bug Fixes

* **Files:** Improve file listing for sources and snapshots ([e878753](https://github.com/stencila/hub/commit/e878753c92330f5dcec8ccca12058a1abe3dad14))
* **Jobs admin:** Add filters, make some fields readonly ([8e85765](https://github.com/stencila/hub/commit/8e8576564ded80f95dc07b79c082e23ca5655a44))
* **Pull job:** Ensure path is within current directory ([aa5fb61](https://github.com/stencila/hub/commit/aa5fb617031e4c13b714d695734068c5b11e67c8))
* **Pull job:** Sort files by path ([aa97f9e](https://github.com/stencila/hub/commit/aa97f9ef1da77d5e6035d11245ac353b587da0d6))
* **User session cache:** Bust every hour for authed users ([e68ec3d](https://github.com/stencila/hub/commit/e68ec3d76c5b837524f983b4e94a31a3aa9b6a0d)), closes [#816](https://github.com/stencila/hub/issues/816)


### Performance Improvements

* **Project files:** Improve performance of listing many files ([2e8a88f](https://github.com/stencila/hub/commit/2e8a88f9b15ddec4a324c25ed887c1c7d9baa22e))
* **Pull callback:** Do a bulk create of files ([fa4a1c4](https://github.com/stencila/hub/commit/fa4a1c490010fdc979d731ae584bff32acef0031))

## [4.20.1](https://github.com/stencila/hub/compare/v4.20.0...v4.20.1) (2020-11-18)


### Bug Fixes

* **Base template:** Temporary fix for [#816](https://github.com/stencila/hub/issues/816) ([2f16bb6](https://github.com/stencila/hub/commit/2f16bb6d246825d7862d17cf31098c7446029f21))
* **Jobs:** Do not add keys or secrets to job parameters ([950cb82](https://github.com/stencila/hub/commit/950cb82e5794c9ba4a1e64ddb0d6e390dec1c823))
* **Nodes:** Display JSON, shorter key, refactored serializer names ([27cf51e](https://github.com/stencila/hub/commit/27cf51e79ea90de9072b8cedd81e7c4d0a82dbdf))
* **Settings:** Reduce user scope to read info and emails ([664a51a](https://github.com/stencila/hub/commit/664a51aed1affd9f56a7691c2bb2e3a1d6166f83))


### Performance Improvements

* **GitHub pull:** Avoid re-reading files for file info ([c09bc07](https://github.com/stencila/hub/commit/c09bc07508a7939371337beef2ad3429fa83efca))
* **GitHub pull:** Use extract and add test_huge_zip ([978daef](https://github.com/stencila/hub/commit/978daef5f778a19b5ea38dca9767c1a04eab811a))

# [4.20.0](https://github.com/stencila/hub/compare/v4.19.0...v4.20.0) (2020-11-17)


### Bug Fixes

* **GitHub repos:** Improve refresh speed by reducing requests and using bulk_create ([669346b](https://github.com/stencila/hub/commit/669346b6486670972742b56a45ff479a9e289579))
* **GitHub repos:** Send username as data; don't use deprecated `warn` ([98f4fce](https://github.com/stencila/hub/commit/98f4fce4205d8ea324d0e5d3e7ce141c237f76eb))


### Features

* **GitHub repos:** Allow user to update list of repos in form ([7cb7a98](https://github.com/stencila/hub/commit/7cb7a98fb49262198ebb4f0dbefeb6e5baa5cda0))

# [4.19.0](https://github.com/stencila/hub/compare/v4.18.1...v4.19.0) (2020-11-17)


### Features

* **Admin:** Improve filtering of GitHub repos ([4a7e40e](https://github.com/stencila/hub/commit/4a7e40e1ddc2b4bb7af58b27466d8dced11b7cc1))

## [4.18.1](https://github.com/stencila/hub/compare/v4.18.0...v4.18.1) (2020-11-17)


### Bug Fixes

* **Github pull:** Fetch zip archive of repo. ([2da189e](https://github.com/stencila/hub/commit/2da189e3d75bd91c9f1616dc97a90ce349931cc3)), closes [#831](https://github.com/stencila/hub/issues/831)
* **GitHub repos:** Invert how values in request are named ([8d23203](https://github.com/stencila/hub/commit/8d2320353fedbfe2da555b0acd976460f5ddfbf9))

# [4.18.0](https://github.com/stencila/hub/compare/v4.17.10...v4.18.0) (2020-11-16)


### Bug Fixes

* **GitHub:** Expanded scopes for connected GitHub accounts ([ab481c4](https://github.com/stencila/hub/commit/ab481c403333b1a3757ae8cf3fe9870d1c7561e4))
* **GitHub repos:** Add throttle for requests to refresh ([232cb26](https://github.com/stencila/hub/commit/232cb263658424877fa6a509d92122ab20e693fe))


### Features

* **GitHub repos:** Add search field ([dcaa15f](https://github.com/stencila/hub/commit/dcaa15ff8a3d6c83a30d610e8281a8c1a13d36ea))
* **GitHub sources:** Maintain a list of GitHUb repos that a user has access to ([a7f2cb0](https://github.com/stencila/hub/commit/a7f2cb004aa5509d8b29a7d367b229d758156857))

## [4.17.10](https://github.com/stencila/hub/compare/v4.17.9...v4.17.10) (2020-11-15)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.102.2 ([96d1978](https://github.com/stencila/hub/commit/96d19789fc5492c5bf4b344518188f9889760b53))
* **deps:** update dependency certifi to v2020.11.8 ([4d39548](https://github.com/stencila/hub/commit/4d39548f1f425ea63d24b65b1bf9cf806c0952b1))
* **deps:** update dependency kubernetes to v12.0.1 ([1feb99f](https://github.com/stencila/hub/commit/1feb99fbfc92bb5b2cd0f910bf207787fa005971))
* **deps:** update dependency sentry-sdk to v0.19.3 ([f15f8e5](https://github.com/stencila/hub/commit/f15f8e5a093f167aba40a8492761da93803dd580))
* **deps:** update dependency urllib3 to v1.26.2 ([ba9a034](https://github.com/stencila/hub/commit/ba9a03427d6b430c129d223ac808644aafcc9905))
* **Manager:** Update version of components ([8246068](https://github.com/stencila/hub/commit/8246068bb717bd5dd46549b46ed5c5b6f894d862))

## [4.17.9](https://github.com/stencila/hub/compare/v4.17.8...v4.17.9) (2020-11-11)


### Bug Fixes

* **Worker:** Update Encoda to 0.102.2 ([e517ea6](https://github.com/stencila/hub/commit/e517ea6b4b5f6a4bd2c5af3ec4576da2a09076ef))

## [4.17.8](https://github.com/stencila/hub/compare/v4.17.7...v4.17.8) (2020-11-10)


### Bug Fixes

* Update Stencila Encoda and Components for Plotly support ([ec1b20e](https://github.com/stencila/hub/commit/ec1b20ea269cb5ce3c28ba89ba50ce7aab584cff))

## [4.17.7](https://github.com/stencila/hub/compare/v4.17.6...v4.17.7) (2020-11-10)


### Bug Fixes

* **User serializer:** Handle no personal account ([9ff235b](https://github.com/stencila/hub/commit/9ff235b8d97959b8b9c3670c541653e29efca4cc)), closes [#813](https://github.com/stencila/hub/issues/813)

## [4.17.6](https://github.com/stencila/hub/compare/v4.17.5...v4.17.6) (2020-11-09)


### Bug Fixes

* **Settings:** Widen regex for CORS from Google Docs add-on ([4a43d83](https://github.com/stencila/hub/commit/4a43d83d25cfa41481baf816381d5163da8ab7e0))
* **User serialiser:** Handle users with no personal account ([27965b2](https://github.com/stencila/hub/commit/27965b251efcf3d963db1f5a4c821268c06a406e))

## [4.17.5](https://github.com/stencila/hub/compare/v4.17.4...v4.17.5) (2020-11-09)


### Bug Fixes

* **Upload source:** Fix pull job and add typings and regression test ([0e03a15](https://github.com/stencila/hub/commit/0e03a15d02bd54de23db424ecb6caf144365185c)), closes [#809](https://github.com/stencila/hub/issues/809)

## [4.17.4](https://github.com/stencila/hub/compare/v4.17.3...v4.17.4) (2020-11-09)


### Bug Fixes

* **User tasks:** For UserFlow send JSON, add fields ([717a9a7](https://github.com/stencila/hub/commit/717a9a71fcd1e393e1b2943dc27bd81abafb2149))

## [4.17.3](https://github.com/stencila/hub/compare/v4.17.2...v4.17.3) (2020-11-09)


### Bug Fixes

* **User tasks:** Fix URL for UserFlow API ([2ca03ef](https://github.com/stencila/hub/commit/2ca03ef689ed7a94c400905b18f3df48ef85e4da))

## [4.17.2](https://github.com/stencila/hub/compare/v4.17.1...v4.17.2) (2020-11-09)


### Bug Fixes

* **Scheduler:** Use UTC timezone ([c5aafc5](https://github.com/stencila/hub/commit/c5aafc5a08abf8b3df36b83d1f6a9344aa74914e))

## [4.17.1](https://github.com/stencila/hub/compare/v4.17.0...v4.17.1) (2020-11-09)


### Bug Fixes

* **Assistant:** Increase log level to info ([99e9b46](https://github.com/stencila/hub/commit/99e9b46308180abdd89b7ae3106b37913956e9d1))
* **Featur flags:** Add serializer to avoid warning on API schema generation ([56b8dd9](https://github.com/stencila/hub/commit/56b8dd9a7f32b7699404085df669d768161e2fcd))
* **User tasks:** Fix queries ([6dc1b7a](https://github.com/stencila/hub/commit/6dc1b7aa7bf8980e791e3229be7575e57b1e7b77))

# [4.17.0](https://github.com/stencila/hub/compare/v4.16.1...v4.17.0) (2020-11-09)


### Bug Fixes

* **Scheduler:** Increase log level to INFO ([fa942e9](https://github.com/stencila/hub/commit/fa942e9727a56ece3dc6ed647850fa35bfecb5ab))
* **UserFlow integration:** Rename token and API key secrets ([5c91458](https://github.com/stencila/hub/commit/5c91458131980fba3e91ffb09af7238bc10d5c10))


### Features

* **Google Sheets:** Add Google Sheets as a project source ([4438e0e](https://github.com/stencila/hub/commit/4438e0ec7c60625eee40dd6381a32407eef7506c))
* **Worker:** Add job to pull Google Sheets ([65404c5](https://github.com/stencila/hub/commit/65404c59bbd89ad76eb6026233ead29d864fff0e))

## [4.16.1](https://github.com/stencila/hub/compare/v4.16.0...v4.16.1) (2020-11-09)


### Bug Fixes

* **Feature flags:** Make SQL Postgres compatible ([89ceee1](https://github.com/stencila/hub/commit/89ceee193fd149ec6f85354c7f3f1523f03061c1)), closes [#807](https://github.com/stencila/hub/issues/807)

# [4.16.0](https://github.com/stencila/hub/compare/v4.15.0...v4.16.0) (2020-11-08)


### Features

* **Users:** Add feature flags to /api/users/me result ([24c66f6](https://github.com/stencila/hub/commit/24c66f63c4bbcf74b2713fd9d802e85ef2eb9a85))
* **Users:** Update external services with new data ([8760d8b](https://github.com/stencila/hub/commit/8760d8b3e0330a63b09f03b1be2b14806cc020fa))

# [4.15.0](https://github.com/stencila/hub/compare/v4.14.1...v4.15.0) (2020-11-07)


### Features

* **Meta data:** Add meta data to pages for Accounts, Projects and Nodes. ([f38d0d3](https://github.com/stencila/hub/commit/f38d0d37954969dc972a52767994da380f2729fb))

## [4.14.1](https://github.com/stencila/hub/compare/v4.14.0...v4.14.1) (2020-11-07)


### Bug Fixes

* **Features:** Allow null values for label ([426b86e](https://github.com/stencila/hub/commit/426b86e724023bf063581a954b1e311711c48562))

# [4.14.0](https://github.com/stencila/hub/compare/v4.13.5...v4.14.0) (2020-11-06)


### Bug Fixes

* **Features:** Update migration ([cf7f199](https://github.com/stencila/hub/commit/cf7f19911b19f8c7958bd49551500cd98169f515))


### Features

* **Features and privacy:** Allow users to turn on/off features ([99baabf](https://github.com/stencila/hub/commit/99baabf5db1a5f6b16faae8fe8ecf7f16774e5fd))

## [4.13.5](https://github.com/stencila/hub/compare/v4.13.4...v4.13.5) (2020-11-06)


### Bug Fixes

* **deps:** update dependency @popperjs/core to v2.5.4 ([497575d](https://github.com/stencila/hub/commit/497575ddce3fd58b2ba11cce9ea7d1ac625f663d))
* **deps:** update dependency @stencila/encoda to v0.101.3 ([035af0f](https://github.com/stencila/hub/commit/035af0fef62f87b778b076e876c4114d49834835))
* **deps:** update dependency @stencila/executa to v1.15.1 ([0d94ee5](https://github.com/stencila/hub/commit/0d94ee557aad9127de3a64faa171b722575f8198))
* **deps:** update dependency django to v3.1.3 ([944fdc9](https://github.com/stencila/hub/commit/944fdc9dce28b2a4ffc64dccf0483b98692e0d1f))
* **deps:** update dependency djangorestframework to v3.12.2 ([c7d452f](https://github.com/stencila/hub/commit/c7d452fcdfcd76feebee11a8d9770f06f0029004))
* **deps:** update dependency htmx.org to v0.3.0 ([2840572](https://github.com/stencila/hub/commit/2840572ecb1951cc11a29be27f687cd1e5f83cfa))
* **deps:** update dependency sentry-sdk to v0.19.2 ([d7e583f](https://github.com/stencila/hub/commit/d7e583f19d969318571e6136cc63fa2a47bc8901))

## [4.13.4](https://github.com/stencila/hub/compare/v4.13.3...v4.13.4) (2020-11-03)


### Bug Fixes

* **Sessions:** Re-enable HTTP server on sessions ([52509c4](https://github.com/stencila/hub/commit/52509c4acee643c1c312386a11943f0e9e8f1df6))

# [4.13.0](https://github.com/stencila/hub/compare/v4.12.0...v4.13.0) (2020-11-03)


### Bug Fixes

* **Worker:** Gracefully handle lack of registry credentials in pin job ([546ac31](https://github.com/stencila/hub/commit/546ac310a113fcb22a2c1f5587d96b37d9ff33e9))
* **Worker:** Update Encoda ([f7ce211](https://github.com/stencila/hub/commit/f7ce211bfd1e60be04e551ff1f2ce2d3747a5da3))


### Features

* **Sessions:** Serve sessions on both Websocket and HTTP ([db0354a](https://github.com/stencila/hub/commit/db0354a10e7fca1a69e3009031aca5fb4624146f))

# [4.12.0](https://github.com/stencila/hub/compare/v4.11.0...v4.12.0) (2020-11-03)


### Bug Fixes

* **Overseer:** Only record events and collect data on workers ([4f5b50e](https://github.com/stencila/hub/commit/4f5b50ef3b886e03ddd187c68747557ca8a6fd2a))


### Features

* **Accounts:** Obtain picture when authenticating with OpenID ([5b87ece](https://github.com/stencila/hub/commit/5b87ece2b877eea4e9123dbd8d052ca6d7e475e9))

# [4.11.0](https://github.com/stencila/hub/compare/v4.10.4...v4.11.0) (2020-11-02)


### Bug Fixes

* **Accounts:** Fix typo in template ([00d8861](https://github.com/stencila/hub/commit/00d8861cc6b823bfe5bd8615c5cef9779fd735b1))
* **Accounts:** Only save if necessary ([cc39533](https://github.com/stencila/hub/commit/cc39533e4be6c4c9f5d058575b50623982d45f13))


### Features

* **Users:** Allow account image to be set from external account ([51956d8](https://github.com/stencila/hub/commit/51956d8e10796358781cb392ca177a3119b9a8f9))

## [4.10.4](https://github.com/stencila/hub/compare/v4.10.3...v4.10.4) (2020-11-02)


### Bug Fixes

* **Users authentication:** When authenticating with OpenID check against verified email addresses ([494a908](https://github.com/stencila/hub/commit/494a908a443420dafa25112e3da6c5aacfe3a837)), closes [#426](https://github.com/stencila/hub/issues/426)

## [4.10.3](https://github.com/stencila/hub/compare/v4.10.2...v4.10.3) (2020-10-31)


### Bug Fixes

* **deps:** pin dependency @stencila/encoda to 0.100.0 ([45af3e3](https://github.com/stencila/hub/commit/45af3e38c9cf1d7c772a95ceffbaaa3063621c45))
* **deps:** update dependency @stencila/encoda to v0.100.0 ([46edc3c](https://github.com/stencila/hub/commit/46edc3c27e19992704d61dc585484c650fbc2a10))
* **deps:** update dependency @stencila/encoda to v0.101.0 ([708e56e](https://github.com/stencila/hub/commit/708e56ec6086635645127c8f561769702870a16c))
* **deps:** update dependency bulma-toast to v2.1.0 ([774470a](https://github.com/stencila/hub/commit/774470aad635cc39d5ae6471a2dcfabf38fdd9b0))
* **deps:** update dependency drf-yasg to v1.20.0 ([8c58f4f](https://github.com/stencila/hub/commit/8c58f4fde85846d4700e1b99ea6802f8ee5669d4))
* **deps:** update dependency pygments to v2.7.2 ([9dfec7e](https://github.com/stencila/hub/commit/9dfec7e01bf4806d5495d27d2835eb8372d5c0e1))
* **deps:** update dependency pytest to v6.1.2 ([6881c7d](https://github.com/stencila/hub/commit/6881c7d8486ca8c0c03f4ba604d8bc1fbc684e9a))
* **deps:** update dependency typescript to v4.0.5 ([1aef30e](https://github.com/stencila/hub/commit/1aef30e1c3e644e8fe20556e3363c08797d7eff7))

## [4.10.2](https://github.com/stencila/hub/compare/v4.10.1...v4.10.2) (2020-10-29)


### Bug Fixes

* **Manager:** Upgrade Thema ([a00c125](https://github.com/stencila/hub/commit/a00c125c63d85010f055de582a887f4a9fdd5fb7))

## [4.10.1](https://github.com/stencila/hub/compare/v4.10.0...v4.10.1) (2020-10-29)


### Bug Fixes

* **Manager:** Update Stencila packages ([fbf1c6d](https://github.com/stencila/hub/commit/fbf1c6dcbc0ad38e2031da9b5090ecbd29ae387d))
* **Worker:** Upgrade Encoda ([41d5701](https://github.com/stencila/hub/commit/41d5701231601d7c0f73931c8ce07d7bf27cea01))

# [4.10.0](https://github.com/stencila/hub/compare/v4.9.0...v4.10.0) (2020-10-27)


### Features

* **Project & orgs:** Add menu option to filter by role ([e749a28](https://github.com/stencila/hub/commit/e749a28fb0a9415add990fb16289f1bc26a1e006)), closes [#772](https://github.com/stencila/hub/issues/772)

# [4.9.0](https://github.com/stencila/hub/compare/v4.8.0...v4.9.0) (2020-10-23)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.99.15 ([54c33f9](https://github.com/stencila/hub/commit/54c33f91c05c2abb261f3e1187059a59ba094476))
* **deps:** update dependency @stencila/executa to v1.15.0 ([08d05f4](https://github.com/stencila/hub/commit/08d05f4f8e5c00336765a2ea6875f2a6772cc97a))
* **deps:** update dependency django-celery-beat to v2.1.0 ([682dd52](https://github.com/stencila/hub/commit/682dd52fcea7f69f12c712a2667ba19d1ed44364))
* **deps:** update dependency google-api-python-client to v1.12.5 ([a84816d](https://github.com/stencila/hub/commit/a84816d5edd6321c71297ccf9b29f13568ef8712))
* **deps:** update dependency google-cloud-storage to v1.32.0 ([55fd3e8](https://github.com/stencila/hub/commit/55fd3e8aa4045da9b6b8b9cdfc37e4d3698b6cbb))
* **deps:** update dependency lxml to v4.6.1 ([1a40ffc](https://github.com/stencila/hub/commit/1a40ffce4571263920d23f6d6117b83b6e6c8aca))
* **deps:** update dependency pillow to v8.0.1 ([77baa49](https://github.com/stencila/hub/commit/77baa49c9c417d2864b452abfa7876d9babd316c))
* **deps:** update dependency sentry-sdk to v0.19.1 ([bf4bfe3](https://github.com/stencila/hub/commit/bf4bfe30174cc335b69fc34b0ff9f68ef08a5ee9))
* **deps:** update dependency setuptools to v50.3.2 ([19fe912](https://github.com/stencila/hub/commit/19fe912b22f91b49796b12d881ff2f77b836c041))
* **deps:** update dependency urllib3 to v1.25.11 ([877ea1d](https://github.com/stencila/hub/commit/877ea1d4e39898a5a5952dd2029277d0acf65134))
* **File detail:** Display images ([4d48f71](https://github.com/stencila/hub/commit/4d48f718249460936027d0377730b2fdbed3ab6e))
* **Worker:** Improve mimetype resolution ([d8b38ca](https://github.com/stencila/hub/commit/d8b38cac08668503256a800c867be373124f9722))


### Features

* **FIle browser:** Add tooltip for mimetype ([7e0e3c4](https://github.com/stencila/hub/commit/7e0e3c46ad4db29a57a5b9ca2b8522ff113924fa))

# [4.8.0](https://github.com/stencila/hub/compare/v4.7.0...v4.8.0) (2020-10-23)


### Bug Fixes

* **Worker:** Improvements to pull jobs ([1b0c1ba](https://github.com/stencila/hub/commit/1b0c1baf8372e0daba6efd710336adc1918f2621))


### Features

* **Manager:** Allow source path to be null ([325d4b6](https://github.com/stencila/hub/commit/325d4b6211c83fffa9ab5d14ff6dcfb0af3ccc67))
* **Worker:** Allow gdive, github and elife pull jobs to select default path ([195e7b2](https://github.com/stencila/hub/commit/195e7b26333317e4a900ff3d0ab0d98a8dc5e9d6))

# [4.7.0](https://github.com/stencila/hub/compare/v4.6.4...v4.7.0) (2020-10-22)


### Bug Fixes

* **Accounts API:** Provide account details in project; redact private account fields; improve typing of account image ([33631fb](https://github.com/stencila/hub/commit/33631fb35f8d8eaddf970c38364ad4e7dd112e2b))
* **Robots.txt:** Disallow /me paths ([fc970ad](https://github.com/stencila/hub/commit/fc970ad5ccc784c2cb41b4056611672df07a8024))


### Features

* **Manager:** Resolve canonical project URL from /projects/<int> ([5dc55da](https://github.com/stencila/hub/commit/5dc55daab673bf2c030eb89d59ae4c81e69b74d3))

## [4.6.4](https://github.com/stencila/hub/compare/v4.6.3...v4.6.4) (2020-10-21)


### Bug Fixes

* **Admin:** Register child models ([72c0e15](https://github.com/stencila/hub/commit/72c0e15a1dd565c1b2c3bdfa7cffe53008cede28))
* **deps:** update dependency kubernetes to v12 ([2fcdafa](https://github.com/stencila/hub/commit/2fcdafaa94e4f22c07f569584cab7ff963fe1537))
* **deps:** update dependency pillow to v8 ([a35cd82](https://github.com/stencila/hub/commit/a35cd825b8a94b4431211e2a77952a62edb104a8))
* **Sources:** Handle permission errors on events ([4b7cbdf](https://github.com/stencila/hub/commit/4b7cbdf2145bfc6e2536a637b335ed28e47a8fdb))

## [4.6.3](https://github.com/stencila/hub/compare/v4.6.2...v4.6.3) (2020-10-21)


### Bug Fixes

* **Sources:** Allow access to event for private projects; custom event handling for GoogleSource ([30dfbf1](https://github.com/stencila/hub/commit/30dfbf1a4584aef370935cc86527dc84a61e57e3))
* **Sources:** Unwatch a source before deletion ([11b74c4](https://github.com/stencila/hub/commit/11b74c4900a6370c6dac0919d634b98989c78a73))

## [4.6.2](https://github.com/stencila/hub/compare/v4.6.1...v4.6.2) (2020-10-20)


### Bug Fixes

* **Sources:** Do not require authentication for event endpoint ([e6d4936](https://github.com/stencila/hub/commit/e6d493683902a9b9c1eb770b8c6863683bdd28f1))

## [4.6.1](https://github.com/stencila/hub/compare/v4.6.0...v4.6.1) (2020-10-20)


### Bug Fixes

* **Sources:** Add waffle_tags ([d0092e6](https://github.com/stencila/hub/commit/d0092e61c33778ae8860acf48cccae15d7c0a689))
* **Sources:** Fix webhook URL and add toggle for testing ([3913b7d](https://github.com/stencila/hub/commit/3913b7d8940ffe0143ef1ea7364fee1bcbca382b))

# [4.6.0](https://github.com/stencila/hub/compare/v4.5.1...v4.6.0) (2020-10-20)


### Bug Fixes

* **Project events:** Fix migration and serializers, add admin ([baae341](https://github.com/stencila/hub/commit/baae3418e0c204f5dfcf2a8b955600f791b09998))
* **Project sources:** Implement GoogleSource watch and unwatch ([22a78f5](https://github.com/stencila/hub/commit/22a78f5a567e3fdbc9cae28e67e0991597a7263f))


### Features

* **Assistant:** Add the assistant service ([fee3ac2](https://github.com/stencila/hub/commit/fee3ac217a6b986a1fcfc021208c609209b56920))
* **Project sources:** Add watch subscriptions and event handling ([4c5e485](https://github.com/stencila/hub/commit/4c5e485c772872d96a076b3c01e6d2d30736f762))

## [4.5.1](https://github.com/stencila/hub/compare/v4.5.0...v4.5.1) (2020-10-19)


### Bug Fixes

* **Jobs:** Allow access to jobs in private projects using key ([6b7f5dd](https://github.com/stencila/hub/commit/6b7f5dd12b73966680bd7547cc4228af713a91b8))

# [4.5.0](https://github.com/stencila/hub/compare/v4.4.0...v4.5.0) (2020-10-16)


### Bug Fixes

* **GitHub source:** Handle large files, keep credentials in worker ([0077764](https://github.com/stencila/hub/commit/0077764e667c9c1d100d6718f4627cb874c03595))
* **Worker:** Fixes to Github pull job ([f99c504](https://github.com/stencila/hub/commit/f99c504e559a88a69017250720a8e9a38182aedf))


### Features

* **GitHub source:** Renable pulling from GitHub repos ([b2fd658](https://github.com/stencila/hub/commit/b2fd658abecb8df0c5ad9d51e48d097f845d93eb))

# [4.4.0](https://github.com/stencila/hub/compare/v4.3.0...v4.4.0) (2020-10-16)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.99.13 ([f9cd393](https://github.com/stencila/hub/commit/f9cd393dcc5295073828bd53bdcb355cb081dc0f))
* **deps:** update dependency django-allauth to v0.43.0 ([ca322a6](https://github.com/stencila/hub/commit/ca322a69dcfb74b78dd82830a09a2b8b1909faa6))
* **deps:** update dependency sentry-sdk to v0.19.0 ([c02a5a9](https://github.com/stencila/hub/commit/c02a5a93f9abc0ad41faa870ed7ed3e2ed89ff5c))
* **deps:** update dependency setuptools to v50.3.1 ([03936ac](https://github.com/stencila/hub/commit/03936ace57c26c053891727a4ebbbdf1f423bea5))
* **GoogleDoc source:** Add logo to form ([efbf7c3](https://github.com/stencila/hub/commit/efbf7c3298816738eef901a34d7e985a0a8134ae))
* **Project sources:** Check that a source is not duplicated. ([13805bf](https://github.com/stencila/hub/commit/13805bf48b24bf1bdea5c389ff623be96ff89cc1)), closes [#681](https://github.com/stencila/hub/issues/681)


### Features

* **GoogleDrive source:** Enable pullling files and folders from Google Drive ([3746659](https://github.com/stencila/hub/commit/3746659aa8ce9b4edd78bc36bdadb8232ef7b1b7))

# [4.3.0](https://github.com/stencila/hub/compare/v4.2.2...v4.3.0) (2020-10-15)


### Bug Fixes

* **Worker:** Ensure that the orginal format of the input is ussed via the --from option ([d6bf12a](https://github.com/stencila/hub/commit/d6bf12aee4bfb4c5659d79a924ee55ac8a24bcbe))


### Features

* **Files:** Add any source from convert job ([148d2a0](https://github.com/stencila/hub/commit/148d2a0d7be321cfefe8bed27d36563fbb9c688f))
* **Worker:** When converting to GDoc create a GDoc ([a1a4d26](https://github.com/stencila/hub/commit/a1a4d264def9038c415afa60bad70b4b17efb1ff))

## [4.2.2](https://github.com/stencila/hub/compare/v4.2.1...v4.2.2) (2020-10-14)


### Bug Fixes

* **Social accounts:** Reauthenticate when connecting; improve styling. ([4cbce69](https://github.com/stencila/hub/commit/4cbce69c6bb635b13542aa3a902e27eb8b5d5280)), closes [#758](https://github.com/stencila/hub/issues/758)

## [4.2.1](https://github.com/stencila/hub/compare/v4.2.0...v4.2.1) (2020-10-14)


### Bug Fixes

* **GDoc:** Add link in access token error message ([14856d0](https://github.com/stencila/hub/commit/14856d0d9f194a3d1c13f9d2112366fdf6ea50e0))

# [4.2.0](https://github.com/stencila/hub/compare/v4.1.5...v4.2.0) (2020-10-14)


### Bug Fixes

* **GDoc pull:** Allow for tokens to be refreshed ([4fb8050](https://github.com/stencila/hub/commit/4fb805046fc55475ce924046972747d969a16b14))
* **Project settings:** Container image should be blank not None ([2419be7](https://github.com/stencila/hub/commit/2419be74f91bb89d38881fd011a256964a2e9164))
* **Project sources:** Set creator of source ([e628580](https://github.com/stencila/hub/commit/e628580b389984a68a4d64ac2eb0a2e4578e5ff3))
* **Upload pull:** Allow for keyword args ([5e01e7e](https://github.com/stencila/hub/commit/5e01e7ef4fbe183bdc357de639d1d9026794364f))


### Features

* **Project sources:** Enable GoogleDocs as source ([49e6c6e](https://github.com/stencila/hub/commit/49e6c6e33fd8728bc4a7733ea290a044aa7d5b04))
* **Worker:** Allow explicit mimetype ([c1cf8db](https://github.com/stencila/hub/commit/c1cf8dbd0084ec530c15fe4f0ca13b4f76e97436))

## [4.1.5](https://github.com/stencila/hub/compare/v4.1.4...v4.1.5) (2020-10-14)


### Bug Fixes

* **API:** Avoid warnings during schema generation ([1ec3256](https://github.com/stencila/hub/commit/1ec325613ebdb1f2d6d86a9707b6953281c7c478)), closes [#755](https://github.com/stencila/hub/issues/755)
* **API:** Improve schema generation for creating a project source. ([613e533](https://github.com/stencila/hub/commit/613e5330413eae0309623a0589e0bed9e0fdf240))

## [4.1.4](https://github.com/stencila/hub/compare/v4.1.3...v4.1.4) (2020-10-13)


### Bug Fixes

* Downgrade to Celery 4.4.6 ([c75c2bb](https://github.com/stencila/hub/commit/c75c2bb12bf106e8e6f6206f7c948773b4709d30))

## [4.1.3](https://github.com/stencila/hub/compare/v4.1.2...v4.1.3) (2020-10-13)


### Bug Fixes

* **Worker:** Also specify options in CLI in Dockerfile ([a326090](https://github.com/stencila/hub/commit/a326090b31a805ee71260ed243c817ed52569e13))
* **Worker:** Do not use mounter sidecar container ([4ebb4d6](https://github.com/stencila/hub/commit/4ebb4d6671c0cdf91019bbcbbc934ae9d7aac29b))

## [4.1.2](https://github.com/stencila/hub/compare/v4.1.1...v4.1.2) (2020-10-13)


### Bug Fixes

* **Jobs:** Improve calculation of runtime ([05066ed](https://github.com/stencila/hub/commit/05066eda2a76042adb073d92bbcb24a726030bd4))
* **Worker:** Correct function name ([9abbcb7](https://github.com/stencila/hub/commit/9abbcb7c0a4f8f1079759c48b0d2a3e00a8bbe99))

## [4.1.1](https://github.com/stencila/hub/compare/v4.1.0...v4.1.1) (2020-10-12)


### Bug Fixes

* **Jobs:** Show subjobs ordered by id ([2d7d9ce](https://github.com/stencila/hub/commit/2d7d9ce1d867d75d8eff322b90920a6d2b54c161))
* **Jobs:** Test if child job is inactive after potential cancellation ([02b0fe2](https://github.com/stencila/hub/commit/02b0fe247c012124a5f1908df70c29118a755e8e))
* **Worker:** Session working directory must be host path ([e849a7d](https://github.com/stencila/hub/commit/e849a7d944808b8a32d717de84b1bbd32fd322de))

# [4.1.0](https://github.com/stencila/hub/compare/v4.0.2...v4.1.0) (2020-10-12)


### Bug Fixes

* **Account content:** Show required domain in assertion message ([e7748a0](https://github.com/stencila/hub/commit/e7748a0338ed5de8ca77bbc63a86f527648e69b1))
* **Worker:** Warn if DJANGO_SENTRY_DSN is not set ([e03be2b](https://github.com/stencila/hub/commit/e03be2b76dd8578474caffba64dd3a2e84998b91))


### Features

* **Snapshots:** Instate pinning for all users ([a084c22](https://github.com/stencila/hub/commit/a084c22b5cf014ea2beb71b938c2eae702d9007b))

## [4.0.2](https://github.com/stencila/hub/compare/v4.0.1...v4.0.2) (2020-10-12)


### Bug Fixes

* **Steward:** Alter permissions for mounts ([0565897](https://github.com/stencila/hub/commit/05658979ff23800433474e6a60de239180f02e64))

## [4.0.1](https://github.com/stencila/hub/compare/v4.0.0...v4.0.1) (2020-10-12)


### Bug Fixes

* **Worker:** Remove redundant RUN in Dockerfile ([a41def3](https://github.com/stencila/hub/commit/a41def36f27026574c573c7aebc853fd70384d8c))

# [4.0.0](https://github.com/stencila/hub/compare/v3.43.3...v4.0.0) (2020-10-12)


### Bug Fixes

* **Manager sources:** Avoid recursion on delete ([8764347](https://github.com/stencila/hub/commit/876434797c256ed4bc57a2b01369ca8808376031)), closes [#754](https://github.com/stencila/hub/issues/754)


### Features

* **Manager:** Attempt to handle WebComponent loading errors ([8880251](https://github.com/stencila/hub/commit/888025159c1468d46afed27eb4de0f7a1306a9a1))
* **Project sessions:** Sessions can be started in a project's working directory ([17c6047](https://github.com/stencila/hub/commit/17c60473c5571999ccaf68b9d83aee008f9966f1))


### BREAKING CHANGES

* **Project sessions:** Significant changes to deployment configuration in this and other recent commits warrant a major version bump.

## [3.43.3](https://github.com/stencila/hub/compare/v3.43.2...v3.43.3) (2020-10-11)


### Bug Fixes

* **Worker, Manager:** upgrades necessary for Celery 5.0 ([c3292af](https://github.com/stencila/hub/commit/c3292af972800510be9adea9832e5214fd43cb85))

## [3.43.2](https://github.com/stencila/hub/compare/v3.43.1...v3.43.2) (2020-10-10)


### Bug Fixes

* **deps:** update dependency amqp to v5 ([4e7ba37](https://github.com/stencila/hub/commit/4e7ba37f959471521be919ba4c411a79e3597e8e))
* **deps:** update dependency celery to v5 ([2c8f987](https://github.com/stencila/hub/commit/2c8f987cab7c1d93d9248b733eccef0c7cb0119a))
* **Deps:** Update Celery invocations for change in CLI args ([47b8c19](https://github.com/stencila/hub/commit/47b8c197d27447e0406faaeb40b979933dffec27)), closes [/docs.celeryproject.org/en/stable/whatsnew-5.0.html#v500](https://github.com//docs.celeryproject.org/en/stable/whatsnew-5.0.html/issues/v500)

## [3.43.1](https://github.com/stencila/hub/compare/v3.43.0...v3.43.1) (2020-10-09)


### Bug Fixes

* **deps:** update dependency @stencila/thema to v2.19.1 ([be002be](https://github.com/stencila/hub/commit/be002be6a303f81dd94a343618207e927fbce3c4))
* **deps:** update dependency httpx to v0.16.1 ([34cd8af](https://github.com/stencila/hub/commit/34cd8af5d81b4076a4173486ef40df04e8bf7f95))
* **deps:** update dependency pytest to v6 ([de7e50c](https://github.com/stencila/hub/commit/de7e50c90997c60e64633b785075755086a0ae13))

# [3.43.0](https://github.com/stencila/hub/compare/v3.42.0...v3.43.0) (2020-10-07)


### Bug Fixes

* **Worker:** Use correct image digest ([4ff8582](https://github.com/stencila/hub/commit/4ff8582c9355a9e4389a89c0e338325a395a1556))


### Features

* **Projects:** Specify and pin container image used to run project ([eccbd0a](https://github.com/stencila/hub/commit/eccbd0a62109b6b3e067700f1f78e987b950f299))
* **Worker:** Add "pin" job ([b3dfa2f](https://github.com/stencila/hub/commit/b3dfa2fcb0087b7e36865b53d83b8d74966c8e14))

# [3.42.0](https://github.com/stencila/hub/compare/v3.41.2...v3.42.0) (2020-10-07)


### Features

* **User API:** Add fields from a user's personal account to /users/{id} ([ed74e3f](https://github.com/stencila/hub/commit/ed74e3f7aa9123fb8d4391cd8ac5da6a8774d2fd))
* **Users API:** Add fields to /users/me ([fff3f4a](https://github.com/stencila/hub/commit/fff3f4a94d6fd7af570d9d619eb37b188eeddfbb))
* **Users API:** Allow user to be retrieved using username or id ([78b7847](https://github.com/stencila/hub/commit/78b784713cf265fefa8734bbb06074709532cd0f))

## [3.41.2](https://github.com/stencila/hub/compare/v3.41.1...v3.41.2) (2020-10-06)


### Bug Fixes

* **Acounts API:** Add docs for parameters ([ff0792a](https://github.com/stencila/hub/commit/ff0792a5e4921c4aa27d226ea23c1196d229e867))

## [3.41.1](https://github.com/stencila/hub/compare/v3.41.0...v3.41.1) (2020-10-06)


### Bug Fixes

* **TS Client:** Fix packaging of TypeScript client ([0a5010d](https://github.com/stencila/hub/commit/0a5010d41200f2201b89744cb628033ebbd8b360))

# [3.41.0](https://github.com/stencila/hub/compare/v3.40.3...v3.41.0) (2020-10-05)


### Features

* **Nodes:** Add nodes to manager ([795e5a1](https://github.com/stencila/hub/commit/795e5a1526885294a820d74369be097d12c94ebd))
* **Typescript API client:** Add initial version ([c353143](https://github.com/stencila/hub/commit/c353143c9d02c80f939e866b064cdb24d66dc2c2))
* **Typescript client:** Only publish dist folder ([b72ada6](https://github.com/stencila/hub/commit/b72ada644a3657e53bef6fb9ac228896579ea75e))

## [3.40.3](https://github.com/stencila/hub/compare/v3.40.2...v3.40.3) (2020-10-05)


### Bug Fixes

* **deps:** update dependency pytest-randomly to v3 ([20925e1](https://github.com/stencila/hub/commit/20925e1b82656bf233a26f273ea798447233a6d2))
* **Python client:** Do not generate Tox file ([4e04292](https://github.com/stencila/hub/commit/4e04292dd5749697d6bdadc974843d24a4538fda))
* **Python client:** Put ampersands in the correct place ([919f2cd](https://github.com/stencila/hub/commit/919f2cd1f238a6bcdb5c52e43ab0f2ce3c97fa49))

## [3.40.2](https://github.com/stencila/hub/compare/v3.40.1...v3.40.2) (2020-10-04)


### Bug Fixes

* **deps:** update dependency htmx.org to v0.2.0 ([89b0011](https://github.com/stencila/hub/commit/89b00113bb3e0bc7aff724d71cf9582bfd239146))

## [3.40.1](https://github.com/stencila/hub/compare/v3.40.0...v3.40.1) (2020-10-04)


### Bug Fixes

* **deps:** pin dependencies ([dec596e](https://github.com/stencila/hub/commit/dec596e8db38c255e71923022e100ff6181898c9))
* **deps:** update dependency @popperjs/core to v2.5.3 ([289fd75](https://github.com/stencila/hub/commit/289fd75a9b370ef0c7b22014a892a52c48fe1eea))
* **deps:** update dependency @stencila/executa to v1.14.2 ([75b520b](https://github.com/stencila/hub/commit/75b520b80db7fc2d1bdb3319dfe09d0ef544fdf4))
* **deps:** update dependency bulma to v0.9.1 ([146f6a4](https://github.com/stencila/hub/commit/146f6a4d7bda5558206d5ab287095fb9fa99400b))
* **deps:** update dependency django to v3.1.2 ([0bdcf74](https://github.com/stencila/hub/commit/0bdcf74d124f71d479ebee3b711911c025df2477))
* **deps:** update dependency djangorestframework to v3.12.1 ([0025475](https://github.com/stencila/hub/commit/00254758c45c756c7266a59d91c18517f56205c8))
* **deps:** update dependency google-api-python-client to v1.12.3 ([0d8db2a](https://github.com/stencila/hub/commit/0d8db2a919bec738d1dbb410145e87fb20978f4e))
* **deps:** update dependency httpx to v0.15.5 ([317c9c9](https://github.com/stencila/hub/commit/317c9c9d77bf1bb6a4ac5c2eaae6c2becf8da628))
* **deps:** update dependency sentry-sdk to v0.18.0 ([14938bb](https://github.com/stencila/hub/commit/14938bb6a5991f8953c76605fc78f93a4fc7642b))
* **Manager styles:** New file extension for Bulma file ([a3315b3](https://github.com/stencila/hub/commit/a3315b38687351af1ffc98f7241b0119bf4ccebd))

# [3.40.0](https://github.com/stencila/hub/compare/v3.39.1...v3.40.0) (2020-09-30)


### Features

* **Python API client:** Add initial version ([2f82a15](https://github.com/stencila/hub/commit/2f82a15ebd684d7aee992ddfe6e471a8dffe0acf))

## [3.39.1](https://github.com/stencila/hub/compare/v3.39.0...v3.39.1) (2020-09-30)


### Bug Fixes

* **Deps:** Upgrade Thema ([e3d28f6](https://github.com/stencila/hub/commit/e3d28f6e55b64e50c7a98008d5d576f3ae00d2cf))

# [3.39.0](https://github.com/stencila/hub/compare/v3.38.0...v3.39.0) (2020-09-28)


### Bug Fixes

* **PLOS Source:** Use correct URL for graphics, fail on 404 ([1d91ef9](https://github.com/stencila/hub/commit/1d91ef9811ecd19557ac7a108975b3596c7ddd04))


### Features

* **PLOS Source:** Enable PLOS article as a project source ([76c3a16](https://github.com/stencila/hub/commit/76c3a16b6d05e16b76b284debcc59bdbc3d234f1))

# [3.38.0](https://github.com/stencila/hub/compare/v3.37.9...v3.38.0) (2020-09-28)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.99.11 ([d63ea19](https://github.com/stencila/hub/commit/d63ea192894eb3168c3f0bfa45a1eab69bf30b6a))
* **deps:** update dependency google-cloud-storage to v1.31.2 ([b508c0a](https://github.com/stencila/hub/commit/b508c0a37b5cd856e35eea17772256f8150c57e6))
* **Project sources:** Only set address if it is absent ([028f347](https://github.com/stencila/hub/commit/028f3478fe841706d692945dd8ac3c9deea6581c))
* **Projects:** Only apply role filter if user is authenticated ([7f2de62](https://github.com/stencila/hub/commit/7f2de626dffc4729f0e951e23caf0009acb12c04))
* **Sources:** Pass user when creating source pull ([01fd51d](https://github.com/stencila/hub/commit/01fd51d1ecfc9128ed5483f43b76791ae85a58b5))


### Features

* **API:** Allow role filter to include multiple roles ([46acff3](https://github.com/stencila/hub/commit/46acff3cf00e2e0e9785b7385718d80bbfb5067b))
* **Manager:** Add filtering of project based on role and presence of source ([e42342d](https://github.com/stencila/hub/commit/e42342dd3c2da45d0dbe5da97d8ec96c238f9d40)), closes [#705](https://github.com/stencila/hub/issues/705)
* **Project sources:** Allow filtering by address ([a7ce92f](https://github.com/stencila/hub/commit/a7ce92fcc8e7a618d46be7a338ef470de8ce64b6))

## [3.37.9](https://github.com/stencila/hub/compare/v3.37.8...v3.37.9) (2020-09-27)


### Bug Fixes

* **deps:** update dependency @popperjs/core to v2.5.2 ([e6d3698](https://github.com/stencila/hub/commit/e6d3698ed540382d67fce8d737a0aaf91d629864))
* **deps:** update dependency django-imagefield to v0.12.4 ([4cfb8d2](https://github.com/stencila/hub/commit/4cfb8d2a1cc696c59436e4575e8afe5eb00faf85))
* **deps:** update dependency google-api-python-client to v1.12.2 ([d06d76a](https://github.com/stencila/hub/commit/d06d76a2192df86bffa5ca90d40b16d90437c2c9))
* **deps:** update dependency htmx.org to v0.1.2 ([e76e503](https://github.com/stencila/hub/commit/e76e5038b8ed06e8477ea9dca99acdf608318e77))
* **deps:** update dependency httpx to v0.15.4 ([d9cdaba](https://github.com/stencila/hub/commit/d9cdabae73f0ad2eb9ea015f20c450b0c7f421e3))
* **deps:** update dependency sentry-sdk to v0.17.8 ([7ce3bf1](https://github.com/stencila/hub/commit/7ce3bf12a4defc894ff3b5b05a02595ebf015bb5))
* **deps:** update dependency typescript to v4.0.3 ([b7461e9](https://github.com/stencila/hub/commit/b7461e9bfcb9d12dd4857c7b42eac97018492c77))
* **Deps:** npm audit fix ([e90c9e3](https://github.com/stencila/hub/commit/e90c9e3b22784cbbcf8d803175eecfd95c9a9f4c))

## [3.37.8](https://github.com/stencila/hub/compare/v3.37.7...v3.37.8) (2020-09-22)


### Bug Fixes

* **Deps:** Update Thema version ([a6f2f8f](https://github.com/stencila/hub/commit/a6f2f8f5c2ad5732a055e2a2cba2a17abb7257dc))

## [3.37.7](https://github.com/stencila/hub/compare/v3.37.6...v3.37.7) (2020-09-21)


### Bug Fixes

* **Steward:** Revert to umask 0007; 0000 is not necessary ([703d1ad](https://github.com/stencila/hub/commit/703d1ad4077c197c4d7251ad02d32e78d85e55c3))
* **Worker:** Use steward snapshot mounts ([f312578](https://github.com/stencila/hub/commit/f3125781eade8ae216d4af83fee90f2302957f02))

## [3.37.6](https://github.com/stencila/hub/compare/v3.37.5...v3.37.6) (2020-09-20)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.99.8 ([d4a6ff7](https://github.com/stencila/hub/commit/d4a6ff7e073fab6a56cef5095c0402c3a227dea4))
* **deps:** update dependency @stencila/thema to v2.17.2 ([ea686fb](https://github.com/stencila/hub/commit/ea686fb11ca6983ce40f5e077eac51682e2c0d49))
* **deps:** update dependency django-extensions to v3.0.9 ([b57d190](https://github.com/stencila/hub/commit/b57d1909f38c8359fe40c8b2cd3af3afabf0c219))
* **deps:** update dependency django-imagefield to v0.12.3 ([6168fdb](https://github.com/stencila/hub/commit/6168fdb47dc5cb3611f3551a92bc632582f157dc))
* **deps:** update dependency django-storages to v1.10.1 ([83d453f](https://github.com/stencila/hub/commit/83d453f7aa61e1141cce90399e1863f3cc166cfa))
* **deps:** update dependency google-api-python-client to v1.12.1 ([dbe1fba](https://github.com/stencila/hub/commit/dbe1fbaed447febfa0a93a5630ade0e7f30df82e))
* **deps:** update dependency pygments to v2.7.1 ([c276378](https://github.com/stencila/hub/commit/c2763781eaaacf4da24ea6700631ca538747894c))
* **deps:** update dependency sentry-sdk to v0.17.6 ([9fdb694](https://github.com/stencila/hub/commit/9fdb6945f2f83fcef4dd5185b05012b0992f19ff))

## [3.37.5](https://github.com/stencila/hub/compare/v3.37.4...v3.37.5) (2020-09-19)


### Bug Fixes

* **Steward:** Change umask to allow other access ([499c188](https://github.com/stencila/hub/commit/499c188df7d3eb277d1d8ff84a6e8fff380a5dd5))

## [3.37.4](https://github.com/stencila/hub/compare/v3.37.3...v3.37.4) (2020-09-18)


### Bug Fixes

* **Router:** Increase the size of buffers ([ae34fc4](https://github.com/stencila/hub/commit/ae34fc46ccbfa6297e78c95fddc7e381dd4cf171)), closes [#690](https://github.com/stencila/hub/issues/690)

## [3.37.3](https://github.com/stencila/hub/compare/v3.37.2...v3.37.3) (2020-09-18)


### Bug Fixes

* **Steward:** Set mount permissions ([fc01fc6](https://github.com/stencila/hub/commit/fc01fc68e13147f90819185259f7e007a9b06061))

## [3.37.2](https://github.com/stencila/hub/compare/v3.37.1...v3.37.2) (2020-09-16)


### Bug Fixes

* **deps:** update dependency typescript to v4 ([3031661](https://github.com/stencila/hub/commit/3031661909227f8feac7c110912755ee5bc198ff))
* **Deps:** Update Stencila Components to v0.23.5 ([985dcd2](https://github.com/stencila/hub/commit/985dcd2558c47c8f79e4be2dd124bccfb000dd71))

## [3.37.1](https://github.com/stencila/hub/compare/v3.37.0...v3.37.1) (2020-09-16)


### Bug Fixes

* **Docke compose:** Add secrets to steward ([5ea6b1b](https://github.com/stencila/hub/commit/5ea6b1bbd7dc94b119e87c52a8b3b1b18ec6b5d7))
* **Stward:** Make shell script executable ([19a435f](https://github.com/stencila/hub/commit/19a435fa2e36e7a7cb5883a7f43f8034d16d8af8))

# [3.37.0](https://github.com/stencila/hub/compare/v3.36.13...v3.37.0) (2020-09-16)


### Bug Fixes

* **Steward:** Use /var/cache rather than /tmp ([5838e44](https://github.com/stencila/hub/commit/5838e44376ca1198f7bd98466da1756caa203040))


### Features

* **Steward:** Add service for providing nodes with access to storage ([adb7966](https://github.com/stencila/hub/commit/adb79666de9bd73af163f1f767c7a4f710566073))

## [3.36.13](https://github.com/stencila/hub/compare/v3.36.12...v3.36.13) (2020-09-15)


### Bug Fixes

* **deps:** update dependency @stencila/thema to v2.17.0 ([605c549](https://github.com/stencila/hub/commit/605c5495d122091a8cc07cf943ec6d6cc8545429))

## [3.36.12](https://github.com/stencila/hub/compare/v3.36.11...v3.36.12) (2020-09-15)


### Bug Fixes

* **Manager:** Do not purge Twitter icon class ([be447b5](https://github.com/stencila/hub/commit/be447b5c756e78d49fb03d0d4ed7b791ab3e1edc))

## [3.36.11](https://github.com/stencila/hub/compare/v3.36.10...v3.36.11) (2020-09-13)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.99.6 ([365fc95](https://github.com/stencila/hub/commit/365fc959e58728d16264d30cd3fe4cf4344e24d0))
* **deps:** update dependency @stencila/executa to v1.14.1 ([bfa4462](https://github.com/stencila/hub/commit/bfa4462f47ce930f7d2a21cdcf9d41375929fada))
* **deps:** update dependency django-extensions to v3.0.8 ([d4e8fd9](https://github.com/stencila/hub/commit/d4e8fd920cb900216243a6a8bf67e46047a9aa35))
* **deps:** update dependency django-storages to v1.10 ([834ad5e](https://github.com/stencila/hub/commit/834ad5e3695212f56d79f8c5e8c29c641262abe6))
* **deps:** update dependency django-waffle to v2 ([e1956d8](https://github.com/stencila/hub/commit/e1956d8c8c89a50a632ddd55b7d037ab9bfb350d))
* **deps:** update dependency httpx to v0.14.3 ([8850670](https://github.com/stencila/hub/commit/8850670edb1584ce6dadf098110f8e21602c4e7b))
* **deps:** update dependency psycopg2-binary to v2.8.6 ([6635c23](https://github.com/stencila/hub/commit/6635c231f4b821ec097222f86571494142ab039a))
* **deps:** update dependency sentry-sdk to v0.17.4 ([24f5cb6](https://github.com/stencila/hub/commit/24f5cb6cca6cc37ebacc78ed7bbaa040dc565adf))

## [3.36.10](https://github.com/stencila/hub/compare/v3.36.9...v3.36.10) (2020-09-11)


### Bug Fixes

* **Deps:** Update Stencila Components dependency ([f1b2f17](https://github.com/stencila/hub/commit/f1b2f17a70cf54c6c5dd5dfd7197039317cfe56e))

## [3.36.9](https://github.com/stencila/hub/compare/v3.36.8...v3.36.9) (2020-09-10)


### Bug Fixes

* **Deps:** Update Manager JS dependencies ([a775e7f](https://github.com/stencila/hub/commit/a775e7fefecb22470995529d208abdcadc8083f3))

## [3.36.8](https://github.com/stencila/hub/compare/v3.36.7...v3.36.8) (2020-09-08)


### Bug Fixes

* **Worker:** Upgrade dependencies ([2eeb0bc](https://github.com/stencila/hub/commit/2eeb0bc9012d80fbc4f754eb55935d4fb01c85fb))

## [3.36.7](https://github.com/stencila/hub/compare/v3.36.6...v3.36.7) (2020-09-07)


### Bug Fixes

* **Worker:** Upgrade Encoda ([08856b5](https://github.com/stencila/hub/commit/08856b59f45ed2cbdd8f50f38add2862d717a465))

## [3.36.6](https://github.com/stencila/hub/compare/v3.36.5...v3.36.6) (2020-09-07)


### Bug Fixes

* **Manager:** Calculate next from the file path ([c20893b](https://github.com/stencila/hub/commit/c20893b9fb7b5312af27f433b7390c3e7dc23f9f))

## [3.36.5](https://github.com/stencila/hub/compare/v3.36.4...v3.36.5) (2020-09-06)


### Bug Fixes

* **deps:** pin dependency @stencila/encoda to 0.99.0 ([3888f3d](https://github.com/stencila/hub/commit/3888f3d701852f68f2874af22695c3732f76fc5a))
* **deps:** update dependency @stencila/encoda to v0.99.1 ([c4c78db](https://github.com/stencila/hub/commit/c4c78db14b7f423bd95263b1efa24ec9a8468909))
* **deps:** update dependency django to v3.1.1 ([1b7aa94](https://github.com/stencila/hub/commit/1b7aa94da63b74c967a3013beae7ca7c3022c5c2))
* **Manager:** Consistent use of null and blank on fields ([7a232ed](https://github.com/stencila/hub/commit/7a232ed36edf5b4fa25b8ad0fc39ff6da254b34f))

## [3.36.4](https://github.com/stencila/hub/compare/v3.36.3...v3.36.4) (2020-09-03)


### Bug Fixes

* **Worker:** Update Encoda system dependencies ([56528f5](https://github.com/stencila/hub/commit/56528f5eb75e3d4ed8e378e57075d02a56ed76e5))

## [3.36.3](https://github.com/stencila/hub/compare/v3.36.2...v3.36.3) (2020-09-03)


### Bug Fixes

* **File highlighting:** Skip binary files; fix resolution of lexer ([d2c084d](https://github.com/stencila/hub/commit/d2c084d0d5ada40dce01c12f802c8cc182f4611d))
* **Manager:** Allow for both prev and next params for jobs ([a6380e5](https://github.com/stencila/hub/commit/a6380e526435f866395f79a28191441f691fce87))
* **Manager:** Typo ([380960c](https://github.com/stencila/hub/commit/380960caf5307e413142584970e98427303e7921))
* **Manager:** Use SameSite Lax in development ([cf824d2](https://github.com/stencila/hub/commit/cf824d27f015e93d9d28bf906ee26b15c4b00ea1))
* **Uploads:** Always pull uploaded files on creation ([c4cc30b](https://github.com/stencila/hub/commit/c4cc30b23886a9c98ab0116234bf8a2a25c25c5f))
* **Worker:** Upgrade Encoda ([4feb4b7](https://github.com/stencila/hub/commit/4feb4b7bbde6bf52da8f885b97e8b1f744962448))

## [3.36.2](https://github.com/stencila/hub/compare/v3.36.1...v3.36.2) (2020-09-02)


### Bug Fixes

* **deps:** update dependency django-cors-headers to v3.5.0 ([85146f4](https://github.com/stencila/hub/commit/85146f45098610dbb7f64e6bbb6ddef8960eabea))
* **deps:** update dependency django-prometheus to v2.1.0 ([898e9b9](https://github.com/stencila/hub/commit/898e9b962ae6dd6ea5c116d277ab140beaafbcdf))
* **deps:** update dependency django-sendgrid-v5 to v0.9.0 ([d8f84e8](https://github.com/stencila/hub/commit/d8f84e843e66950a1e9ad31ea69567c5326e3e87))
* **deps:** update dependency google-api-python-client to v1.11.0 ([80421d3](https://github.com/stencila/hub/commit/80421d322cce77f0de2c5a6ab4bab2e92794dafd))
* **deps:** update dependency google-cloud-storage to v1.31.0 ([a135c2b](https://github.com/stencila/hub/commit/a135c2b1aa652c4083802ec4828c0a60762b5a54))
* **Manager:** Rename django-cors-headers settings ([e89f737](https://github.com/stencila/hub/commit/e89f737625b8f9de114090d515147e366e1b9bcb)), closes [/github.com/adamchainz/django-cors-headers/blob/master/HISTORY.rst#350-2020-08-25](https://github.com//github.com/adamchainz/django-cors-headers/blob/master/HISTORY.rst/issues/350-2020-08-25)

## [3.36.1](https://github.com/stencila/hub/compare/v3.36.0...v3.36.1) (2020-08-28)


### Bug Fixes

* **Manager:** Do not clean and pull in shaphots; reuse file convert method ([bfa3506](https://github.com/stencila/hub/commit/bfa35068b437109ae3d41058144cd006e4900052))
* **Manager:** Pass mimetype to convert job; add format lexers ([2703701](https://github.com/stencila/hub/commit/270370167306ce03178687720bfa44fa768f90a8)), closes [#663](https://github.com/stencila/hub/issues/663)
* **Worker:** Remove destination path if exists ([93fdafb](https://github.com/stencila/hub/commit/93fdafbbf4f1a6189b9187ad9280d328fd11fe40))

# [3.36.0](https://github.com/stencila/hub/compare/v3.35.5...v3.36.0) (2020-08-28)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.98.5 ([784c96f](https://github.com/stencila/hub/commit/784c96ff6ccf44f898dee8ee56dcfe6b105e0ac1))
* **deps:** update dependency brotli to v1.0.9 ([549a85d](https://github.com/stencila/hub/commit/549a85d876c5545e1edc4f1d2020909f0f7ba8b3))
* **deps:** update dependency bulma-toast to v2.0.3 ([b953923](https://github.com/stencila/hub/commit/b9539236d17cf7f854c0d0babb9d9d42c5138d6b))


### Features

* **Account content:** Allow per account and per project content injection ([600dd0a](https://github.com/stencila/hub/commit/600dd0a93a25ed8b78248064a997263c54886562)), closes [#655](https://github.com/stencila/hub/issues/655)

## [3.35.5](https://github.com/stencila/hub/compare/v3.35.4...v3.35.5) (2020-08-27)


### Bug Fixes

* **deps:** update dependency django to v3.1 ([86c4a59](https://github.com/stencila/hub/commit/86c4a591dcd5df9ecd3e4058916618af991708b5))
* **deps:** update dependency django-allauth to v0.42.0 ([1551b8b](https://github.com/stencila/hub/commit/1551b8bdc1163051f097711ae22312722c64ce4c))
* **deps:** update dependency django-extensions to v3.0.5 ([ef50545](https://github.com/stencila/hub/commit/ef505454b08851a2006a7ad38002d6497ce1c260))
* **Manager:** Remove dependency django-jsonfallback ([5682af9](https://github.com/stencila/hub/commit/5682af9ca4f692ece9885fc19da37910fceb2db4)), closes [#660](https://github.com/stencila/hub/issues/660)
* **Manager:** Use None string for SESSION_COOKIE_SAMESITE ([a251ff2](https://github.com/stencila/hub/commit/a251ff2d2aa3008a484493a592634ac80eb0dfc2))

## [3.35.4](https://github.com/stencila/hub/compare/v3.35.3...v3.35.4) (2020-08-27)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.98.3 ([ac985df](https://github.com/stencila/hub/commit/ac985df133b606ebaffae4c1196ef5444ae3ab36))
* **deps:** update dependency django-imagefield to v0.12.2 ([f6f8dca](https://github.com/stencila/hub/commit/f6f8dca5ed1a5aac29f7f46d8ffd3d7f7a9a5031))
* **deps:** update dependency django-polymorphic to v3 ([8500793](https://github.com/stencila/hub/commit/850079375d2f8138e2f754e8382c5baa1d83576c))
* **deps:** update dependency httpx to v0.14.2 ([5ccdd5e](https://github.com/stencila/hub/commit/5ccdd5eb59d8e7302b89d0b24b913c1786c17e38))
* **deps:** update dependency pygithub to v1.53 ([531dd6a](https://github.com/stencila/hub/commit/531dd6a1b74cb3480edcddaf8cc06f4e3d354010))
* **deps:** update dependency sentry-sdk to v0.17.0 ([10b65d4](https://github.com/stencila/hub/commit/10b65d4ab4d50c7e8ea35b51dc88a213898db322))
* **Deps:** Updates to Thema and Components versions ([d1d8e96](https://github.com/stencila/hub/commit/d1d8e9698f9b4b5bf3ed7c270996055a7bd39bcd))

## [3.35.3](https://github.com/stencila/hub/compare/v3.35.2...v3.35.3) (2020-08-24)


### Bug Fixes

* **deps:** update dependency @stencila/thema to v2.16.3 ([3c8a028](https://github.com/stencila/hub/commit/3c8a02804f83a4f42e5e4f11678ce51dd169496e))

## [3.35.2](https://github.com/stencila/hub/compare/v3.35.1...v3.35.2) (2020-08-24)


### Bug Fixes

* **Kubernetes session:** Use flock to avoid races to fetch snapshot ([5b7b215](https://github.com/stencila/hub/commit/5b7b215fb3427df1fbb96bed676551e99b1ea307))

## [3.35.1](https://github.com/stencila/hub/compare/v3.35.0...v3.35.1) (2020-08-24)


### Bug Fixes

* **Worker:** Add support for setting options via env vars ([259d2ea](https://github.com/stencila/hub/commit/259d2ea53b150e6bb87b3f95ca8fc1ade02c7484))

# [3.35.0](https://github.com/stencila/hub/compare/v3.34.2...v3.35.0) (2020-08-23)


### Bug Fixes

* **Overseer:** Perform all blocking work outside of event handling thread ([ccc4104](https://github.com/stencila/hub/commit/ccc4104d2df55dc80657b24006df64ad74c04e27))


### Features

* **Manager:** Add a partial update endpoint for workers separate from online ([fca3929](https://github.com/stencila/hub/commit/fca392960cb09f0ed5e5767e495696827bcb08bc))
* **Overseer:** Send worker update to manager ([bd60b01](https://github.com/stencila/hub/commit/bd60b01a1d41f8439bc3edd6d12fb64483500d15))

## [3.34.2](https://github.com/stencila/hub/compare/v3.34.1...v3.34.2) (2020-08-21)


### Bug Fixes

* **Manager:** Inline Component version number to improve perf ([b9a4bc5](https://github.com/stencila/hub/commit/b9a4bc5c68e72e146e1e9ae7dfc079a04730f25f))

## [3.34.1](https://github.com/stencila/hub/compare/v3.34.0...v3.34.1) (2020-08-21)


### Bug Fixes

* **Deps:** Update Dev Dependencies ([c7391cf](https://github.com/stencila/hub/commit/c7391cfcb15d3e6f6a8af37b12408a35c1ad00b2))
* **Deps:** Update Thema dependency ([8f3230c](https://github.com/stencila/hub/commit/8f3230cf7f22b18ef2dc5b780d4ff10ab95848f8))

# [3.34.0](https://github.com/stencila/hub/compare/v3.33.5...v3.34.0) (2020-08-21)


### Features

* **Overseer:** Send requests to the manager asynchronously ([a23c283](https://github.com/stencila/hub/commit/a23c28387f977506898f7e39268df8673bcdf811))

## [3.33.5](https://github.com/stencila/hub/compare/v3.33.4...v3.33.5) (2020-08-20)


### Bug Fixes

* **Worker:** Revert to prefork pool ([2751751](https://github.com/stencila/hub/commit/27517513bbe868db94c0be04d3a291439f5b3904))

## [3.33.4](https://github.com/stencila/hub/compare/v3.33.3...v3.33.4) (2020-08-20)


### Bug Fixes

* **deps:** update dependency @stencila/executa to v1.14.0 ([8355952](https://github.com/stencila/hub/commit/835595207929ee2e8bd466e5822b3319292b6830))

## [3.33.3](https://github.com/stencila/hub/compare/v3.33.2...v3.33.3) (2020-08-20)


### Bug Fixes

* **Kubernetes session:** Use polling instead of attaching ([b906fcb](https://github.com/stencila/hub/commit/b906fcb4e11c301f46e0b267b91b57cc2cd9016f))

## [3.33.2](https://github.com/stencila/hub/compare/v3.33.1...v3.33.2) (2020-08-20)


### Bug Fixes

* **Kubernetes session:** Ignore if session already created ([06e8c17](https://github.com/stencila/hub/commit/06e8c17c5cec663cc7f2e9e66a30d6ce8bbb29e5))
* **Workers:** Use gevent for greater concurrency, settable as an env var ([1178657](https://github.com/stencila/hub/commit/1178657ce735be228ae9ae86d8741fd20210024d))

## [3.33.1](https://github.com/stencila/hub/compare/v3.33.0...v3.33.1) (2020-08-20)


### Bug Fixes

* **Router:** Do not pass basic auth header on to manager ([0c9ed79](https://github.com/stencila/hub/commit/0c9ed79954ef8abed560de391af4c5f8844896bf))

# [3.33.0](https://github.com/stencila/hub/compare/v3.32.5...v3.33.0) (2020-08-19)


### Bug Fixes

* **Manager:** Allow either token or username/password with basic auth ([e0b073a](https://github.com/stencila/hub/commit/e0b073a194eab98abab185124f441c7969bae683))


### Features

* **Manager:** Allow configuration of API throttling ([9b52696](https://github.com/stencila/hub/commit/9b5269638706b15dda2191229d5581c7734603cc))

## [3.32.5](https://github.com/stencila/hub/compare/v3.32.4...v3.32.5) (2020-08-19)


### Bug Fixes

* **Manager:** Default to allowing basic auth API access in staging ([a67d08b](https://github.com/stencila/hub/commit/a67d08b4b0eb5564c7c5dc9733700e3b1994444c))

## [3.32.4](https://github.com/stencila/hub/compare/v3.32.3...v3.32.4) (2020-08-19)


### Bug Fixes

* **Router:** Add LB public IP as trusted ([71692d6](https://github.com/stencila/hub/commit/71692d60bd639df0a70c8f920b1abb735151a94a))

## [3.32.3](https://github.com/stencila/hub/compare/v3.32.2...v3.32.3) (2020-08-19)


### Bug Fixes

* **Router:** More fine tuning for running behind GLB ([c49f53a](https://github.com/stencila/hub/commit/c49f53a523510750fe48d7ab8901d6bcaeedcf3d))

## [3.32.2](https://github.com/stencila/hub/compare/v3.32.1...v3.32.2) (2020-08-19)


### Bug Fixes

* **Router:** Get the real IP address ([633a125](https://github.com/stencila/hub/commit/633a1250ee9c4410a99e17853837b73aeddea883))

## [3.32.1](https://github.com/stencila/hub/compare/v3.32.0...v3.32.1) (2020-08-19)


### Bug Fixes

* **Router:** Add domain for staging ([31f9519](https://github.com/stencila/hub/commit/31f9519fc36bedb78083b20b73a31e02780dcdb3))
* **Router:** Allow private IPs to bypass basic auth ([6b5f7f1](https://github.com/stencila/hub/commit/6b5f7f1cc7668f01ea8aa287f2eadc074619efa1))

# [3.32.0](https://github.com/stencila/hub/compare/v3.31.1...v3.32.0) (2020-08-19)


### Features

* **Router:** Allow for basic auth for staging env ([6f18d3d](https://github.com/stencila/hub/commit/6f18d3decc2a08c53986d0dc1c1f68589a6e254a))


### Reverts

* Revert "fix(Worker): Use startupProbe for sessions" ([a4d2dd9](https://github.com/stencila/hub/commit/a4d2dd917b0a94d89376ce92952a9a35a58d0bde))

## [3.31.1](https://github.com/stencila/hub/compare/v3.31.0...v3.31.1) (2020-08-17)


### Bug Fixes

* **Worker:** Use startupProbe for sessions ([f086261](https://github.com/stencila/hub/commit/f086261c502921f6d07676d1fba15c21563ee8f6))

# [3.31.0](https://github.com/stencila/hub/compare/v3.30.6...v3.31.0) (2020-08-17)


### Features

* **Worker:** Set resources and node pool for sessions ([1d03746](https://github.com/stencila/hub/commit/1d037465ee061b97da042683735b670b9c109ab5))

## [3.30.6](https://github.com/stencila/hub/compare/v3.30.5...v3.30.6) (2020-08-17)


### Bug Fixes

* **Router:** Increase proxy send and read timeout for Websockets ([b3a5a4e](https://github.com/stencila/hub/commit/b3a5a4eab71ae9944485f9eff3caec94a23f2f63))

## [3.30.5](https://github.com/stencila/hub/compare/v3.30.4...v3.30.5) (2020-08-17)


### Bug Fixes

* **Manager:** Catch Resolver404 exceptions ([77cca64](https://github.com/stencila/hub/commit/77cca64286d0fe028c994c3339460fee6ce48413))

## [3.30.4](https://github.com/stencila/hub/compare/v3.30.3...v3.30.4) (2020-08-16)


### Bug Fixes

* **Base template:** Upgrade Sentry and change navbar logo link ([36f544c](https://github.com/stencila/hub/commit/36f544cf249dce0377169fd089c51dd19d4b5c5a))
* **Pricing plans:** Remove empty help text icon ([4719cd0](https://github.com/stencila/hub/commit/4719cd0346005edbbc4c15d6d2f9664039085c57))
* **Router:** Remove report dialog and update Sentry DSN ([67c083f](https://github.com/stencila/hub/commit/67c083fc2f5f1213a7ef65a4844a2167b1b4237e))

## [3.30.3](https://github.com/stencila/hub/compare/v3.30.2...v3.30.3) (2020-08-16)


### Bug Fixes

* **Projects:** Only consider current files when choosing main file ([2c79ff1](https://github.com/stencila/hub/commit/2c79ff1cb6cbe5a274997660c83c81763767873d))
* **Router:** Add status page link to 50x; remove uneeded script tag ([104cc1c](https://github.com/stencila/hub/commit/104cc1c86b25c3fac0e6ce4d8fd09a5b6aa074fc))

## [3.30.2](https://github.com/stencila/hub/compare/v3.30.1...v3.30.2) (2020-08-16)


### Bug Fixes

* **Router:** Optimize Nginx config ([3bcbd80](https://github.com/stencila/hub/commit/3bcbd807c98d411f6027d5cbc55486e9e1df4522))

## [3.30.1](https://github.com/stencila/hub/compare/v3.30.0...v3.30.1) (2020-08-16)


### Bug Fixes

* **Router:** Increase number of worker connections ([4d38507](https://github.com/stencila/hub/commit/4d38507303294532a6907f79d84d47e05706da5c))

# [3.30.0](https://github.com/stencila/hub/compare/v3.29.3...v3.30.0) (2020-08-15)


### Bug Fixes

* **Account content:** Revert setting of script-src etc CSP directives ([35c22ea](https://github.com/stencila/hub/commit/35c22ea78d3c875177ae704453c7251886ca6e7a))
* **Template tags:** Check for match ([e0be30e](https://github.com/stencila/hub/commit/e0be30e416fec0cd2136ad5c2c65bac6192ff89e))


### Features

* **Plans:** Updating pricing view & add public pricing page ([30f82ab](https://github.com/stencila/hub/commit/30f82aba3d4e6bd476d0c467a864e73ec221a5fa))

## [3.29.3](https://github.com/stencila/hub/compare/v3.29.2...v3.29.3) (2020-08-15)


### Bug Fixes

* **Account content:** Correct syntax for script-src ([605d900](https://github.com/stencila/hub/commit/605d9003d609e760297ea7838f8d194f0535c767))

## [3.29.2](https://github.com/stencila/hub/compare/v3.29.1...v3.29.2) (2020-08-15)


### Bug Fixes

* **Account content:** Add CSP directives needed for Sentry integration ([f68310d](https://github.com/stencila/hub/commit/f68310d18afd465f943d338913bda7f9fe6d55fa))

## [3.29.1](https://github.com/stencila/hub/compare/v3.29.0...v3.29.1) (2020-08-15)


### Bug Fixes

* **Snapshots:** Add back "New Snapshot" button to snapshot list view ([360597b](https://github.com/stencila/hub/commit/360597bdba298c2b076aa62f06559c6aadb169a1))

# [3.29.0](https://github.com/stencila/hub/compare/v3.28.0...v3.29.0) (2020-08-15)


### Bug Fixes

* **Manager uploads:** Add help text on uploading archives ([94bd88d](https://github.com/stencila/hub/commit/94bd88d5f7334ef0dd681c9c700eeb4750eca95a))
* **Manager worker:** Make get_or_create an atomic transaction ([cf0415b](https://github.com/stencila/hub/commit/cf0415b67ea4335b2654885f906920e32b843439))


### Features

* **Project settings:** Allow setting main file on settings page ([45df91e](https://github.com/stencila/hub/commit/45df91e4a2fc96caecd9bf52f1ae4ea7d4670cf0))
* **Worker:** Unpack archive uploads ([b9cc410](https://github.com/stencila/hub/commit/b9cc41016fd3c995a0b4af9969750047e9f37892))

# [3.28.0](https://github.com/stencila/hub/compare/v3.27.3...v3.28.0) (2020-08-14)


### Features

* **Router:** Increase upload file size limit ([2b95576](https://github.com/stencila/hub/commit/2b95576e1caed97c3f431beaa6e30898b6aa2997))

## [3.27.3](https://github.com/stencila/hub/compare/v3.27.2...v3.27.3) (2020-08-14)


### Bug Fixes

* **deps:** update dependency @stencila/encoda to v0.98.0 ([db253d0](https://github.com/stencila/hub/commit/db253d0bf3f7963b75d9a82cefa174a61884685c))
* **deps:** update dependency @stencila/executa to v1.13.0 ([8703522](https://github.com/stencila/hub/commit/8703522e75d47764f6ad32e4220f7be678e88430))
* **deps:** update dependency sentry-sdk to v0.16.4 ([fb16fae](https://github.com/stencila/hub/commit/fb16fae4c9748edde7140b7c734744c424b7b838))

## [3.27.2](https://github.com/stencila/hub/compare/v3.27.1...v3.27.2) (2020-08-14)


### Bug Fixes

* **Jobs:** Remove zone filters on queues ([cab70f9](https://github.com/stencila/hub/commit/cab70f98fca949c14c56990c4f3bf339cf45f720))

## [3.27.1](https://github.com/stencila/hub/compare/v3.27.0...v3.27.1) (2020-08-13)


### Bug Fixes

* **Account content:** Pin Thema, add Sentry to index.html ([ca7176b](https://github.com/stencila/hub/commit/ca7176b88af144c516e64fafcf1e6e1775369bd6))
* **Manager:** Allow HTTP session cookie during dev ([a5891be](https://github.com/stencila/hub/commit/a5891be909c0427361f75d888ce1faeec249f7b0))

# [3.27.0](https://github.com/stencila/hub/compare/v3.26.2...v3.27.0) (2020-08-13)


### Bug Fixes

* **UI:** Misc UI refinements ([7ef62a7](https://github.com/stencila/hub/commit/7ef62a768ebfee7f5ab3dc1cbba77aaebdf89cbf))


### Features

* **Projects:** Trim project descriptions with "read more" toggle ([7c39234](https://github.com/stencila/hub/commit/7c392345f5031e95ebc399ac767f78de708a7e62))

## [3.26.2](https://github.com/stencila/hub/compare/v3.26.1...v3.26.2) (2020-08-13)


### Bug Fixes

* **Account content:** Do not use slice for setting header ([eb733f6](https://github.com/stencila/hub/commit/eb733f687282af962cfd662eee40b9ec67931a07))

## [3.26.1](https://github.com/stencila/hub/compare/v3.26.0...v3.26.1) (2020-08-13)


### Bug Fixes

* **Worker:** Remove queues option in Dockerfile ([5bfdd59](https://github.com/stencila/hub/commit/5bfdd5999ba9be3b6db1df3f7ed916cb3f8e64f4))

# [3.26.0](https://github.com/stencila/hub/compare/v3.25.10...v3.26.0) (2020-08-12)


### Features

* **Worker:** Allow queues to be configured as an environment variable ([e2e99f0](https://github.com/stencila/hub/commit/e2e99f0d1dc542d8be7659be22cd969fcdb7450a))

## [3.25.10](https://github.com/stencila/hub/compare/v3.25.9...v3.25.10) (2020-08-12)


### Bug Fixes

* **Kubernetes session:** Check for container statuses ([506b8fc](https://github.com/stencila/hub/commit/506b8fc57c424540fb2908a9da75c9d7a234a639))

## [3.25.9](https://github.com/stencila/hub/compare/v3.25.8...v3.25.9) (2020-08-12)


### Bug Fixes

* **Kubernetes session:** Keep track of readiness probe ([aed5069](https://github.com/stencila/hub/commit/aed5069c1bd5dec2406e4dad981b9693242f3418))

## [3.25.8](https://github.com/stencila/hub/compare/v3.25.7...v3.25.8) (2020-08-12)


### Bug Fixes

* **Nginx:** Increase job connection timeouts ([855a11a](https://github.com/stencila/hub/commit/855a11ad242e8cc93e5cff99207cf81de1cb9277))
* **Worker:** Fix labels and alter some timeout defaults ([edea9b2](https://github.com/stencila/hub/commit/edea9b21cb3024fa247a560c3596e63c191060dd))
* **Worker:** Use executa-midi as default image ([aca32b7](https://github.com/stencila/hub/commit/aca32b7438fd6113833b50b61dc68fdc0e84eb56))

## [3.25.7](https://github.com/stencila/hub/compare/v3.25.6...v3.25.7) (2020-08-11)


### Bug Fixes

* **Jobs:** Increase throlling rates for API requests to GET project jobs ([6a76731](https://github.com/stencila/hub/commit/6a76731fd964cee081ce8ff90b4506aae1b40638))
* **Jobs:** Tweaks to status message ([d918009](https://github.com/stencila/hub/commit/d9180097b74e893840433455296a044c9bdb6601))
* **Kubernetes session:** Add a startup probe ([04cb9e0](https://github.com/stencila/hub/commit/04cb9e06e15b09c56264f413d0e4509f0ae454e6))
* **Manager:** Further updates to session cookie sessions ([52713b6](https://github.com/stencila/hub/commit/52713b6842ff331acd5c4025607608303502fc88))
* **Users:** Do not expire the auth_provider cookie ([9301848](https://github.com/stencila/hub/commit/93018482b918c78f009e2194c70d82345639bb64))

## [3.25.6](https://github.com/stencila/hub/compare/v3.25.5...v3.25.6) (2020-08-11)


### Bug Fixes

* **Jobs:** Improve session status messages. ([68fff44](https://github.com/stencila/hub/commit/68fff44f60253c6bd9877f18bb4e1559138a0643)), closes [#603](https://github.com/stencila/hub/issues/603)
* **Manager:** Allow credentials in cross-origin requests ([82af7d4](https://github.com/stencila/hub/commit/82af7d4341c0ee2fd50ba5a4f4f4f4b577155ff5))
* **Manager:** Allow session cookie from other site ([a7e9187](https://github.com/stencila/hub/commit/a7e9187941e14f759cc4f3c165b15f72c36177e4))

## [3.25.5](https://github.com/stencila/hub/compare/v3.25.4...v3.25.5) (2020-08-10)


### Bug Fixes

* **Worker:** Disable prefetching jobs ([a59b1ba](https://github.com/stencila/hub/commit/a59b1bac0162c39e46249363562cd491e2f30485))

## [3.25.4](https://github.com/stencila/hub/compare/v3.25.3...v3.25.4) (2020-08-10)


### Bug Fixes

* **Kubernetes session:** Correct when no snapshot path; make arg name consistent ([5431051](https://github.com/stencila/hub/commit/5431051bf4336cb4a774bb22adc19143f5125d4f))

## [3.25.3](https://github.com/stencila/hub/compare/v3.25.2...v3.25.3) (2020-08-10)


### Bug Fixes

* **Account subdomains:** Correct config of CORS whitelist ([ec812cf](https://github.com/stencila/hub/commit/ec812cfcf43f9d18b6ec317d4cbb323a5a6799e9))

## [3.25.2](https://github.com/stencila/hub/compare/v3.25.1...v3.25.2) (2020-08-10)


### Bug Fixes

* **Kubernetes session:** Clean up completed sessions ([193114d](https://github.com/stencila/hub/commit/193114d9e0bd16848ab89ccfb6d01af0b971fd11))
* **Kubernetes session:** Handle case where snapshot dir is empty ([248cf7e](https://github.com/stencila/hub/commit/248cf7e4a9655ee57dd5ae3e920dd12706eabf7c))
* **Kubernetes session:** Use snapshot_dir, which is the name provided by manager ([da444d8](https://github.com/stencila/hub/commit/da444d8147a8e23cf5387288f2b05c4eff13af15))

## [3.25.1](https://github.com/stencila/hub/compare/v3.25.0...v3.25.1) (2020-08-10)


### Bug Fixes

* **Manager:** Allow requests from account subdomains ([0e4dbbc](https://github.com/stencila/hub/commit/0e4dbbc582852739d156adaa3f3e31f70d2eda5e))
* **Manager:** Do not retrict sessions to staff ([9692787](https://github.com/stencila/hub/commit/9692787a4d1d57f85b6988100d70c9c4c740d822))

# [3.25.0](https://github.com/stencila/hub/compare/v3.24.1...v3.25.0) (2020-08-09)


### Bug Fixes

* **Account content:** Do not include port in primary domain url ([785e3e2](https://github.com/stencila/hub/commit/785e3e231e5ea35ee991aa116954572b0462b77f))


### Features

* **Kubernetes sessions:** Mount snapshot directory into session ([3859672](https://github.com/stencila/hub/commit/3859672f34c31326de4ef9e748d616cb0c8f8b37)), closes [#419](https://github.com/stencila/hub/issues/419)
* **Worker:** Make it easier to create a new session container ([c49f41d](https://github.com/stencila/hub/commit/c49f41d99aa51a2de910c03b4b4f3a8690f62853))

## [3.24.1](https://github.com/stencila/hub/compare/v3.24.0...v3.24.1) (2020-08-09)


### Bug Fixes

* **Manager:** Allow media, uplads, working etc roots to be configed separately ([0f3ee37](https://github.com/stencila/hub/commit/0f3ee3757d1eb2caf35a5d6e61176e08baa99e5d))
* **Snapshots:** Remove pin/unpin butoon ([b4eac78](https://github.com/stencila/hub/commit/b4eac7884f2860a7908ca632a8fd5926618f04c2))

# [3.24.0](https://github.com/stencila/hub/compare/v3.23.1...v3.24.0) (2020-08-08)


### Bug Fixes

* **Account cotent:** Render error page if file not in working ([9517be6](https://github.com/stencila/hub/commit/9517be6cf6e7f0b4b59a2d29c541c66e4eefcb25))


### Features

* **Account content:** Add file path to 404 page ([2be7724](https://github.com/stencila/hub/commit/2be7724634b3b1f1799f93627d0251f22f686e21))
* **Manager:** Preview contents of project files and live serving. ([0cb9697](https://github.com/stencila/hub/commit/0cb9697c7f65236db2a8e10d4d126a05a50194c5)), closes [#601](https://github.com/stencila/hub/issues/601) [#607](https://github.com/stencila/hub/issues/607)

## [3.23.1](https://github.com/stencila/hub/compare/v3.23.0...v3.23.1) (2020-08-08)


### Bug Fixes

* **Account content:** Fix handling of host CSP headers ([e5ac671](https://github.com/stencila/hub/commit/e5ac671738eaa0397e048f1ffaf44b7b707c0c04))

# [3.23.0](https://github.com/stencila/hub/compare/v3.22.4...v3.23.0) (2020-08-07)


### Bug Fixes

* **Account content:** Add stenci.la as CSP host ([da8b144](https://github.com/stencila/hub/commit/da8b144775d099d8912a4eb40a95390ac2e61432))


### Features

* **Account quotas:** Add quota for file downloads ([49065a7](https://github.com/stencila/hub/commit/49065a7342e2933a25ac6aa34923b74ecc3d15ba))

## [3.22.4](https://github.com/stencila/hub/compare/v3.22.3...v3.22.4) (2020-08-07)


### Bug Fixes

* **deps:** update dependency django-extensions to v3.0.4 ([94b38d7](https://github.com/stencila/hub/commit/94b38d79f9add74c2a90c5bea241acb2c96596ef))
* **deps:** update dependency djangorestframework to v3.11.1 ([0438c7f](https://github.com/stencila/hub/commit/0438c7fdee0a7d2a817c7900870b3a8053cfde64))
* **deps:** update dependency pygithub to v1.52 ([3f8a316](https://github.com/stencila/hub/commit/3f8a316f3dcf98332a3bcc40ec9dc2eb2cc132bc))
* **deps:** update dependency sentry-sdk to v0.16.3 ([4b3ceb2](https://github.com/stencila/hub/commit/4b3ceb2cdd700d6cacb5a6ad6ba314ce7ab6f039))
* **deps:** update dependency whitenoise to v5.2.0 ([cff338d](https://github.com/stencila/hub/commit/cff338daa6d3014d3f0158d9dae2abf4ae14da69))

## [3.22.3](https://github.com/stencila/hub/compare/v3.22.2...v3.22.3) (2020-08-07)


### Bug Fixes

* **Account content:** Put project key into path ([edcdce5](https://github.com/stencila/hub/commit/edcdce527c38301e6c6cf31ca1343b3e039b29ad))
* **deps:** update dependency @stencila/encoda to v0.97.3 ([d0306b9](https://github.com/stencila/hub/commit/d0306b91ae10a5d08eec462f91c4c6c1a57d90f3))
* **deps:** update dependency @stencila/executa to v1.12.0 ([18d4962](https://github.com/stencila/hub/commit/18d4962d93c5f414c25e8314ac0b69e695112a2e))
* **deps:** update dependency @stencila/thema to v2.15.3 ([6cee52b](https://github.com/stencila/hub/commit/6cee52b55e16a612dd84d7c263c3beddb89e6dd5))
* **deps:** update dependency amqp to v2.6.1 ([a6cbe20](https://github.com/stencila/hub/commit/a6cbe20ee3a36f068c074c5cda1b4b443378098c))
* **deps:** update dependency celery to v4.4.7 ([bfc2b3d](https://github.com/stencila/hub/commit/bfc2b3d351f1602260c2c843e1e48a35366b5026))
* **deps:** update dependency django to v3.1 ([cd4aa4f](https://github.com/stencila/hub/commit/cd4aa4f955513b132bea79709176adb4f906f1ed))
* **Router:** Serve robots.txt etc ([e8cfa36](https://github.com/stencila/hub/commit/e8cfa36e4193e8ca0271fe068c4bd49fe0572f85))

## [3.22.2](https://github.com/stencila/hub/compare/v3.22.1...v3.22.2) (2020-08-07)


### Bug Fixes

* **Account content:** Redirection to primary domain ([404dd91](https://github.com/stencila/hub/commit/404dd91fd4ffc00e9acf04cf2bdf7324a34da4e1))
* **Router:** Proxy external addresses using resolver ([72ea49e](https://github.com/stencila/hub/commit/72ea49ef3d2e64db1c58952c75a572854023d969))

## [3.22.1](https://github.com/stencila/hub/compare/v3.22.0...v3.22.1) (2020-08-07)


### Bug Fixes

* **Account content:** Append slash if necessary; always use local 404 page ([62e6a53](https://github.com/stencila/hub/commit/62e6a539ac554731c448cd502e537ae7c71b8330))
* **Account content:** Use the absolute URL of the primary domain for links ([b4969a9](https://github.com/stencila/hub/commit/b4969a91b19a970778ae682621d7532307ef9cf5))

# [3.22.0](https://github.com/stencila/hub/compare/v3.21.1...v3.22.0) (2020-08-06)


### Bug Fixes

* **Snapshots:** Return absolute URL when using FileSystemStorage ([1d10b12](https://github.com/stencila/hub/commit/1d10b12a157354f494b526e51d8a838d4646d17b))


### Features

* **Manager:** Add settings for serving project content ([bda8faf](https://github.com/stencila/hub/commit/bda8faf6fd1f26a099fb70e63cbda9dc8df0b510))
* **Manager:** Serve account content ([c62a4b9](https://github.com/stencila/hub/commit/c62a4b954644026f050dd3f3d4f8c6d46336ad6b))
* **Router:** Reverse proxy account domains ([14e7d92](https://github.com/stencila/hub/commit/14e7d920707ed98565a4f0a41c5d01cf0485b9b0))

## [3.21.1](https://github.com/stencila/hub/compare/v3.21.0...v3.21.1) (2020-08-06)


### Bug Fixes

* **Manager:** Serve Prometheus metrics ([e3f5c0e](https://github.com/stencila/hub/commit/e3f5c0e25268f359635c397ec16a08801d3697f4))

# [3.21.0](https://github.com/stencila/hub/compare/v3.20.0...v3.21.0) (2020-08-06)


### Bug Fixes

* **Manager:** User user_id to reduce db queries ([39201cc](https://github.com/stencila/hub/commit/39201ccf913f7cece8feb452bfd4348d648c5d6b))
* **Users:** Clear user session data on log in and log out ([11aaf04](https://github.com/stencila/hub/commit/11aaf0422e3a62e73bf9d8f51d06280d05b0d77a))


### Features

* **Manager sources:** Allow sources to be reffered to using address ([1245e59](https://github.com/stencila/hub/commit/1245e592e75fa29a462452dc48be33ad9b249935))

# [3.20.0](https://github.com/stencila/hub/compare/v3.19.3...v3.20.0) (2020-08-04)


### Bug Fixes

* **Snapshots:** Inject Executable Toolbar into Thema article context ([3e9e94e](https://github.com/stencila/hub/commit/3e9e94eea7cea46e87af4a7fc509a3756a3cfbff))


### Features

* **Jobs:** Return an existing, running, matching session for a user ([5a0eecc](https://github.com/stencila/hub/commit/5a0eecc4c400dfb550b5510bb43b97da2306c61b))
* **K8s session:** Add default timeout and timelimit ([cfa1a79](https://github.com/stencila/hub/commit/cfa1a794b210cd094bbec3406ec032a8f4ef3523))

## [3.19.3](https://github.com/stencila/hub/compare/v3.19.2...v3.19.3) (2020-08-03)


### Bug Fixes

* **Jobs:** Do not alter the protocol for the redirected URL ([3b73655](https://github.com/stencila/hub/commit/3b7365590d07603b177c9ac2a44564e7e4760602))
* **Jobs:** Nginx really doesn't like ws:// is header URL ([a7f0a81](https://github.com/stencila/hub/commit/a7f0a814942c8d0a4ae2c420b81c182539010e7f))
* **Jobs:** Return a Websocket URL is needs be ([a4498d3](https://github.com/stencila/hub/commit/a4498d35e292d14ab1e410ab3af8028b95ed0c1a))
* **Router:** Add Connection header ([e192995](https://github.com/stencila/hub/commit/e192995f79f8646224dbee8a34f4b9fd8eea8430))

## [3.19.2](https://github.com/stencila/hub/compare/v3.19.1...v3.19.2) (2020-08-03)


### Bug Fixes

* **Kubernetes session:** Terminate on exception during streaming ([eed6aed](https://github.com/stencila/hub/commit/eed6aed54950314b3490542ea1a8fa3171373bac))

## [3.19.1](https://github.com/stencila/hub/compare/v3.19.0...v3.19.1) (2020-08-03)


### Bug Fixes

* **Kubernetes session:** Improve logging and termination ([b11d1d7](https://github.com/stencila/hub/commit/b11d1d7d2a11f3758c736723343ba2670d7fa676))
* **Manager:** FIx type and send extra dict ([0f2bcf1](https://github.com/stencila/hub/commit/0f2bcf1d82c7a436c926d84020d1e88f34f88323))
* **Worker:** Improve switching between session types ([3706700](https://github.com/stencila/hub/commit/3706700e4725d23752269c2e833adfa736d0ce96))

# [3.19.0](https://github.com/stencila/hub/compare/v3.18.1...v3.19.0) (2020-08-03)


### Bug Fixes

* **Jobs:** Show job error message in detailed view ([45956ff](https://github.com/stencila/hub/commit/45956ffd3c22ddbaa61bced96078db03fd39efa9))
* **Jobs:** When cancelling a compound job cancel subjobs ([bb019bd](https://github.com/stencila/hub/commit/bb019bd6a7a9eaa6b76fba11d0056318dc5021ce))
* **Kubernetes worker:** More checks of Minikube ([2969cdf](https://github.com/stencila/hub/commit/2969cdf3c608d3087aaa6aa532424001f55c7bd1))


### Features

* **Worker:** Add more detail to job logs ([37206bc](https://github.com/stencila/hub/commit/37206bce517c024c1e3ff96814360583496d58ae))

## [3.18.1](https://github.com/stencila/hub/compare/v3.18.0...v3.18.1) (2020-08-03)


### Bug Fixes

* **Kubernetes session:** Need to export api_instance ([b4db8c0](https://github.com/stencila/hub/commit/b4db8c06d629c26e80b53de0d79307d5fb8ff8e9))
* **Kubernetes sessions:** Fix in cluster config ([3f4c39f](https://github.com/stencila/hub/commit/3f4c39f04284102b3446dfd81848f859f8d4fb56))

# [3.18.0](https://github.com/stencila/hub/compare/v3.17.0...v3.18.0) (2020-08-02)


### Bug Fixes

* **Jobs:** Add job key to task arguments ([03e22d7](https://github.com/stencila/hub/commit/03e22d746fbd7ab32e37a2f854098c008f03b8e8))
* **Jobs:** Kubernetes session ([6624831](https://github.com/stencila/hub/commit/6624831634b74dfca58cc277365b054a33c74f56))
* **Kubernetes session:** Avoid error on systems where K8s is not available ([929cf5e](https://github.com/stencila/hub/commit/929cf5e797635f3b63fde18c4eb8f9ceda9196f4))
* **Kubernetes session:** Use a custom namespace ([ae98376](https://github.com/stencila/hub/commit/ae983766ef5b447f1f3028fe5d797d26d24966ad))


### Features

* **Kubernetes session:** Send key as param to job ([99941a3](https://github.com/stencila/hub/commit/99941a3361b3680c4176f19903810f491fa6fb08))
* **Manage jobs:** Add cancel button and minor template tidyups ([d6c103b](https://github.com/stencila/hub/commit/d6c103b99ea847aa1edab922977ce31f1ee59a56))
* **Manage jobs:** Add cancel button and minor template tidyups ([a9e9665](https://github.com/stencila/hub/commit/a9e96655a1a7231402684c511744ce6e75ee391d))
* **Session jobs:** Switch session type based on environ ([13b3ca3](https://github.com/stencila/hub/commit/13b3ca3eb71db987ae4623cd71df60738eae17b5))

# [3.17.0](https://github.com/stencila/hub/compare/v3.16.1...v3.17.0) (2020-07-31)


### Features

* **Manager jobs:** Allow cancellation of jobs from admin interface ([884a2ca](https://github.com/stencila/hub/commit/884a2cad427340652f777a9a31b6485809a2f217))

## [3.16.1](https://github.com/stencila/hub/compare/v3.16.0...v3.16.1) (2020-07-31)


### Bug Fixes

* **Snapshots:** Don't inject CSS variables as they're set by Designa ([4d52fb8](https://github.com/stencila/hub/commit/4d52fb8c6dc5ffd5350d8c54c69210b765988c6b))

# [3.16.0](https://github.com/stencila/hub/compare/v3.15.1...v3.16.0) (2020-07-31)


### Bug Fixes

* **Manager jobs:** Check that callback object exists ([c6223f3](https://github.com/stencila/hub/commit/c6223f393172d358f39a2ec375c563bebf97eed0)), closes [#596](https://github.com/stencila/hub/issues/596)


### Features

* **Cache:** Add cache service ([73d1aa8](https://github.com/stencila/hub/commit/73d1aa80d22176dbe5cc155a345493f14cdd1da9))
* **Manager:** Allow use of cache service as result backend ([ddb8141](https://github.com/stencila/hub/commit/ddb8141b924fb0edbaf176c6b26066535146ce4b))
* **Worker:** Allow use of cache service as result backend ([f1435c2](https://github.com/stencila/hub/commit/f1435c2a9bd05b95391c505046ab62f0b825db09))

## [3.15.1](https://github.com/stencila/hub/compare/v3.15.0...v3.15.1) (2020-07-31)


### Bug Fixes

* **Manager:** Use extra dict instead on interpolation ([eb9e8db](https://github.com/stencila/hub/commit/eb9e8db61cafc9019ff5e909490cc6713314e384))

# [3.15.0](https://github.com/stencila/hub/compare/v3.14.0...v3.15.0) (2020-07-31)


### Bug Fixes

* **Jobs:** Use get (instead of wait) and log (instead of raising) ([8f36030](https://github.com/stencila/hub/commit/8f3603042a72002a6dd87580155443e602976405))
* **Worker:** Set concurrency and prefetch in image ([19b262e](https://github.com/stencila/hub/commit/19b262e3f8ed4d606cc06f57f33d06031fd61956))


### Features

* **File formats:** Specify which formats can be converted to ([048a619](https://github.com/stencila/hub/commit/048a6192c9c51ac7632b0619ee77072f2b4e02ff))
* **Jobs:** Show job log and result ([60b7749](https://github.com/stencila/hub/commit/60b7749a4e3128816737a682201d27d65f7fe760))

# [3.14.0](https://github.com/stencila/hub/compare/v3.13.0...v3.14.0) (2020-07-31)


### Bug Fixes

* **Acount pages:** Show projects that a user is a member of ([31ae01c](https://github.com/stencila/hub/commit/31ae01c0fcdcf290c7b315cde618851b624e1ef6))
* **deps:** pin dependencies ([df95c00](https://github.com/stencila/hub/commit/df95c0098d004df2420d02382a674685b9e9a7c1))
* **deps:** update dependency @stencila/thema to v2.14.0 ([3c66683](https://github.com/stencila/hub/commit/3c66683a50056f371066f536097f08dcf5aa8bb4))
* **deps:** update dependency google-cloud-storage to v1.30.0 ([058d4c8](https://github.com/stencila/hub/commit/058d4c81ca4963c570e832ec2e34d4b613e34a1c))
* **Jobs:** Only provide a single connection URL ([11da982](https://github.com/stencila/hub/commit/11da982932f69ad94732364be6e73e8aae10acf0))
* **Jobs:** Use queue_id to reduce querys ([83db585](https://github.com/stencila/hub/commit/83db5853dda17e55fda509d758dacf8eca0d76cc))
* **Manager:** Improve updating of job status ([9a0b0b4](https://github.com/stencila/hub/commit/9a0b0b443d34d5a510b6cb170e6f123b84fb9291))
* **Overseer:** Add timezone to times, ensure status field whenever updating a job ([93c21c4](https://github.com/stencila/hub/commit/93c21c4ea26f854d6c60f653c75b82971a70619f))
* **Overseer:** Handle taks logging events ([e84ab50](https://github.com/stencila/hub/commit/e84ab50026fc9cdb9be674c372e3104076e90424))
* **Project role:** Use project role when account role is manager ([8a80def](https://github.com/stencila/hub/commit/8a80defa99e7c81de48be44ea6c771594c693771))
* **Projects:** Fix getting of main file ([5dd0428](https://github.com/stencila/hub/commit/5dd04283b56fa089d9ec7151c5e67e789d09e410))
* **Snapshots:** Allow for CSRF except API views ([bd8296f](https://github.com/stencila/hub/commit/bd8296fa081a36b556ab5e5e639bef6682eeebaa))
* **Snapshots:** Fix var name and add temporary script replacement ([fb28470](https://github.com/stencila/hub/commit/fb284702947511ddc0affbbd4a4668264cb59806))
* **Snapshots:** Integrate snapshot preview into details page and tidyup templates ([48f7205](https://github.com/stencila/hub/commit/48f7205f497730028761d94ff4994fb081df4336))
* **Subproces session:** Determine port in do method ([296e065](https://github.com/stencila/hub/commit/296e06590d81dabd0e0b15beada16f18a36e9f7c))
* **Subprocesss job:** Only send remainder if failed ([80ae534](https://github.com/stencila/hub/commit/80ae5349a6c3c97ec245357ec2e1c162d742bc43))
* **Themes:** Update Thema version ([004e6a6](https://github.com/stencila/hub/commit/004e6a6b3aa84ad1e3d0c8a62988b3abed551f0e))
* **Worker:** Add Executa as dep and refer to local node_modules/.bin ([918fe48](https://github.com/stencila/hub/commit/918fe483e2710d0cc37471dde6676956251a7a0c))
* **Worker:** Aggregate log lines that are not JSON ([3ddd8bf](https://github.com/stencila/hub/commit/3ddd8bf6ef340356c86f982d3b868e1d7babf212))
* **Worker:** Emit all Job log entries to the Python logger ([9205c47](https://github.com/stencila/hub/commit/9205c475eeab62ca2f09561e23ad5bb0cef23ed1))
* **Worker:** Make SubprocessSession extend SubprocessJob ([857c532](https://github.com/stencila/hub/commit/857c532f494a311b3e3d9d6a8622a769379308a2))
* **Worker:** Send custom log event with task id ([7f2b96a](https://github.com/stencila/hub/commit/7f2b96a69fabf5fd422306890f1244e985a75c67))


### Features

* **Job:** Add job key and use in URLs ([0482620](https://github.com/stencila/hub/commit/0482620dce9355520d81ec05f022cff0688a1214))
* **Jobs:** Add filters to admin ([65aa197](https://github.com/stencila/hub/commit/65aa1974a0b7bc0da9ced7f24542001c374c2303))
* **Jobs:** Add status message field ([ed07689](https://github.com/stencila/hub/commit/ed07689ff4a24d55f48b806bd3345272bddfb165))
* **Manager jobs:** Allow restriction of job methods by staff status ([b3c9db5](https://github.com/stencila/hub/commit/b3c9db528cfc577fa7a582f5409c2738f2f97e21))
* **Snapshots:** Create session for snapshot and inject toolbar into index.html ([3592fe5](https://github.com/stencila/hub/commit/3592fe56832f923f0d5bd267fe221700aa872651))

# [3.13.0](https://github.com/stencila/hub/compare/v3.12.0...v3.13.0) (2020-07-28)


### Bug Fixes

* **Files:** Add more mime type icons ([c2fb0c8](https://github.com/stencila/hub/commit/c2fb0c82737a5c064e6d0d4f34547a335ad77a94))
* **Files:** List all upstreams and downstreams ([8e8af7e](https://github.com/stencila/hub/commit/8e8af7e9421ac083263434df5321758b44774dd7))
* **Jobs:** Save before updating parent ([e4c1be6](https://github.com/stencila/hub/commit/e4c1be6b986d6523dc5de7cacad1f2c6eabf315d))
* **Sources:** Add icon for upload sources ([21ef3cf](https://github.com/stencila/hub/commit/21ef3cf1c2120583405882ca493b5ef944ed73fc))


### Features

* **File formats:** Add types and enums for file formats ([1c3c439](https://github.com/stencila/hub/commit/1c3c43996fdf961e863debe419c044dc72a0a205))
* **Files:** Add views to retrieve, convert and destroy files ([9037745](https://github.com/stencila/hub/commit/9037745104e2796df156786f97cd2b2335542842))
* **Jobs:** Add progress bar partial ([eda5efe](https://github.com/stencila/hub/commit/eda5efea14cd7c110d00761a2aef649032d894b7))
* **Pipelines:** Hide pipelines behind a feature flag ([da1379d](https://github.com/stencila/hub/commit/da1379dcd269efadb6d6ffc624d3804970b99060))
* **Sources:** Add fields for uploads; improve retrieve view ([d40e5ad](https://github.com/stencila/hub/commit/d40e5ad841425b85c9916a923bc8fe7473d9ac58))

# [3.12.0](https://github.com/stencila/hub/compare/v3.11.0...v3.12.0) (2020-07-28)


### Features

* **Email:** Add template for confirming additional email addresses ([4d1470f](https://github.com/stencila/hub/commit/4d1470f5142e12d9550defc7e8bf83dba9e1950b)), closes [#582](https://github.com/stencila/hub/issues/582)

# [3.11.0](https://github.com/stencila/hub/compare/v3.10.3...v3.11.0) (2020-07-27)


### Features

* **User search:** Add images to user search results ([e51463e](https://github.com/stencila/hub/commit/e51463e26ddbf1b07ab11cdcc022e72890cb7323)), closes [#280](https://github.com/stencila/hub/issues/280)
* **User search:** Add public email and location to search results ([979885b](https://github.com/stencila/hub/commit/979885b4778f0dc40db9f0c7566734ad6eee9c8c))

## [3.10.3](https://github.com/stencila/hub/compare/v3.10.2...v3.10.3) (2020-07-24)


### Bug Fixes

* **deps:** update dependency @stencila/thema to v2.13.1 ([1d5b918](https://github.com/stencila/hub/commit/1d5b918cd6ddab2ca32a31faabab0d42e8c18044))
* **deps:** update dependency django-imagefield to v0.12.0 ([4c65706](https://github.com/stencila/hub/commit/4c65706c03beb931b14916fe285bc0c468e22b32))
* **deps:** update dependency sentry-sdk to v0.16.2 ([9157c18](https://github.com/stencila/hub/commit/9157c18b8d34b2cadb4aa726a858f753dc8e78e9))

## [3.10.2](https://github.com/stencila/hub/compare/v3.10.1...v3.10.2) (2020-07-24)


### Bug Fixes

* **Template context:** Add USERFLOW_KEY ([fafc732](https://github.com/stencila/hub/commit/fafc73279e9d432155176e8c27b1ced3a1cd28fa))

## [3.10.1](https://github.com/stencila/hub/compare/v3.10.0...v3.10.1) (2020-07-24)


### Bug Fixes

* **Email confirmation:** Improve page ([9c96e25](https://github.com/stencila/hub/commit/9c96e25d254eeb121d7b337cb5e4bb49e6c53988))
* **Emails:** Fix templating, consistent subject lines ([19e79e7](https://github.com/stencila/hub/commit/19e79e706a75a61d2a6656c720a80e26c27b2935))
* **Password reset:** Small fixes to templates ([5a5d94c](https://github.com/stencila/hub/commit/5a5d94c0c6f79696bf8011ea983cb44eede7a1d1))

# [3.10.0](https://github.com/stencila/hub/compare/v3.9.2...v3.10.0) (2020-07-23)


### Features

* **Manager:** Use email templates ([db75622](https://github.com/stencila/hub/commit/db75622f80fc01910aac81ed9ee587d5d289cd29))

## [3.9.2](https://github.com/stencila/hub/compare/v3.9.1...v3.9.2) (2020-07-23)


### Bug Fixes

* **Snapshots:** Allow anon access to snapshot archives ([2216001](https://github.com/stencila/hub/commit/22160014b4b36b568055590cda8a7b48549e0a3c))

## [3.9.1](https://github.com/stencila/hub/compare/v3.9.0...v3.9.1) (2020-07-23)


### Bug Fixes

* **Jobs:** Only update the job from the partial_update view ([96e1e38](https://github.com/stencila/hub/commit/96e1e38965124cf604e76a57311c4f6477613cef))
* **Snapshots:** Merge snapshots files and serve views ([e4c2dd3](https://github.com/stencila/hub/commit/e4c2dd35f8d8a3f65a850c138567d84379dcd44e))

# [3.9.0](https://github.com/stencila/hub/compare/v3.8.1...v3.9.0) (2020-07-23)


### Bug Fixes

* **Snapshots:** Add clean job; use BigAuto for job id ([7ebb1d1](https://github.com/stencila/hub/commit/7ebb1d1c18eaf131b0b675f05a93f056bac86737))
* **Snapshots:** Add path and zip_name fields ([8f2f8aa](https://github.com/stencila/hub/commit/8f2f8aa10c725b0d1d9f71ab89edf0d4672b4f68))
* **Snapshots:** Do not create an index.html if there is not main file ([7b4b50a](https://github.com/stencila/hub/commit/7b4b50ab3550823e94ea52b603d776d5e59564be))
* **User profiles:** Allow setting of first and last names; sync to display name. ([cbba699](https://github.com/stencila/hub/commit/cbba6991295331f3a04f2606e2c941d8e8f30381))


### Features

* **JS:** Add User Flow js for creating product tours ([501e62f](https://github.com/stencila/hub/commit/501e62f189fa052495b03c0c9a46092e6479e948))

## [3.8.1](https://github.com/stencila/hub/compare/v3.8.0...v3.8.1) (2020-07-22)


### Bug Fixes

* **Worker:** Make entrypoint executable in container too ([3529488](https://github.com/stencila/hub/commit/3529488b49ca1b8ddd7c88e2d4b67002366a58c8))
* **Worker:** Specify bash shebang ([b57afbc](https://github.com/stencila/hub/commit/b57afbc40e1273ce81f1375e10b1229c461d4b52))

# [3.8.0](https://github.com/stencila/hub/compare/v3.7.1...v3.8.0) (2020-07-22)


### Bug Fixes

* **Files:** Cache the project attribute and pass to the template context. ([c19e1f8](https://github.com/stencila/hub/commit/c19e1f8a7be53ca05515b23207737c385f16133a))
* **FIles:** Make modified time timezone aware ([b5d662b](https://github.com/stencila/hub/commit/b5d662b2f954f6e1c3b71e8b975ded680fed75ae))
* **Worker:** Add entrypoint script to mount bucket ([5adb355](https://github.com/stencila/hub/commit/5adb3554466a5c827dcfa6f15de3b15e8acf5582))


### Features

* **Snapshots:** Add a separate snapshot serve API endpoint ([4818ade](https://github.com/stencila/hub/commit/4818adebc2d9ff98c5c678064b3e4be356682a0f))
* **Snapshots:** Make snapshot id a UUID and add number within project ([ef5e76e](https://github.com/stencila/hub/commit/ef5e76ed9f4cbd416bd16a3615135dce3253fa74))
* **Snapshots:** Reverse proxy content from buckets ([5e27742](https://github.com/stencila/hub/commit/5e277425a141287107fd273dc8e6b0b7dc3953db))
* **Worker:** Add gcsfuse to allow mounting of buckets for storage ([e31636c](https://github.com/stencila/hub/commit/e31636ccb9e87942e47b5a6a236dba68800ce39a))

## [3.7.1](https://github.com/stencila/hub/compare/v3.7.0...v3.7.1) (2020-07-21)


### Bug Fixes

* **Password Reset:** Style password reset form views ([1541b93](https://github.com/stencila/hub/commit/1541b9341477e6355fc7900b88fd99c8c3260756))
* **Passwrod reset:** Consistent titles and layout across views. ([dec7b7e](https://github.com/stencila/hub/commit/dec7b7ea6b5d711d7edd9495aa7c435ce1ced4cf))

# [3.7.0](https://github.com/stencila/hub/compare/v3.6.1...v3.7.0) (2020-07-21)


### Bug Fixes

* **Accounts:** Exclude temp org from list ([171eac9](https://github.com/stencila/hub/commit/171eac9a0af3696263198203324f323c6f3add95)), closes [#553](https://github.com/stencila/hub/issues/553)


### Features

* **Account tiers:** Allow plans to be designated inactive; add admin filtering by tier ([76a0b49](https://github.com/stencila/hub/commit/76a0b4934c6baa95c951b072e4c5a5566f6c778e))

## [3.6.1](https://github.com/stencila/hub/compare/v3.6.0...v3.6.1) (2020-07-20)


### Bug Fixes

* **Account images:** Update the session store for user account images ([8ebfc94](https://github.com/stencila/hub/commit/8ebfc94f984698cded6e42d2c8fab816427add06))
* **Accounts:** Make it clearer that account email only used in profile ([9a83cb3](https://github.com/stencila/hub/commit/9a83cb3a5cd8b567ff19a5fe47092d208c6d92a9))
* **Merge users:** When merging ensure only one primary email ([caea5f9](https://github.com/stencila/hub/commit/caea5f9c40c23c29508fdb875eecdb5721363269)), closes [#570](https://github.com/stencila/hub/issues/570)

# [3.6.0](https://github.com/stencila/hub/compare/v3.5.1...v3.6.0) (2020-07-20)


### Bug Fixes

* **Projects:** Alter to on_delete actions ([c7389fc](https://github.com/stencila/hub/commit/c7389fc43da13f8946201f85a03b8c1f6d3892d3))


### Features

* **Manager:** Add management command for merging users ([9f3e466](https://github.com/stencila/hub/commit/9f3e46623c355190268a5af1c77990f502bd6e5b))

## [3.5.1](https://github.com/stencila/hub/compare/v3.5.0...v3.5.1) (2020-07-19)


### Bug Fixes

* **Manager:** Enable Intercom for unauthenticated users ([f8d213c](https://github.com/stencila/hub/commit/f8d213c5e515fbf94cc9458af00513a46ebcd8c8))

# [3.5.0](https://github.com/stencila/hub/compare/v3.4.1...v3.5.0) (2020-07-19)


### Bug Fixes

* **deps:** update dependency @stencila/thema to v2.13.0 ([babcde8](https://github.com/stencila/hub/commit/babcde8b99976fcc5da7ddd75cf0b9ad9c6d4409))
* **deps:** update dependency django-extensions to v3.0.3 ([4246c0d](https://github.com/stencila/hub/commit/4246c0dd3cf741303688e649ccc253fc2beb4d9b))
* **deps:** update dependency google-api-python-client to v1.10.0 ([7c3b4a1](https://github.com/stencila/hub/commit/7c3b4a1b5cb72c130cf85fa0a79f00e8b2a9ce29))
* **deps:** update dependency sentry-sdk to v0.16.1 ([10629bc](https://github.com/stencila/hub/commit/10629bc460f3801b57db0f840c287d2d26b11e6e))


### Features

* **Manager admin:** Add filters and search for account related models ([45862f9](https://github.com/stencila/hub/commit/45862f9523689e79e9a2d049c1ed403fbde8e105))
* **Manager admin:** Customize admin interface ([c26e8d9](https://github.com/stencila/hub/commit/c26e8d9ab6bca9d08236360486dd0d1a6ca9cb58))

## [3.4.1](https://github.com/stencila/hub/compare/v3.4.0...v3.4.1) (2020-07-16)


### Bug Fixes

* **Manager:** Increase workers to 3 ([56c4d0d](https://github.com/stencila/hub/commit/56c4d0db4f367b22b34ed83992621399334bfc09))

# [3.4.0](https://github.com/stencila/hub/compare/v3.3.4...v3.4.0) (2020-07-16)


### Bug Fixes

* **Orgs:** Don't attach event handler if role dropdown doesn't exist ([3a6368a](https://github.com/stencila/hub/commit/3a6368a3d41df6eeabda61daaa5a729c466b7553)), closes [#560](https://github.com/stencila/hub/issues/560)


### Features

* **UI:** Add links to Help docs & open links in new tabs ([2999f20](https://github.com/stencila/hub/commit/2999f20a038d62969f6849abc41d5b3e08adf686))

## [3.3.4](https://github.com/stencila/hub/compare/v3.3.3...v3.3.4) (2020-07-15)


### Bug Fixes

* **JS:** Fix JS usage after splitting into multiple files ([f75a8b1](https://github.com/stencila/hub/commit/f75a8b16d1e74b234e7991d061e9a8462b93ebe0))

## [3.3.3](https://github.com/stencila/hub/compare/v3.3.2...v3.3.3) (2020-07-15)


### Bug Fixes

* **Account quotas:** Add limit to messages; avoid divide by zero ([56cc42e](https://github.com/stencila/hub/commit/56cc42e26212552d1f1fa5cfada2013ef4f2d615))
* **Broker:** Expose management API ([10ccd83](https://github.com/stencila/hub/commit/10ccd83e708938bc5367f602ca6a939dd373546d))
* **Projects:** Improve validation of create and update projects ([a3fe00f](https://github.com/stencila/hub/commit/a3fe00fb35343988cb2b9855daa7585bca651a69))
* **Router:** Capture as error, instead of info message ([0016227](https://github.com/stencila/hub/commit/0016227e7e2765a684d7c3952a74523f88c83c26))

## [3.3.2](https://github.com/stencila/hub/compare/v3.3.1...v3.3.2) (2020-07-14)


### Bug Fixes

* **a11y:** Add lable to role selector in Org search view ([4c483f6](https://github.com/stencila/hub/commit/4c483f6f4f42a67651efe79f2cfc20ed4dc39791))
* **a11y:** Address accessibility issues found by Axe ([5a78d83](https://github.com/stencila/hub/commit/5a78d8314bc104d975442b3c772066b621b792bc))
* **a11y:** Fix more accessibility issues ([a1939cf](https://github.com/stencila/hub/commit/a1939cf7463e024522396cf2ddf66b26549c2696))
* **JS:** Don't attach event-handlers if element doesn't exist ([41d297e](https://github.com/stencila/hub/commit/41d297ed4e6e36ce146a8ea9a5e2298098b3e3c9))
* **SEO:** Add description meta tag ([48c01e2](https://github.com/stencila/hub/commit/48c01e213330bc25e40759c305fb6d56bdc4ad7d))


### Performance Improvements

* **CSS:** Optimize generated CSS ([f667417](https://github.com/stencila/hub/commit/f6674172b67902dfaa1f19d98ba51445c773f0fa))
* **JS:** Split JS into internal and 3rd party files ([c51b204](https://github.com/stencila/hub/commit/c51b2047631b0d320123a9cf36eac5e672de78a6))
* **JS:** Update Posthog snippet to be non-blocking ([98bf742](https://github.com/stencila/hub/commit/98bf7420e268f48775b66008513f5d1318c311bb))
* **Manager:** Fix auth API test ([ab5ebbb](https://github.com/stencila/hub/commit/ab5ebbba962e7d9a7cce3a4b530147dbf44c5c33))

## [3.3.1](https://github.com/stencila/hub/compare/v3.3.0...v3.3.1) (2020-07-14)


### Bug Fixes

* **Manager:** Allow un-throttled anon access to status ([27a05da](https://github.com/stencila/hub/commit/27a05da62c1d7a1da5aa9dddec320780676362f2))

# [3.3.0](https://github.com/stencila/hub/compare/v3.2.2...v3.3.0) (2020-07-14)


### Bug Fixes

* **Messages:** Allow for permanant messages; safer JS strings ([ef9898b](https://github.com/stencila/hub/commit/ef9898b732c0f53566cb44887bbb447aaad61c9f))


### Features

* **Open:** Add /open page for creation of temporary projects; various other related improvements ([6034801](https://github.com/stencila/hub/commit/60348016f75ee750aa5a7a22f24189e37c6c6880))
* **Temporary projects:** Adds temporary projects and project claims ([006fb19](https://github.com/stencila/hub/commit/006fb1983431f5d77d2ef81ccd7fc8e3c05c0175))


### Performance Improvements

* **Manager:** Add API throttling ([e016dc2](https://github.com/stencila/hub/commit/e016dc2fa773616879153ce22be70e8d9805d51c))

## [3.2.2](https://github.com/stencila/hub/compare/v3.2.1...v3.2.2) (2020-07-14)


### Bug Fixes

* **Accounts:** Update name of quota ([01c889d](https://github.com/stencila/hub/commit/01c889db9f6d3f77bbf222fffa9e3092cb4832b3))
* **Projects:** Do not sets defaults ([754998f](https://github.com/stencila/hub/commit/754998ff93948510e2bd77e939a7e699ed7c8786))

## [3.2.1](https://github.com/stencila/hub/compare/v3.2.0...v3.2.1) (2020-07-13)


### Bug Fixes

* **Projects:** Default to public project ([7f07444](https://github.com/stencila/hub/commit/7f0744491e4308cf6be7a09d75256bfa2a33c125))

# [3.2.0](https://github.com/stencila/hub/compare/v3.1.3...v3.2.0) (2020-07-12)


### Bug Fixes

* **Manager:** Revert to name url for field ([60ced3f](https://github.com/stencila/hub/commit/60ced3f325b2327ed5131a0aae873ef5e60b22a4))
* **Manager:** Use a URL address to fetch uploaded files ([40ab80f](https://github.com/stencila/hub/commit/40ab80f4a2a11e01ae8b588b80972fb746c892d0))
* **Manager jobs:** Use seconds, rather than minutes ([1c3c424](https://github.com/stencila/hub/commit/1c3c424f880a75f990fcc3bdf563e6a1aef2d40d))
* **Manager sources:** Autofocus remove button ([adeed41](https://github.com/stencila/hub/commit/adeed41e97546a09e3891c0ad701f16c576e8007))


### Features

* **Worker:** Report job exceptions to Sentry ([3350255](https://github.com/stencila/hub/commit/3350255fb71d0dd1693a4e1602a0b5a4f0e49c5a))

## [3.1.3](https://github.com/stencila/hub/compare/v3.1.2...v3.1.3) (2020-07-11)


### Bug Fixes

* **Accounts:** Fix Plan Tier listing layout overflow ([c171d00](https://github.com/stencila/hub/commit/c171d003be4f50deb8bfd7d168737be32d28eb9d))
* **JS:** Reset spinner buttons if Form contains an error ([631ec3b](https://github.com/stencila/hub/commit/631ec3b272a85f9790a3fa130b8df0f72c1516e5))
* **Manager eLife source:** Correct reference to static image ([afb6242](https://github.com/stencila/hub/commit/afb62421346949cd4d53f8ac158b4fcf6c9e5c3e))
* **Manager middleware:** Add status codes ([e74900d](https://github.com/stencila/hub/commit/e74900da5f676e2cf01f36a8f7c75dc399a514f5))
* **Manager URL source:** Fix field name ([90aaf5f](https://github.com/stencila/hub/commit/90aaf5fe18d26773146c4855e6740d1e549045d1))

## [3.1.2](https://github.com/stencila/hub/compare/v3.1.1...v3.1.2) (2020-07-10)


### Bug Fixes

* **deps:** update dependency lxml to v4.5.2 ([94923ee](https://github.com/stencila/hub/commit/94923ee434012a3774471e7e2d51304ecf466af6))
* **Quotas:** Do not use enum ([5925ab2](https://github.com/stencila/hub/commit/5925ab22ea11e535a0d0a5901fb24d5ce862e013))

## [3.1.1](https://github.com/stencila/hub/compare/v3.1.0...v3.1.1) (2020-07-10)


### Bug Fixes

* **deps:** pin dependency @stencila/encoda to 0.97.1 ([d33a853](https://github.com/stencila/hub/commit/d33a853aff8137ce63e43ea3c3775a679281a727))
* **deps:** update dependency @stencila/thema to v2.12.0 ([8956d86](https://github.com/stencila/hub/commit/8956d862d64e101a2d8fbc6cd97ee363b80c0d5c))
* **deps:** update dependency htmx.org to v0.0.8 ([4c7492c](https://github.com/stencila/hub/commit/4c7492cc579458f00e23816cb219880a08d9a5f1))
* **Exception handling:** Handle DRF exceptions in UI views ([52c6fa6](https://github.com/stencila/hub/commit/52c6fa600a1b9ea3a037660825a1d0f0d4885512)), closes [#538](https://github.com/stencila/hub/issues/538)
* **Sources:** Remove Source.url field, add /open API endpoint instead ([16a0d80](https://github.com/stencila/hub/commit/16a0d80b345fe3706abdd1fa36dfabc6a81872ed)), closes [#539](https://github.com/stencila/hub/issues/539)
* **Worker:** Upgrade Encoda ([5320a5d](https://github.com/stencila/hub/commit/5320a5d841717df69ad9f5fb6217b1066a53ab2f))


### Performance Improvements

* **Manager:** Override url method for public media files ([9a39738](https://github.com/stencila/hub/commit/9a3973891067085565435dbc2dbe00de073a370a))

# [3.1.0](https://github.com/stencila/hub/compare/v3.0.6...v3.1.0) (2020-07-09)


### Features

* **Admin interface:** Add additional model admins ([71fa01c](https://github.com/stencila/hub/commit/71fa01c75ecd3f5130048fe3ce950425c1dfcdd7))
* **JS:** Open dropdowns on click. Needed for Product Tours ([d47e277](https://github.com/stencila/hub/commit/d47e2775dc340240265291601c6dbbe5c1847445))
* **Manager:** Allow setting STORAGE_ROOT using env var in Prod ([6371bc6](https://github.com/stencila/hub/commit/6371bc637f83c78a05a70af151db02c53192f0d0))


### Performance Improvements

* **Manager:** Improve Dockerfile gunicorn settings ([7c32275](https://github.com/stencila/hub/commit/7c32275778bc05c62dd42049089f65ceea00530a))

## [3.0.6](https://github.com/stencila/hub/compare/v3.0.5...v3.0.6) (2020-07-09)


### Bug Fixes

* **Manager:** Use simple CASE syntax and remove extra condition. ([831be6b](https://github.com/stencila/hub/commit/831be6ba5608c724382f52ef54b8b1f94d0cb4e6))
* **Manager URLs:** Improve ordering of URLs to avoid 404s for debug etc ([1625534](https://github.com/stencila/hub/commit/16255342e34dfa9370819ff67a0bdf85fa1bc419))
* **Worker:** Unique hostname and increase heartbeat interval ([0e8505f](https://github.com/stencila/hub/commit/0e8505ffd4bd4021d0f2312f6b9821bad2b51ff9))

## [3.0.5](https://github.com/stencila/hub/compare/v3.0.4...v3.0.5) (2020-07-09)


### Bug Fixes

* **Manager:** Use single quotes for string constants in Postgres ([1dc5dc5](https://github.com/stencila/hub/commit/1dc5dc50adff3d5ea8cd28622d375e56ebf476a3))

## [3.0.4](https://github.com/stencila/hub/compare/v3.0.3...v3.0.4) (2020-07-09)


### Bug Fixes

* **Manager:** Modify CASE statements for Postgres compatability ([9efeb71](https://github.com/stencila/hub/commit/9efeb71f54651e990c388c07edfe221d8a56f22e))

## [3.0.3](https://github.com/stencila/hub/compare/v3.0.2...v3.0.3) (2020-07-09)


### Bug Fixes

* **Account tiers:** Use gigabytes for limits instead of bytes ([a44be10](https://github.com/stencila/hub/commit/a44be10ea19df98a43dcef352dd085faa73480fc))

## [3.0.2](https://github.com/stencila/hub/compare/v3.0.1...v3.0.2) (2020-07-09)


### Bug Fixes

* **Manager:** Remove stencibot from migration ([bda8930](https://github.com/stencila/hub/commit/bda8930dfca8f4eef4ffd82758c33bf26ea99a13))

## [3.0.1](https://github.com/stencila/hub/compare/v3.0.0...v3.0.1) (2020-07-09)


### Bug Fixes

* **Manager:** Include manage.py in image; update version ([b82dae7](https://github.com/stencila/hub/commit/b82dae7bbc81a4a9950035abc328ae429eed61aa))

## [2.44.2](https://github.com/stencila/hub/compare/v2.44.1...v2.44.2) (2020-07-07)


### Bug Fixes

* **Manager:** Rename account quotas ([dc25312](https://github.com/stencila/hub/commit/dc2531266729e4414bb66aca8a89d55091a29fb8))

## [2.44.1](https://github.com/stencila/hub/compare/v2.44.0...v2.44.1) (2020-07-07)


### Bug Fixes

* **Manager:** Fix Docker image build; add run-docker recipe ([2dc115c](https://github.com/stencila/hub/commit/2dc115c8d81ab0adf4e16c6f962a8913e0a53702))
* **Manager:** More fixes to imports ([9bbf104](https://github.com/stencila/hub/commit/9bbf1047777df0f94d626e51e6a5ec1d2ad76438))
* **Manager:** Update location of version file ([b18978f](https://github.com/stencila/hub/commit/b18978f546347f0f628bc2bb6da03866efa54ed2))
* **Router:** Revert to proxying to director ([f7ecf4a](https://github.com/stencila/hub/commit/f7ecf4a787e90fc685928e76f7f5999b297ddad3))

# [2.44.0](https://github.com/stencila/hub/compare/v2.43.0...v2.44.0) (2020-07-07)


### Bug Fixes

* **Projects:** Allow read access by anon users to project files, sources and snapshots ([7dc09b5](https://github.com/stencila/hub/commit/7dc09b5b49c31b71d0c8020dea5d9d2ff03086ad))
* **Quotas:** Use correct property access for dict ([00f7707](https://github.com/stencila/hub/commit/00f7707ea39670c1a7a9e7201b7770fb7de36319))


### Features

* **Account tiers:** Add job runtime limits ([450828d](https://github.com/stencila/hub/commit/450828db2206724ea4c3bb9a5cf49cf3dc00d114))
* **Manager:** Feature flags ([e8ff7d2](https://github.com/stencila/hub/commit/e8ff7d25827f39465cb8cb7ee6e890eedce04b8d))
* **Plans:** Add Plan page for accounts ([3498a60](https://github.com/stencila/hub/commit/3498a60a39cefa1c94b567f2ddc1f4dbc5178ec9))
* **User signin:** Add social account buttons to signup page ([0b2cd5f](https://github.com/stencila/hub/commit/0b2cd5f08abeb558e0bd14430c69d52a3d42e108))

# [2.43.0](https://github.com/stencila/hub/compare/v2.42.0...v2.43.0) (2020-07-06)


### Bug Fixes

* **deps:** update dependency @popperjs/core to v2.4.4 ([c257112](https://github.com/stencila/hub/commit/c2571121224cb1c1b49da7edf9ee4c0ce70f1cde))
* **deps:** update dependency sentry-sdk to v0.16.0 ([e07ee93](https://github.com/stencila/hub/commit/e07ee9332ea0d71b1eb332bdf56b719bf1b9eee8))
* **Jobs:** Select related creator and their account ([4d78575](https://github.com/stencila/hub/commit/4d78575f234ba85630115194e492e3c7efeeaeb8))
* **Manager:** Correct for change in HTMX event names ([c1c16a5](https://github.com/stencila/hub/commit/c1c16a58a6463e73a57ef7d6d9cc100de7b0e9d9))
* **Manager:** Upgrade dependencies ([8417e56](https://github.com/stencila/hub/commit/8417e563bc8028dbabb00bb110f1e7788e46c191))
* **Manager sessions:** Use session storage to reduce db queries ([123bf5c](https://github.com/stencila/hub/commit/123bf5c3ba3d089e954779329417b4ec0ec3989d))
* **Overseer:** Make robust to manager being down ([986d9e6](https://github.com/stencila/hub/commit/986d9e6cae557d1e0203a673a2c5cf7f2dc7b3fa))
* **Snapshots:** Prefetch job ([b78f71c](https://github.com/stencila/hub/commit/b78f71c883baef4ce418aac1a269540cd20c0382))
* **Worker:** Fix typings ([6c23163](https://github.com/stencila/hub/commit/6c231633cf365ddc1827848cf62f9e15870005e0))
* **Worker convert:** Set format from mimetype ([ffa24b2](https://github.com/stencila/hub/commit/ffa24b23828ca2aa5c08086bff6f8aa9ef2ac836))


### Features

* **Files:** Add action menu for files and setting of main ([17d9cef](https://github.com/stencila/hub/commit/17d9cefd4b5f494abf6ea4326a3262c71e985f74))

# [2.42.0](https://github.com/stencila/hub/compare/v2.41.0...v2.42.0) (2020-07-03)


### Bug Fixes

* **deps:** update dependency @popperjs/core to v2.4.3 ([72a4d4c](https://github.com/stencila/hub/commit/72a4d4c795682d49029ce157add6606d3a31cf49))
* **deps:** update dependency @stencila/encoda to v0.97.0 ([e2a8af2](https://github.com/stencila/hub/commit/e2a8af2a7a8f1057a7121b802440e6bebedc8f70))
* **deps:** update dependency @stencila/thema to v2.10.4 ([50bddc1](https://github.com/stencila/hub/commit/50bddc1b4eaae000dddc5ebcc76bc2b8735bd05d))
* **deps:** update dependency celery to v4.4.6 ([2b12744](https://github.com/stencila/hub/commit/2b12744b162224a64878282c8f63c53e50732b98))
* **deps:** update dependency django to v2.2.14 ([3c17f3a](https://github.com/stencila/hub/commit/3c17f3ad3f9fb1d2b27d5a17e1f3dea51d460068))
* **deps:** update dependency django-extensions to v3 ([f6f6dff](https://github.com/stencila/hub/commit/f6f6dff7313b29d5839f1dd426fb3874d553e792))
* **deps:** update dependency google-cloud-storage to v1.29.0 ([41593c5](https://github.com/stencila/hub/commit/41593c5a60642b645a5330910088f664f46e2226))
* **deps:** update dependency htmx.org to v0.0.7 ([bd6bce9](https://github.com/stencila/hub/commit/bd6bce98cc8d5d4cff256902b317531aa131de2f))
* **deps:** update dependency pillow to v7.2.0 ([f48ebf5](https://github.com/stencila/hub/commit/f48ebf5511f46c6ac42da409a9360fca8bedf662))
* **HTMX Buttons:** Remove loading for buttons in forms ([b8d7ffc](https://github.com/stencila/hub/commit/b8d7ffc867b030f59da195ad438e9a6f67c51bfa))
* **Invites:** Mark accepted after signup. ([3665b5c](https://github.com/stencila/hub/commit/3665b5c185546ec0536fd99abcdcd22a65c8690e))
* **Lint:** Fix linting error ([17d575f](https://github.com/stencila/hub/commit/17d575fdab9274ce0eee391bd8dca21caebbe74c))
* **Project:** Raise a 404, not permission denied ([bd3bb0a](https://github.com/stencila/hub/commit/bd3bb0a6aee9fa8fd90bcf8073aa8f6f5df7d40f))
* **Projects:** Allow for all roles ([936b124](https://github.com/stencila/hub/commit/936b124d9da9f1ff087482839e6cc9ce0d02154f))


### Features

* **Invitations:** Add invite model and views ([9637cc2](https://github.com/stencila/hub/commit/9637cc24059f213a102f8babb21675d5020c49ff))
* **Invites:** Add links to invites pages ([5172f84](https://github.com/stencila/hub/commit/5172f841e2efea8cf2d082dd116ea52a7f90d352))
* **Invites:** Add more info to invites listing; change order ([27af173](https://github.com/stencila/hub/commit/27af173ef54d04fa315c21ddb184e66d51977df3))
* **Invites:** Add views for creating and listing invites ([fe0bd4f](https://github.com/stencila/hub/commit/fe0bd4f8a0b4cac2fb71a4b430d2de585c49d6b8))
* **Invites:** Allow inviters to select the project / account role ([ee1f189](https://github.com/stencila/hub/commit/ee1f189d1af764da7bbd4c5d23ee7ffb7b4186b8))
* **Invites:** Custom templates for emails, messages and creating ([b8111d0](https://github.com/stencila/hub/commit/b8111d073f234470b449e9f402a2999ffc8fb689))
* **Invites:** Style list of invites ([816cd6e](https://github.com/stencila/hub/commit/816cd6e262fc2bf741fc8b62a757a17f242cb570))
* **Jobs:** Expose sub-jobs in line with parent Job ([b5916dc](https://github.com/stencila/hub/commit/b5916dce0ea953c8de55e51d17d354cca796dcdf))

# [2.41.0](https://github.com/stencila/hub/compare/v2.40.0...v2.41.0) (2020-06-30)


### Bug Fixes

* Standardize view header/action bar layouts ([97cb263](https://github.com/stencila/hub/commit/97cb263f87745ad39b8358eb02333b293ddf096e))
* **Files:** Use get_or_create and ensure options is a dict. ([16dd90b](https://github.com/stencila/hub/commit/16dd90bd3ceee7e86dcaae1287e057d588037f36))
* **Jobs:** Cancel waiting jobs if a predecessor fails ([37a81ba](https://github.com/stencila/hub/commit/37a81bae07ddd5f44e3403681d9f98da4a93e557))
* **Projects:** Make Source filter full-width on mobile view ([0190613](https://github.com/stencila/hub/commit/019061375ba836a4fb635e4089e009bb7ddad06b))
* **Snapshots:** Style snapshot preview page ([b85f72b](https://github.com/stencila/hub/commit/b85f72b5f73d30e43669edd13356b0fd066f1df1))
* **Upload sources:** Make URL and address based on storage type ([73b5504](https://github.com/stencila/hub/commit/73b550488de1c79c8eb4e9b778ef6f273e6f7a51))


### Features

* **Files and snapshots:** Allow specifying main file for a project; snapshot viewing and download ([d59db75](https://github.com/stencila/hub/commit/d59db75d4c652660bab870d4ed1ae35eab0d1fba))
* **Projects:** Hide time & file size on mobile views for improved UI ([ce6efb6](https://github.com/stencila/hub/commit/ce6efb64b640d0af9b9f9bcb1372f1ef7280632c))
* **Projects:** Match project sidebar layout/header to Org view ([0a76915](https://github.com/stencila/hub/commit/0a769157eea61ba7c3f869037b0e6b719a3e1562))
* **Worker:** Add pull job for local files ([c329ce7](https://github.com/stencila/hub/commit/c329ce72a9373509afc70e3f440673044c3c2a74))

# [2.40.0](https://github.com/stencila/hub/compare/v2.39.0...v2.40.0) (2020-06-29)


### Bug Fixes

* **CSS:** Don't delay spinning animation start ([470ef78](https://github.com/stencila/hub/commit/470ef788b72e40ea1d8b1c75c9f9ba1237871f2a))
* **Jobs:** Update status of parallel jobs ([e5f3af5](https://github.com/stencila/hub/commit/e5f3af52add448d89916f1bb903a0f486c67440d))
* **Projects:** Don't show link to File Source when listing Sources files ([2f181db](https://github.com/stencila/hub/commit/2f181dbd809dcb92bf97ebfee476c1d4b95b8202))
* **Projects:** Standardize elements across views ([da06261](https://github.com/stencila/hub/commit/da06261c15bca88b44d27551718e3c4dbb8d553a))
* **Projects:** Use Breadcrumbs component for file list view ([c24ac4b](https://github.com/stencila/hub/commit/c24ac4b035eab172c0c4f5bdcd628cafd3dc78dc))
* **Snapshots:** Add copy sub-job; improve updating of compound jobs ([cc29e23](https://github.com/stencila/hub/commit/cc29e23d269586a6abd3bb00ba942e3fc9e42a2d))
* **Snapshots:** Partially style Snapshot listing page ([d1935fe](https://github.com/stencila/hub/commit/d1935fe069ba568f7cdb88efcc94a7fafe855842))
* **Worker:** Set GDoc mimetype on pull ([79e86d0](https://github.com/stencila/hub/commit/79e86d0bcc685745d6f45dbe4491641bd18e5a67))
* **Worker:** Set JATS mimetype on pull ([10f6c5b](https://github.com/stencila/hub/commit/10f6c5b37332b9e225505801a50796a877a8cb2b))


### Features

* **Projects:** Hide project hero section when listing sub-directories ([0fe09a2](https://github.com/stencila/hub/commit/0fe09a21a5a2c5f9e8c5ad688da5b769cc3a0990))
* **Projects:** Move directory content count to name field ([9f4e6b6](https://github.com/stencila/hub/commit/9f4e6b638251320a35528fe552424a195bac3f91))
* **Snapshots:** Record files for each snapshot ([fe289cc](https://github.com/stencila/hub/commit/fe289ccaa29433da3e2a40e6d3606e76450e9313))
* **Sources:** Add pull all project sources action ([49c8eaa](https://github.com/stencila/hub/commit/49c8eaa264b3cef1a3ef98cfd3378c8ab4b0daa3))
* **Sources:** Improve source views and pull on creation ([a774595](https://github.com/stencila/hub/commit/a77459595e885f4363e90dd4fb780fed2baf2298))
* **UX:** Show spinner when buttons perform async operations ([2ee55d5](https://github.com/stencila/hub/commit/2ee55d531096db6a46981a4515a6436ac0910ac5))
* **Worker:** Add copy job for use with snapshots ([4a87367](https://github.com/stencila/hub/commit/4a873675598469d83ebbc75434d3e3e381dda79a))

# [2.39.0](https://github.com/stencila/hub/compare/v2.38.0...v2.39.0) (2020-06-28)


### Bug Fixes

* **Files:** Merge two file filters from different branches ([1effa36](https://github.com/stencila/hub/commit/1effa369a6cd4e550585d80c83cfd93738be5b93))


### Features

* **Files:** Add aggregation to directory ([b9090de](https://github.com/stencila/hub/commit/b9090de573d4e6ab82602a1fc408b4c5f70c2079))
* **Files:** Add breadcrumbs and remove prefix ([b09f171](https://github.com/stencila/hub/commit/b09f171c5b8705f904559e96e59db4cdf6465555))
* **FIles:** Add filtering by name and prefix ([1137c8a](https://github.com/stencila/hub/commit/1137c8a12dd58811fb4da385e87b413432fecd86))

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
