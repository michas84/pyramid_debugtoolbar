from zope.interface import Interface

from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IView

from pyramid_debugtoolbar.panels import DebugPanel

_ = lambda x: x


class RoutesDebugPanel(DebugPanel):
    """
    A panel to display application routes.
    """
    name = 'Routes'
    has_content = True

    def __init__(self, request):
        self.request = request
        registry = request.registry
        self.mapper = registry.queryUtility(IRoutesMapper)
        if self.mapper is None:
            self.down = True
            self.is_active = False

    def nav_title(self):
        return _('Routes')

    def title(self):
        return _('Routes')

    def url(self):
        return ''

    def content(self):
        info = []
        mapper = self.mapper
        if mapper is not None:
            registry = self.request.registry
            routeinfo = getattr(registry, 'debugtoolbar_routeinfo', None)
            if routeinfo is None:
                routes = mapper.get_routes()
                for route in routes:
                    request_iface = registry.queryUtility(IRouteRequest,
                                                          name=route.name)
                    view_callable = None
                    if (request_iface is None) or (route.factory is not
                                                   None):
                        view_callable = '<unknown>'
                    else:
                        view_callable = registry.adapters.lookup(
                            (IViewClassifier, request_iface, Interface),
                            IView, name='', default=None)
                    predicates = []
                    for predicate in route.predicates:
                        text = getattr(predicate, '__text__', repr(predicate))
                        predicates.append(text)
                    info.append({'route':route,
                                 'view_callable':view_callable,
                                 'predicates':', '.join(predicates)})
                registry.debugtoolbar_routeinfo = info
                
            vars = {
                'routes': registry.debugtoolbar_routeinfo,
                }
            return self.render(
                'pyramid_debugtoolbar.panels:templates/routes.jinja2',
                vars, self.request)
        return ''
