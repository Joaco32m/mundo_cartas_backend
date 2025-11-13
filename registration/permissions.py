from rest_framework import permissions

class EsAdmin(permissions.BasePermission):
   

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        perfil = getattr(user, 'perfilusuario', None)
        if perfil and perfil.rol:
            return perfil.rol.nombre.lower() == "administrador"
        return False


class EsVendedor(permissions.BasePermission):
    

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        perfil = getattr(user, 'perfilusuario', None)
        if perfil and perfil.rol:
            return perfil.rol.nombre.lower() in ["vendedor", "administrador"]
        return False
