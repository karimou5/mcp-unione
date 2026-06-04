from .server import build_server


def main() -> None:
    build_server().run()  # stdio by default


if __name__ == "__main__":
    main()
