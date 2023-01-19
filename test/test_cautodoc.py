#!/usr/bin/env python3
# Copyright (c) 2018, Jani Nikula <jani@nikula.org>
# Licensed under the terms of BSD 2-Clause, see LICENSE for details.

import os
import shutil

import pytest
from sphinx_testing import with_app

from test import testenv

def _get_suffix(buildername):
    return 'txt' if buildername == 'text' else buildername

def _get_output(testcase, app, status, warning):
    input_filename = testcase.get_input_filename()
    shutil.copyfile(input_filename,
                    os.path.join(app.srcdir, os.path.basename(input_filename)))

    directive_str = testcase.get_directive_string()

    with open(os.path.join(app.srcdir, 'index.rst'), 'w') as f:
        f.write(directive_str)

    # Hack: It's not possible to disable search via configuration
    app.builder.search = False

    app.build()

    output_suffix = _get_suffix(app.builder.name)
    output_filename = os.path.join(app.outdir, f'index.{output_suffix}')

    return testenv.read_file(output_filename), None

def _get_expected(testcase, app, status, warning):
    shutil.copyfile(testcase.get_expected_filename(),
                    os.path.join(app.srcdir, 'index.rst'))

    # Hack: It's not possible to disable search via configuration
    app.builder.search = False

    app.build()

    output_suffix = _get_suffix(app.builder.name)
    output_filename = os.path.join(app.outdir, f'index.{output_suffix}')

    return testenv.read_file(output_filename), None

class ExtensionTextTestcase(testenv.Testcase):
    pass

class ExtensionHtmlTestcase(testenv.Testcase):
    pass

def _get_text_testcases(path):
    for f in testenv.get_testcase_filenames(path):
        yield ExtensionTextTestcase(f)

def _get_html_testcases(path):
    for f in testenv.get_testcase_filenames(path):
        yield ExtensionHtmlTestcase(f)

# Test using Sphinx plain text builder
@with_app(confdir=testenv.testdir, create_new_srcdir=True, buildername='text')
def _get_output_text(testcase, app, status, warning, **unused):
    return _get_output(testcase, app, status, warning)

@with_app(confdir=testenv.testdir, create_new_srcdir=True, buildername='text')
def _get_expected_text(testcase, app, status, warning, **unused):
    return _get_expected(testcase, app, status, warning)

@pytest.mark.parametrize('testcase', _get_text_testcases(testenv.testdir),
                         ids=testenv.get_testid)
def test_directive_text(testcase):
    testcase.run_test(_get_output_text, _get_expected_text)

# Test using Sphinx html builder
@with_app(confdir=testenv.testdir, create_new_srcdir=True, buildername='html')
def _get_output_html(testcase, app, status, warning, **unused):
    return _get_output(testcase, app, status, warning)

@with_app(confdir=testenv.testdir, create_new_srcdir=True, buildername='html')
def _get_expected_html(testcase, app, status, warning, **unused):
    return _get_expected(testcase, app, status, warning)

@pytest.mark.full
@pytest.mark.parametrize('testcase', _get_html_testcases(testenv.testdir),
                         ids=testenv.get_testid)
def test_directive_html(testcase):
    testcase.run_test(_get_output_html, _get_expected_html)
