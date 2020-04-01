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
