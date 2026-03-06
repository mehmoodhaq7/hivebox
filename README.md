# HiveBox 🐝

A scalable RESTful API for beekeepers using openSenseMap data.

## Version

Current version: v0.0.1

## What is HiveBox?

HiveBox fetches temperature data from beehive-mounted sensors
via openSenseMap API and exposes it through a REST API.

## SenseBox IDs Used

- 5eba5fbad46fb8001b799786
- 5c21ff8f919bf8001adf2488
- 5ade1acf223bd80019a1011c

## How to Run

### Local

```bash
pip install -r requirements.txt
python src/app.py
```

### Docker

```bash
docker build -t hivebox:0.0.1 .
docker run -p 8080:8080 hivebox:0.0.1
```

## API Endpoints

| Endpoint     | Method | Description                                 |
| ------------ | ------ | ------------------------------------------- |
| /version     | GET    | Returns current app version                 |
| /temperature | GET    | Returns average temperature from senseBoxes |

## How to Test

```bash
python -m pytest tests/ -v
```

## Project Status

- Phase 1 - Initial version with app versioning ✔️
- Phase 2 - Flask REST API + Dockerized ✔️
- Phase 3 - Unit tests, CI pipeline, Docker best practices ✔️
