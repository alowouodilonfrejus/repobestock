"""Matrice RBAC : chaque role ne voit que ce qui lui revient."""

from app.core.permissions import is_superadmin, role_has, role_permissions
from app.models.user import UserRole


def test_superadmin_has_everything():
    for perm in ("users:read", "stock:write", "dashboard:view", "moi:read"):
        assert role_has(UserRole.SUPERADMIN, perm)
    assert is_superadmin(UserRole.SUPERADMIN)


def test_admin_cannot_manage_users():
    assert not role_has(UserRole.ADMIN, "users:read")
    assert not role_has(UserRole.ADMIN, "users:validate")
    assert role_has(UserRole.ADMIN, "stock:write")
    assert not is_superadmin(UserRole.ADMIN)


def test_manager_is_read_only():
    assert role_has(UserRole.MANAGER, "stock:read")
    assert not role_has(UserRole.MANAGER, "stock:write")
    assert not role_has(UserRole.MANAGER, "affectations:write")
    assert not role_has(UserRole.MANAGER, "employes:write")


def test_employe_is_personal_scope_only():
    assert role_has(UserRole.EMPLOYE, "moi:read")
    assert not role_has(UserRole.EMPLOYE, "stock:read")
    assert not role_has(UserRole.EMPLOYE, "dashboard:view")


def test_role_permissions_front_payload():
    superadmin_perms = role_permissions(UserRole.SUPERADMIN)
    assert "*" not in superadmin_perms
    assert {"users:read", "users:validate", "stock:write"} <= superadmin_perms

    admin_perms = role_permissions(UserRole.ADMIN)
    assert "users:read" not in admin_perms
    assert "stock:write" in admin_perms

    assert role_permissions(UserRole.EMPLOYE) == {"moi:read"}


def test_unknown_permission_denied_by_default():
    for role in UserRole:
        assert not role_has(role, "inconnue:read") or is_superadmin(role)
