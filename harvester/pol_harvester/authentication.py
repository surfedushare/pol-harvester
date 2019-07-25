from basicauth.middleware import BasicAuthMiddleware


class SearchBasicAuthMiddleware(BasicAuthMiddleware):

    def process_request(self, request):
        if request.path.startswith("/admin") or request.path.startswith("/api") or \
                request.path.startswith("/content") or request.path.startswith("/rest_framework"):
            return
        return super().process_request(request)
