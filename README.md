# migrate-mtlynch-to-hugo

[![CircleCI](https://circleci.com/gh/mtlynch/migrate-mtlynch-to-hugo.svg?style=svg)](https://circleci.com/gh/mtlynch/migrate-mtlynch-to-hugo)

## Overview

Scripts to migrate the Jekyll version of mtlynch.io to Hugo.

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
