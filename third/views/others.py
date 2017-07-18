import json
import traceback

import requests
from rest_framework.decorators import api_view

from utils.customClass import JSONResponse, InvestError
from utils.util import SuccessResponse, catchexcption, ExceptionResponse, InvestErrorResponse, checkrequesttoken


@api_view(['GET'])
def getcurrencyreat(request):
    try:
        checkrequesttoken(request)
        tcur = request.GET.get('tcur', None)
        scur = request.GET.get('scur', None)
        if not tcur or not scur:
            raise InvestError(20072)
        response = requests.get('https://sapi.k780.com/?app=finance.rate&scur=%s&tcur=%s&appkey=18220&sign=9b97118c7cf61df11c736c79ce94dcf9'% (scur, tcur)).content
        response = json.loads(response)
        if isinstance(response,dict):
            success = response.get('success',False)
            if success in ['1',True]:
                result = response.get('result',{})
            else:
                raise InvestError(code=2007,msg=response.get('msg',None))
        else:
            raise InvestError(code=2007,msg=response)
        return JSONResponse(SuccessResponse(result))
    except InvestError as err:
        return JSONResponse(InvestErrorResponse(err))
    except Exception:
        catchexcption(request)
        return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

