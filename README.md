![Plugin Tests](https://github.com/qporest/pytest-exception-script/workflows/Plugin%20Tests/badge.svg?branch=master)
# pytest-exception-script
The goal of this pytest plugin is to allow quick and easy testing of your application's resiliency. This is accomplished by creating exception scripts / scenarios which allow you to inject exceptions into your code execution without having to repeatedly set-up tests.

This won't work for applications that have multiple processes, but should work with threads (need to do more testing). Under the hood it's just abusing monkeypatch.

### Structure
Scripts can be written in YAML or TOML.
Each script / scenario (these will be used interchangeably below) consists of multiple acts, each of which can have multiple actions. Scenario is successful and complete if every act in it is complete.
**To have your script detected**: make sure it starts with `chaos_` and is a toml or yaml file. It will get auto-discovered by pytest, or you can call pytest directly against the file.

#### Examples of config files:
Using `yaml`
```
entry-point: tests.fake_app_success.factory
next-point: tests.fake_app_success.process_data
acts:
  - tests.fake_app_success.get_data:
      - exc: KeyError, "Error in act I"
        next-point: 
    tests.fake_app_success.unused_method:
      - exc: OSError, "Custom message passed"
  - tests.fake_app_success.get_data:
      - exc: KeyError
```
Using `toml`
```
entry-point="tests.fake_app_success.factory"
next-point="tests.fake_app_success.process_data"
[[act]]
[[act."tests.fake_app_success.get_data"]]
exc="KeyError"
next-point="tests.fake_app_success.process_data"
[[act]]
[[act."tests.fake_app_success.get_data"]]
exc="KeyError"
[[act]]
[[act."tests.fake_app_success.get_data"]]
exc="KeyError"
```
#### What's happening here?
`entry-point` should be a factory for your application that takes no parameters.
`next-point` - can be specified globally, per act, or both. Once this method gets called script will move on to the next act.
`acts` - list of acts each of which consists of actors. Each Actor is a method and an exception that it will throw if called during execution.
`exc` - exception to raise.

So factory will be loaded and started, upon which first act starts. Every time when `get_data` will get called `KeyError` will be raised. With either a default or a custom message. Once `next-point` gets called next act starts. Once `next-point` of the last act is called the application terminates (hopefully) and all the tests get marked as complete.