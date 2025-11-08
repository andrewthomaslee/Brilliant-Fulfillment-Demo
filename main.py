#!/usr/bin/env python

if __name__ == "__main__":
    import uvicorn

    # FastAPI start
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=7999,
        workers=3,
        timeout_graceful_shutdown=10,
        use_colors=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
