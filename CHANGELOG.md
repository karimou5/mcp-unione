# Changelog

## [0.2.0](https://github.com/karimou5/mcp-unione/compare/v0.1.0...v0.2.0) (2026-06-04)


### Features

* async UniOne httpx client with error mapping ([25dce9f](https://github.com/karimou5/mcp-unione/commit/25dce9fe817f1beb8163e526a8525aab7085e0be))
* config from env with eu default region ([a412b9f](https://github.com/karimou5/mcp-unione/commit/a412b9fb7bd6902582904d59e324915455755db2))
* docs tools (search, live fetch, error/status lookup) ([2f960ee](https://github.com/karimou5/mcp-unione/commit/2f960ee1624d6a0225f86832828db43edb51fb57))
* domain tools ([6f8e8e5](https://github.com/karimou5/mcp-unione/commit/6f8e8e514781f3fb67f8971b90571565d6c71456))
* email send (with send-guard) + subscribe tools ([18aaaef](https://github.com/karimou5/mcp-unione/commit/18aaaef27c2e1300705b252996fca8aa3926b7d2))
* email validation tool ([c4cc26c](https://github.com/karimou5/mcp-unione/commit/c4cc26cd0da37bb984bdb3e4a9063fd6c65c81be))
* event-dump tools ([1414287](https://github.com/karimou5/mcp-unione/commit/1414287be1c240b03572546cebfa0a892a8f95b5))
* expose knowledge base as MCP resources ([eb54d63](https://github.com/karimou5/mcp-unione/commit/eb54d63eb3255eb5d5d36f592874dca054bec8fb))
* FastMCP server skeleton + stdio entrypoint ([47efe26](https://github.com/karimou5/mcp-unione/commit/47efe26dc6a731385c51ce0161d844044bb58ac5))
* generate curated KB, error table, status maps from research ([d37acf2](https://github.com/karimou5/mcp-unione/commit/d37acf2d984aa31b30afe8553729d8581111be3d))
* MCP prompts for composing/diagnosing email ([c0f74b6](https://github.com/karimou5/mcp-unione/commit/c0f74b65aeb0b90ce04f2790fa087e0ae29b8d27))
* MCP UniOne server — transactional API tools + hybrid knowledge base ([1c22f18](https://github.com/karimou5/mcp-unione/commit/1c22f18e689bc4f5c200edfb4840e87c0c536d33))
* suppression tools ([f209809](https://github.com/karimou5/mcp-unione/commit/f209809083b2e6274a35256c5979fd0bd6f605f4))
* system ping/info tools ([4fe7f42](https://github.com/karimou5/mcp-unione/commit/4fe7f42142ebfda87cbd0ad7b10c88b145ce0fd7))
* tag + project tools ([f57f79b](https://github.com/karimou5/mcp-unione/commit/f57f79b6a97e0d1d174d5330b3ed07c8c39df32c))
* template tools ([e2785ff](https://github.com/karimou5/mcp-unione/commit/e2785ff52a8a7f91882f8dc2655ceaf34888b662))
* UniOneError + error-code enrichment ([e5365e9](https://github.com/karimou5/mcp-unione/commit/e5365e9266726bf6d49e0de649b1203ff89b6658))
* webhook tools ([dc16ead](https://github.com/karimou5/mcp-unione/commit/dc16eadd4bc462b46b8df79d3f4a886c88417a25))


### Bug Fixes

* align event-dump/project params with UniOne API reference (start_time required, delimiter default, backend_domain_id) ([03baf05](https://github.com/karimou5/mcp-unione/commit/03baf052c4667d6ba3935fb08cff0ac8d2371175))
* harden docs tools (empty-query, missing-kb, case-insensitive status) and cache reads ([7422c08](https://github.com/karimou5/mcp-unione/commit/7422c08e13eaa776b3843c48be12f6949f2ed876))
* harden email send-guard (body semantics, empty inputs) and tests ([8cb8946](https://github.com/karimou5/mcp-unione/commit/8cb894615481db36e59394d63276ac436088b66e))
* skip stray delivery_status header row; harden KB generator + data tests ([d7fefe6](https://github.com/karimou5/mcp-unione/commit/d7fefe645d2b3d966455fc891b02a468b9833682))


### Documentation

* add MCP UniOne design spec and API research notes ([99f45ca](https://github.com/karimou5/mcp-unione/commit/99f45ca93d59dbad81fbd593b08291ce3d01d1c8))
* add MCP UniOne implementation plan ([996e23f](https://github.com/karimou5/mcp-unione/commit/996e23f9f90ec9b1a02b1d145bcf2d255343ddaf))
* README with setup, config, tools, and safety notes ([000d298](https://github.com/karimou5/mcp-unione/commit/000d298178477286930d537c6481c47f9cc87c5c))


### Code Refactoring

* address Phase 0 review (client return type, url normalization, lint, test cleanup) ([96f23c9](https://github.com/karimou5/mcp-unione/commit/96f23c9571a4f8f704f86ad9ce37ab91de4e6470))
