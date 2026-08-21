"""Mock ของไลบรารี network สำหรับรันโค้ด Part VI แบบ offline

ติดตั้งเข้า sys.modules ก่อนบล็อกโค้ดจะ import
ครอบคลุม: websockets · aiohttp · requests
ทุกตัวคืนข้อมูลจำลองรูปแบบเดียวกับของจริง แล้วปิดตัวเองหลังส่งไม่กี่ข้อความ
เพื่อไม่ให้ลูป `while True` ค้าง
"""
import asyncio
import json
import sys
import types

MAX_MSGS = 3          # ส่งกี่ข้อความก่อนปิด stream
_closed_after = {}


# ─────────────────────────── websockets ───────────────────────────
class _WSException(Exception):
    pass


class _ConnectionClosed(_WSException):
    def __init__(self, code=1000, reason="mock closed"):
        self.code, self.reason = code, reason
        super().__init__(f"{code} {reason}")


def _binance_kline(i):
    base = 65000 + i * 12.5
    return json.dumps({
        "e": "kline", "E": 1705123456789 + i * 1000, "s": "BTCUSDT",
        "k": {"t": 1705123400000 + i * 60000, "T": 1705123459999 + i * 60000,
              "s": "BTCUSDT", "i": "1m", "o": f"{base:.2f}", "c": f"{base + 5:.2f}",
              "h": f"{base + 9:.2f}", "l": f"{base - 4:.2f}", "v": "12.5",
              "x": i % 2 == 0, "q": "812345.6"},
    })


def _bybit_kline(i):
    base = 65010 + i * 11.0
    return json.dumps({
        "topic": "kline.1.BTCUSDT", "ts": 1705123456789 + i * 1000, "type": "snapshot",
        "data": [{"start": 1705123400000 + i * 60000, "interval": "1",
                  "open": f"{base:.2f}", "close": f"{base + 4:.2f}",
                  "high": f"{base + 8:.2f}", "low": f"{base - 3:.2f}",
                  "volume": "11.1", "turnover": "722345.6", "confirm": i % 2 == 0,
                  "timestamp": 1705123456789 + i * 1000}],
    })


class _MockWS:
    def __init__(self, url):
        self.url, self._i = url, 0
        self._bybit = "bybit" in url.lower()

    async def send(self, data):        # subscribe message
        await asyncio.sleep(0)

    async def recv(self):
        if self._i >= MAX_MSGS:
            raise _ConnectionClosed(1000, "mock stream finished")
        msg = (_bybit_kline if self._bybit else _binance_kline)(self._i)
        self._i += 1
        await asyncio.sleep(0.01)
        return msg

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.recv()
        except _ConnectionClosed:
            raise StopAsyncIteration

    async def close(self):
        await asyncio.sleep(0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        await asyncio.sleep(0)


class _Connect:
    def __init__(self, url, **kw):
        self.url = url

    def __await__(self):
        async def go():
            return _MockWS(self.url)
        return go().__await__()

    async def __aenter__(self):
        return _MockWS(self.url)

    async def __aexit__(self, *a):
        await asyncio.sleep(0)


websockets = types.ModuleType("websockets")
websockets.connect = lambda url, **kw: _Connect(url, **kw)
_wsexc = types.ModuleType("websockets.exceptions")
_wsexc.ConnectionClosed = _ConnectionClosed
_wsexc.WebSocketException = _WSException
_wsexc.ConnectionClosedError = _ConnectionClosed
websockets.exceptions = _wsexc
sys.modules["websockets"] = websockets
sys.modules["websockets.exceptions"] = _wsexc


# ─────────────────────────── aiohttp ───────────────────────────
def _rest_payload(url):
    u = url.lower()
    if "ticker" in u or "price" in u:
        return {"symbol": "BTCUSDT", "price": "65123.45", "lastPrice": "65123.45",
                "retCode": 0, "result": {"list": [{"symbol": "BTCUSDT",
                                                   "lastPrice": "65123.45"}]}}
    if "order" in u:
        return {"orderId": "mock-1", "status": "FILLED", "executedQty": "0.01",
                "retCode": 0, "result": {"orderId": "mock-1", "orderStatus": "Filled"}}
    if "klines" in u or "kline" in u:
        return [[1705123400000, "65000", "65100", "64950", "65050", "12.5"]]
    return {"ok": True, "retCode": 0, "result": {}}


class _Resp:
    def __init__(self, url):
        self.url, self.status = url, 200
        self.headers = {"Content-Type": "application/json",
                        "X-MBX-USED-WEIGHT-1M": "12"}

    async def json(self, **kw):
        await asyncio.sleep(0)
        return _rest_payload(self.url)

    async def text(self):
        await asyncio.sleep(0)
        return json.dumps(_rest_payload(self.url))

    def raise_for_status(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        await asyncio.sleep(0)


class _Session:
    def __init__(self, *a, **kw):
        self.closed = False

    def get(self, url, **kw):
        return _Resp(url)

    def post(self, url, **kw):
        return _Resp(url)

    def ws_connect(self, url, **kw):
        return _Connect(url)

    async def close(self):
        self.closed = True
        await asyncio.sleep(0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        await self.close()


aiohttp = types.ModuleType("aiohttp")
aiohttp.ClientSession = _Session
aiohttp.ClientTimeout = lambda **kw: types.SimpleNamespace(**kw)
aiohttp.ClientError = Exception
aiohttp.ClientResponseError = Exception
aiohttp.TCPConnector = lambda **kw: object()
sys.modules["aiohttp"] = aiohttp


# ─────────────────────────── requests ───────────────────────────
class _RResp:
    def __init__(self, url):
        self.url, self.status_code, self.text = url, 200, ""
        self.headers = {"Content-Type": "application/json"}
        self.text = json.dumps(_rest_payload(url))

    def json(self):
        return _rest_payload(self.url)

    def raise_for_status(self):
        pass


requests = types.ModuleType("requests")
requests.get = lambda url, **kw: _RResp(url)
requests.post = lambda url, **kw: _RResp(url)
requests.Session = lambda: types.SimpleNamespace(
    get=lambda url, **kw: _RResp(url), post=lambda url, **kw: _RResp(url))
requests.exceptions = types.SimpleNamespace(RequestException=Exception,
                                            Timeout=TimeoutError)
sys.modules["requests"] = requests
