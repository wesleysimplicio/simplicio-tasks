#!/usr/bin/env node
'use strict';

const { ensureAndRun } = require('../lib/python-shim');

ensureAndRun({
  packageName: 'simplicio-loop',
  version: '3.15.0',
  entrypoint: 'simplicio-loop',
  args: process.argv.slice(2),
});
