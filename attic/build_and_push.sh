#!/usr/bin/env bash
docker build . -t registry.digitalocean.com/nka/oddipedia:latest
docker push registry.digitalocean.com/nka/oddipedia:latest

