# Maven/Travis CI Example

Shows a working setup for travis integration to extract project dependencies

## Travis CI Setup

The `.travis.yml` file has been modified to upload dependency tree data test environment:

```yaml
after_success:
  - bash <(curl -s URL)
```
