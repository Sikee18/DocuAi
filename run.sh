#!/bin/bash

# Start Reflex services in background
reflex run --env prod &

# Start Caddy in foreground to proxy traffic
caddy run --config Caddyfile
