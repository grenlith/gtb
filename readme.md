# gtb

the gemlog tractor beam

## what is it?

### turn your social media posts into gemtext files

- keep your gemini capsule fresh with this one neat trick!
- you probably post all the time, why not let people see your brilliant posting outside of the web?

### expectations

- i wrote this for me; if you don't like something, take a look at the contributing section
- this is or is not in a state of development at any given time
  - i may have hacky solutions in place that i just haven't gotten around to testing

## how do i run it?

### requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### configuration

- `cp config-example.yml config.yml`
  - edit `config.yml` to add collectors and specify your options
  - the example is kept up to date with all relevant configuration options

### running

i tried to make this as simple as i could so it could easily run under a user's crontab.

`uv run main.py -o /path/to/desired/directory/`

you can optionally specify a configuration file path with `-c` or `--config`

## how do i hack on it?

### setting up the venv

`uv sync --all-groups`

`source .venv/bin/activate`

you should use the appropriate activation script for your shell; mine is `activate.fish`, for example.

### linting

this project uses [ruff](https://docs.astral.sh/ruff/) for linting.

`ruff check --fix .`

### typing

i tried to use type hints throughout this project and i check them with [mypy](https://mypy-lang.org)

[markdownify](https://github.com/matthewwithanm/python-markdownify) in particular did not have type definitions or a types library, so it is ignored in `mypy.ini`

`mypy.ini` also specifies strict, so this part is easy

`mypy .`

## contributing

i will accept pull requests, but there is no guarantee on when i get around to them. hopefully you have the information you need :)
