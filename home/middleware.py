from user_agents import parse
from .models import Track, Token
from home.functions import *
import json

class UserAgentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_agent_data = parse(user_agent)
        common_smartphone_keywords = ['iPhone', 'Android', 'BlackBerry', 'Windows Phone']
        agent_data = {
            "browser": str(user_agent_data.browser.family) + ' - ' + str(user_agent_data.browser.version_string),
            "os": str(user_agent_data.os.family) + ' - ' + user_agent_data.os.version_string,
            "mobile": user_agent_data.is_mobile,
            "tablet": user_agent_data.is_tablet,
            "touch": user_agent_data.is_touch_capable,
            "pc": user_agent_data.is_pc,
            "bot": user_agent_data.is_bot,
            "smartphone": any(keyword in user_agent for keyword in common_smartphone_keywords),
        }
        # content_type = request.META.get('CONTENT_TYPE', '').lower()
        # if 'multipart/form-data' in content_type:
        form_data = request.POST.copy()
        form_data['locate'] = str(agent_data)
        request.POST = form_data
        response = self.get_response(request)
        return response

class ModifyApiResponse:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        # print(request.headers['Authorization'].replace('Basic ','').replace('Token ',''))
        # if '/easyapi/v1/' in request.path and '/easyapi/v1/screenshot/' not in request.path and '/easyapi/v1/error-report/' not in request.path and (request.META['REQUEST_METHOD'] != 'PATCH' and '/easyapi/v1/task/' not in request.path):
        if '/easyapi/v1/' in request.path:
            # print(request.headers['Authorization'].replace('Basic ','').replace('Token ',''))
            if response is not None:
                try:
                    '''Your logic here'''
                    # print("Middleware called", request.user, request.scheme, request.META, request.META['HTTP_HOST'])
                    url = str(request.scheme)+"://"+str(request.META['HTTP_HOST'])+str(request.META['PATH_INFO'])
                    if len(request.META['QUERY_STRING']) > 1:
                        url += "?"+str(request.META['QUERY_STRING'])
                    try:
                        rqtoken = request.headers['Authorization'].replace('Basic ','').replace('Token ','')
                    except: rqtoken = "token"
                    try:
                        user = request.user
                    except:
                        try:
                            user = Token.object.get(key=rqtoken).user
                        except: user = None
                    try:
                        respons = json.dumps(response.data)
                    except: respons = {}
                    trk = Track(user=user,url=url,method=request.META['REQUEST_METHOD'], rqtoken=rqtoken, response=respons)
                    trk.save()
                except: pass
        return response