#!/usr/bin/env python
# coding:utf-8

import logging
import re
import traceback
from contextlib import contextmanager
from pprint import pprint

from ldap3 import Connection, Server, ALL, LEVEL

