from . import (  # add domains here as implemented
    domain,
    email,
    event_dump,
    project,
    suppression,
    system,
    tag,
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
    suppression.register(mcp, client)
    domain.register(mcp, client)
    event_dump.register(mcp, client)
    tag.register(mcp, client)
    project.register(mcp, client)
