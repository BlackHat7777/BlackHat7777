# Render uploader demo

Endpoints:
- POST /upload (Bearer token, form file field `file`)
- GET /files (Bearer token)
- GET /files/<filename> (Bearer token)

Set environment variables on Render:
- SECRET_TOKEN (your token)
- STORAGE_PATH (e.g. /data/uploads)
