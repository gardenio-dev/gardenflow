from abc import ABC

from gardenflow.core.services import Service


class TenantService(Service, ABC):
    """Base class for tenant-aware services."""

    def __init__(self, tenant: str):
        """Create a new instance."""
        self._tenant = tenant

    @property
    def tenant(self) -> str:
        """Get the tenant ID."""
        return self._tenant
