from starlette.middleware.base import BaseHTTPMiddleware
from philh_myftp_biz.text import contains
from philh_myftp_biz.terminal import Log
from urllib.parse import parse_qs
from typing import Callable
from .. import Request

class MineFartS_Middleware(BaseHTTPMiddleware):

    async def _log(self,
        logger: Callable,
        status: str
    ) -> None:
        
        # GET: Parse URL params
        params = parse_qs(self._request.url.query)

        # POST: Read Form params
        if len(params) == 0:
            ...#params = dict(await self._request.form())
        
        # Hide Sensitive info
        for name in params:
            if contains.any(name, ['password', 'token']):
                params[name] = '***'

        logger(f"""
 HOST  = {self._request.client.host}
 PATH  = {self._request.url.path}
PARAMS = {params}
METHOD = {self._request.method}
STATUS = {status}
""")
    
    async def dispatch(self, 
        request: Request, 
        call_next # pyright: ignore[reportMissingParameterType]
    ):
        
        self._request = request

        await self._log(Log.VERB, '...')

        # Process the request
        response = await call_next(request)

        # Add the allow-all-origins header directly to the response
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"

        await self._log(Log.INFO, response.status_code)

        return response
    
    async def __call__(self, *args, **kwargs): # pyright: ignore[reportMissingParameterType]
        try:
            await super().__call__(*args, **kwargs)
        except:
            Log.FAIL('', exc_info=True)

