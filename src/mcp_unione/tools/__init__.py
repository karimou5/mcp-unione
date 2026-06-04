from . import email, system  # add domains here as implemented


def register_all(mcp, client) -> None:
    system.register(mcp, client)
    email.register(mcp, client)
    # more domains added per task
