# Distributed file compression service

## Technologies

1. Python (Flask)
2. Kafka
3. Docker
4. ffmpeg
5. minio

## Usage

### setup env variables

```bash
cp ./backend/.env.example ./backend/.env
```

```bash
cp ./video-compressor/.env.example ./video-compressor/.env
```

### run the containers

```bash
docker compose up -d # or make u
```

### Upload videos

A react app is running in http://localhost:5173

## Licence

Apache
