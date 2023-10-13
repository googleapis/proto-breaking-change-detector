# Changelog

## [2.4.0](https://github.com/googleapis/proto-breaking-change-detector/compare/v2.3.0...v2.4.0) (2023-10-13)


### Features

* Check field format changes ([#404](https://github.com/googleapis/proto-breaking-change-detector/issues/404)) ([461206c](https://github.com/googleapis/proto-breaking-change-detector/commit/461206c230cdeba41b43d0f17c8205fbbbc8fea6))
* Detect docs changes ([#405](https://github.com/googleapis/proto-breaking-change-detector/issues/405)) ([8a24168](https://github.com/googleapis/proto-breaking-change-detector/commit/8a24168af875235cedf4009f865e2e0649c12e27))

## [2.3.0](https://github.com/googleapis/proto-breaking-change-detector/compare/v2.2.0...v2.3.0) (2023-08-25)


### Features

* CLI flag and a method to return all changes ([#378](https://github.com/googleapis/proto-breaking-change-detector/issues/378)) ([28fb873](https://github.com/googleapis/proto-breaking-change-detector/commit/28fb87315db63bec7431f4cdcbdda620bed77803))

## [2.2.0](https://github.com/googleapis/proto-breaking-change-detector/compare/v2.1.2...v2.2.0) (2023-08-16)


### Features

* Detect when a message is moved to another file ([#374](https://github.com/googleapis/proto-breaking-change-detector/issues/374)) ([dd4d3f3](https://github.com/googleapis/proto-breaking-change-detector/commit/dd4d3f3337bc3268ce5f0e6fd5f8e872746857a2))
* Introduce conventional commit tag ([#334](https://github.com/googleapis/proto-breaking-change-detector/issues/334)) ([f0317ff](https://github.com/googleapis/proto-breaking-change-detector/commit/f0317ffbc9c59719f9ecee72fab9acb8bab4fd38))

## [2.1.2](https://github.com/googleapis/proto-breaking-change-detector/compare/v2.1.1...v2.1.2) (2023-02-21)


### Bug Fixes

* Changing proto3 optional is a breaking change ([#303](https://github.com/googleapis/proto-breaking-change-detector/issues/303)) ([8518bf3](https://github.com/googleapis/proto-breaking-change-detector/commit/8518bf377050b1f83a06797d8400bf1a3a83d507))

## [2.1.1](https://github.com/googleapis/proto-breaking-change-detector/compare/v2.1.0...v2.1.1) (2022-11-28)


### Bug Fixes

* Treat a change to an optional field correctly ([#283](https://github.com/googleapis/proto-breaking-change-detector/issues/283)) ([0eb0fda](https://github.com/googleapis/proto-breaking-change-detector/commit/0eb0fda6ea459ed8ec38ce0957a46e2a014d4d7b)), closes [#220](https://github.com/googleapis/proto-breaking-change-detector/issues/220)

## [2.1.0](https://github.com/googleapis/proto-breaking-change-detector/compare/v2.0.2...v2.1.0) (2022-11-04)


### Features

* Add METHOD_SIGNATURE_ORDER_CHANGE ([#276](https://github.com/googleapis/proto-breaking-change-detector/issues/276)) ([90cdeee](https://github.com/googleapis/proto-breaking-change-detector/commit/90cdeeec43b2bcbe221a3f65c971a91ea5098346))


### Bug Fixes

* Change the internal representation of method signature ([#274](https://github.com/googleapis/proto-breaking-change-detector/issues/274)) ([056f4c0](https://github.com/googleapis/proto-breaking-change-detector/commit/056f4c0cf64821eb099c8291ca8041d23ca35a78))


### Dependencies

* Update protobuf to 4.21.9 ([#271](https://github.com/googleapis/proto-breaking-change-detector/issues/271)) ([14cd00b](https://github.com/googleapis/proto-breaking-change-detector/commit/14cd00bf8a6b65093dfd4df123c9de8645ff1fc5))

## [2.0.2](https://github.com/googleapis/proto-breaking-change-detector/compare/v2.0.1...v2.0.2) (2022-09-14)


### Bug Fixes

* Allow adding a new alias in Enum ([#249](https://github.com/googleapis/proto-breaking-change-detector/issues/249)) ([fe3d5ef](https://github.com/googleapis/proto-breaking-change-detector/commit/fe3d5efc6b12de97cef47c7543686295120f9499)), closes [#205](https://github.com/googleapis/proto-breaking-change-detector/issues/205)

## [2.0.1](https://github.com/googleapis/proto-breaking-change-detector/compare/v2.0.0...v2.0.1) (2022-08-31)


### Bug Fixes

* use hash for requirements.txt ([#238](https://github.com/googleapis/proto-breaking-change-detector/issues/238)) ([5981542](https://github.com/googleapis/proto-breaking-change-detector/commit/598154208c216e4690205a0150fdccbef78e34e5))

## [2.0.0](https://github.com/googleapis/proto-breaking-change-detector/compare/v1.2.2...v2.0.0) (2022-08-30)


### ⚠ BREAKING CHANGES

* change directory structure (#235)

### Bug Fixes

* change directory structure ([#235](https://github.com/googleapis/proto-breaking-change-detector/issues/235)) ([af233bb](https://github.com/googleapis/proto-breaking-change-detector/commit/af233bbcfb7a9d904c0fdf6b69dade9e1f7e94fe))

## [1.2.2](https://github.com/googleapis/proto-breaking-change-detector/compare/v1.2.1...v1.2.2) (2022-07-12)


### Bug Fixes

* silence some type errors ([#230](https://github.com/googleapis/proto-breaking-change-detector/issues/230)) ([1493660](https://github.com/googleapis/proto-breaking-change-detector/commit/149366093b14f3c873799cf174d5bbdb04d6db0b))

### [1.2.1](https://github.com/googleapis/proto-breaking-change-detector/compare/v1.2.0...v1.2.1) (2022-05-05)


### Bug Fixes

* do not report file option changes for new or removed files ([#216](https://github.com/googleapis/proto-breaking-change-detector/issues/216)) ([93c215c](https://github.com/googleapis/proto-breaking-change-detector/commit/93c215ce0b73a7b29814fba5cf6fd54ea66b39bd))

## [1.2.0](https://github.com/googleapis/proto-breaking-change-detector/compare/v1.1.2...v1.2.0) (2022-02-15)


### Features

* check for the java_multiple_files option ([#201](https://github.com/googleapis/proto-breaking-change-detector/issues/201)) ([f1fa654](https://github.com/googleapis/proto-breaking-change-detector/commit/f1fa654ee63d9a2238d0483ded4b98a1416463de))

### [1.1.2](https://github.com/googleapis/proto-breaking-change-detector/compare/v1.1.1...v1.1.2) (2022-01-11)


### Bug Fixes

* location info for field and enum name changes ([#197](https://github.com/googleapis/proto-breaking-change-detector/issues/197)) ([b824451](https://github.com/googleapis/proto-breaking-change-detector/commit/b824451a908894bf9e4d9b424e4b205e74276f08))

### [1.1.1](https://www.github.com/googleapis/proto-breaking-change-detector/compare/v1.1.0...v1.1.1) (2021-12-02)


### Bug Fixes

* disable bad return type check ([#187](https://www.github.com/googleapis/proto-breaking-change-detector/issues/187)) ([c1488a6](https://www.github.com/googleapis/proto-breaking-change-detector/commit/c1488a6911829e051d92a3fde70bcb6a00f30bf3))
* fix the logic for finding package name ([#192](https://www.github.com/googleapis/proto-breaking-change-detector/issues/192)) ([d0c5280](https://www.github.com/googleapis/proto-breaking-change-detector/commit/d0c52809cd337f286d3c34944a4f89d81c136a67))

## [1.1.0](https://www.github.com/googleapis/proto-breaking-change-detector/compare/v1.0.2...v1.1.0) (2021-10-08)


### Features

* --no_line_numbers disables lines numbers output ([#185](https://www.github.com/googleapis/proto-breaking-change-detector/issues/185)) ([bdf0293](https://www.github.com/googleapis/proto-breaking-change-detector/commit/bdf02939b8b09c8c542a376c3825a1235c58dc8d))
* context-aware messages ([#180](https://www.github.com/googleapis/proto-breaking-change-detector/issues/180)) ([10e384a](https://www.github.com/googleapis/proto-breaking-change-detector/commit/10e384a32cb7329c4b3d7ad34103bfcd1082c2fa))
* nonzero exit code means there are breaking changes ([#176](https://www.github.com/googleapis/proto-breaking-change-detector/issues/176)) ([06490a9](https://www.github.com/googleapis/proto-breaking-change-detector/commit/06490a9118412b739a847227c1c4983f8418d0d8))
* pretty-print JSON output ([#178](https://www.github.com/googleapis/proto-breaking-change-detector/issues/178)) ([218ff85](https://www.github.com/googleapis/proto-breaking-change-detector/commit/218ff854ab923f377da640a6d3967ec0952fe644))
