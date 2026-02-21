import sys, os, traceback
sys.path.insert(0, os.getcwd())

try:
    from app.main import app
except Exception:
    traceback.print_exc()
    raise

import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='debug')
