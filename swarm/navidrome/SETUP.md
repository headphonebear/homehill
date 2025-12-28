# Navidrome Setup Guide

## Pre-Deployment Volume Setup

Due to Docker Swarm limitations with init containers, the data volume needs manual preparation:

## One-time volume permission setup (run on deployment node):

docker run --rm
-v navidrome_navidrome_data:/data
alpine:latest
sh -c "mkdir -p /data/cache /data/backup && chown -R 2001:2001 /data && chmod -R 755 /data"

## Required Docker Secrets

Create the following secrets before deployment:

Last.fm API credentials (get from https://www.last.fm/api/account/create)

echo "your_lastfm_api_key" | docker secret create lastfm_api_key -
echo "your_lastfm_secret" | docker secret create lastfm_secret -

## Database password for navidrome user

echo "your_secure_db_password" | docker secret create navidrome_db_password -

## PostgreSQL Setup

-- Connect to PostgreSQL and create navidrome database/user
CREATE DATABASE navidrome;
CREATE USER navidrome WITH PASSWORD 'your_secure_db_password';
GRANT ALL PRIVILEGES ON DATABASE navidrome TO navidrome;

## Deployment

docker stack deploy -c navidrome-stack.yml navidrome

## Music Library Structure

- `/mnt/mk3/mk3.album` → Rock, Pop, Punk, Jazz (~1650 albums)
- `/mnt/mk3/mk3.classic` → Classical music
- `/mnt/mk3/mk3.io` → Bandcamp releases

Expected format: `album/artist/album/tracks.flac` with cover art files.