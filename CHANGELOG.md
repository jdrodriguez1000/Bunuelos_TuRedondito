# Changelog

## [0.12.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.11.0...Bunuelos_TuRedondito-v0.12.0) (2026-03-18)


### Features

* **agent:** update workflows and skills for project lifecycle and st… ([081d78a](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/081d78a3221e39275c15bbc7cd11bff4401e5565))
* **agent:** update workflows and skills for project lifecycle and strategic communication ([364eaae](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/364eaaea0ead087eb1a374d67e77ede27d5d8421))

## [0.11.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.10.0...Bunuelos_TuRedondito-v0.11.0) (2026-03-18)


### Features

* **skill:** expand project_lifecycle_expert to 6 execution modes with full traceability ([65722d2](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/65722d2538120a70747acdfdd1832d6d85893511))
* **skill:** expand project_lifecycle_expert to 6 modes including Task List and Project Plan ([2951cf0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/2951cf02a9768b1c2e3909936d0e4fb811351547))


### Bug Fixes

* **workflow:** add dvc pull and remove blocked push to protected main ([fe403ed](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/fe403ed3581ce4fc2363623540f819ac89f94e5d))
* **workflow:** add dvc pull for incremental load and remove blocked push to main ([8209060](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/8209060a135bb77a44e3858a7420622b9dc8f2fd))

## [0.10.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.9.0...Bunuelos_TuRedondito-v0.10.0) (2026-03-17)


### Features

* **pipeline:** rename INCREMENTAL to INCR and fix bootstrap logic ([873e244](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/873e2442db771bc868d40c8178f9fbc2b90c9034))
* **pipeline:** unify load terminology to INCR and optimize bootstrap sync logic ([24a3f9e](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/24a3f9e13b445b43afead2fb8b7f01bffed63ce6))

## [0.9.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.8.0...Bunuelos_TuRedondito-v0.9.0) (2026-03-17)


### Features

* **governance:** refine kpi names, implement recovery mode and updat… ([66235f8](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/66235f83d7ef0056a2f9f788557306af3b5f8d8f))
* **governance:** refine kpi names, implement recovery mode and update rules ([10cc05b](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/10cc05b1b0386f056b6fdedf8e2eedc51f0dbff4))

## [0.8.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.7.0...Bunuelos_TuRedondito-v0.8.0) (2026-03-16)


### Features

* **contract:** enable ipc and smlv tables for ingestion ([41b2b10](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/41b2b10e3276753ad8244946f6f8b812d08c74a9))
* **contract:** enable sales table for ingestion ([f6711f5](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/f6711f58e8bbf0f340dbebddaecd537db7f5822e))
* **dashboard:** cloud-native dynamic authorized tables from supabase contract ([0fbf662](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/0fbf66256d68b832feec221d1df1c63bb48e6057))
* **dashboard:** refine last sync indicator to be ultra-discreet and in English ([82753f8](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/82753f88e0e4a95242cc63d86dafde00200dac9c))
* Hard Reset & Dynamic Governance for Production Readiness ([cad8404](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/cad840472da60aa57b4f2d81757942b237424573))


### Bug Fixes

* **dashboard:** add usr_salario_minimo_anual to audit view ([b16cba8](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/b16cba85c2eb6a69dd2f2945b4b83a8945ba9c97))
* explicit cleaning before dvc add ([d90bb40](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/d90bb4090896ee82e83db8334ca39727294f7b3b))
* **pipeline:** enable verbose DVC errors and secure local config ([efd02e6](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/efd02e6568b79174ca88316f366dd153a7ea4240))
* **pipeline:** overhaul bootstrap configuration for clean start ([2485257](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/248525735b0d8303aaf9430fb40b3840a4f6d26d))
* **pipeline:** remove obsolete scripts and fix auto-commit logic ([c2cd19a](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/c2cd19a81a90c798c193ce656b64f4b1cfcb7d75))

## [0.7.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.6.0...Bunuelos_TuRedondito-v0.7.0) (2026-03-16)


### Features

* **dashboard:** refine health scoring logic and enhance dashboard UI status indicators ([5466e0e](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/5466e0ea66110eca9a15b171d744d90e2bc31848))
* **dashboard:** refine health scoring logic and enhance dashboard UI… ([62ea982](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/62ea982e472177a1aa502a31a209d2200355bbd9))

## [0.6.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.5.0...Bunuelos_TuRedondito-v0.6.0) (2026-03-16)


### Features

* **ops:** establish automated daily data pipeline at 02:00 COL ([b4abdc5](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/b4abdc52931a983049bc0be5a7c5a2da274e904b))
* **ops:** establish automated daily data pipeline at 02:00 COL ([1eb7905](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/1eb7905a8e4050b3daa43def7d06edc2edbda00c))
* **ops:** implement scheduled daily data pipeline at 02:00 COL ([4766827](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/4766827950fa925b33477150b43d5515c527f6c7))

## [0.5.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.4.0...Bunuelos_TuRedondito-v0.5.0) (2026-03-16)


### Features

* **dashboard:** implement monitoring logic and quality gate validation ([4c4d2e1](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/4c4d2e12b9caf6f388ce681622f0f75226bac5b7))
* **dashboard:** implement monitoring logic and quality gate validation ([f332d04](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/f332d041b367e8836b947c132f3451f03a7d66f1))
* **dashboard:** implement monitoring logic and quality gate validation ([9fb49e3](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/9fb49e331fd4133c8d48e65ffc973581bc4b2ec1))

## [0.4.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.3.0...Bunuelos_TuRedondito-v0.4.0) (2026-03-16)


### Features

* **arch:** complete Phase 01: infrastructure, connectivity, and data contract [MILESTONE-03] ([4c37cd3](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/4c37cd36760579794231d36174ba47d1ab5e9f58))
* complete Stage 2.2 and sync Cloud-DVC with Supabase S3 bucket dvc_Bunuelos_TuRedondito ([7d816b9](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/7d816b95c7ed62aea03b549551451cdce08d6449))
* Finalización Etapa 2.2 - Ingesta, Gobernanza y Consolidación Documental ([01d640c](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/01d640c7a4a49aa3d7a24f36d9fb505e51a45a69))
* **ingestion:** completar etapa 2.2, consolidar reportes y cerrar gobernanza ([e97cf1e](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/e97cf1e41153064feccf800122f7f423cff1b017))


### Bug Fixes

* desacoplar configuración de S3 en tests y mejorar robustez de conectores ([a52dcca](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/a52dcca9739a97bf8c91393c93d6d2362c4aa13e))

## [0.3.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.2.0...Bunuelos_TuRedondito-v0.3.0) (2026-03-14)


### Features

* implement db connector with s3 and double persistence reporting ([8c7b422](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/8c7b422359393ae9ebb13aec62b9231c3b82b647))
* implement db connector with s3 and double persistence reporting ([c6ac525](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/c6ac525844a4a4c86e2386cb6653b2bd083927c2))


### Bug Fixes

* **test:** mock environment variables in unit tests to fix CI failure ([98fc8f4](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/98fc8f46378a8eef8f6070c7aede40f5bab79686))

## [0.2.0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/compare/Bunuelos_TuRedondito-v0.1.0...Bunuelos_TuRedondito-v0.2.0) (2026-03-13)


### Features

* Configuracion Inicial de Infraestructura y CI ([d967bd3](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/d967bd329f2e4347b0e89d2dfd9540df087f19f8))
* infraestructura inicial y gobernanza ([0fbb55e](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/0fbb55ed9e8224d987360322208a4544cd0ded5c))
* infraestructura inicial, gobernanza y pipeline de CI ([d818f8d](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/d818f8d070c2dc1d79f89452cf0c240aa942ca03))
* infraestructura inicial, gobernanza, testing y pipeline de CI ([3252b6f](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/3252b6f0ba14f1a2ec49dd360b5aa36af1c25aee))
* integración de sistema de releases automatizado (Release Please) ([c20911e](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/c20911ecfd972d4506e90dcac0acadc582232682))
* integrar google release-please para automatización de versiones ([6c075d4](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/6c075d45c3e77909d05e98174560de5cfd6eed9a))


### Bug Fixes

* asegurar que el directorio src exista en Git mediante .gitkeep ([edd62f0](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/edd62f04f5be2f0acd7cf738b91206c9f5fd5fea))
* resolver conflictos de merge en README.md y .gitignore ([15eaec8](https://github.com/jdrodriguez1000/Bunuelos_TuRedondito/commit/15eaec8e2e44f7a019ee40b62a7b0108a1b27226))
