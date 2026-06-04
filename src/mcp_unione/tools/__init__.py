from . import email, system, template, validation  # add domains here as implemented


def register_all(mcp, client) -> None:
    system.register(mcp, client)
    email.register(mcp, client)
    validation.register(mcp, client)
    template.register(mcp, client)
    # more domains added per task
