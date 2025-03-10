#!/bin/bash
gunicorn fleet:server --bind 0.0.0.0:10000