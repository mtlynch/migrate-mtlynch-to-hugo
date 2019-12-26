# migrate-mtlynch-to-hugo

[![CircleCI](https://circleci.com/gh/mtlynch/migrate-mtlynch-to-hugo.svg?style=svg)](https://circleci.com/gh/mtlynch/migrate-mtlynch-to-hugo)

## Overview

Scripts to migrate the Jekyll version of mtlynch.io to Hugo.

## Caveat

This code is very ugly, and I designed it as a one-off script and not necessarily something that others can reuse. Much of the logic is specific to features of mtlynch.io. That said, I'm leaving it public and MIT licensed in case any of the code is useful to you.

## Installation

```bash
mkdir -p ./venv
virtualenv --python python3 ./venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt
hooks/enable_hooks
```

## Run

```bash
./app/main.py
```
