from rest_framework import permissions
from registration.models import PerfilUsuario

class IsVendedor(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        try:
            perfil = PerfilUsuario.objects.get(user=user)
        except PerfilUsuario.DoesNotExist:
            return False
        return perfil.rol and perfil.rol.nombre == "Vendedor"
