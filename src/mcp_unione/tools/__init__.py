from . import (  # add domains here as implemented
    email,
    system,
    template,
    validation,
    webhook,
)


def register_all(mcp, client) -> None:
    system.register(mcp, client)
    email.register(mcp, client)
    validation.register(mcp, client)
    template.register(mcp, client)
    webhook.register(mcp, client)
    # more domains added per task
