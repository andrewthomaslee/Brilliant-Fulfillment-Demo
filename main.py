#!/usr/bin/env python

if __name__ == "__main__":
    import uvicorn
    import valkey
    import pymongo
    import time

    while True:
        try:
            kv = valkey.Valkey(host="valkey")
            kv.ping()
            break
        except Exception as e:
            print(e)
            time.sleep(2)
            pass
        finally:
            print("Valkey running...")

    while True:
        try:
            client = pymongo.MongoClient(host="mongo")
            print(client.server_info())
            break
        except Exception as e:
            print(e)
            time.sleep(2)
            pass
        finally:
            print("Mongo running...")

    # FastAPI start
    # uvicorn.run(
    #     "app.app:app",
    #     host="0.0.0.0",
    #     port=7999,
    #     workers=3,
    #     timeout_graceful_shutdown=10,
    #     use_colors=True,
    # )
