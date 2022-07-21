class URL():

    def __init__(self, scheme: str, host: str, port: int):
        self._scheme = scheme
        self._host = host
        self._port = port

    # Getters

    @property
    def scheme(self) -> str:
        """URL scheme."""
        return self._scheme

    @property
    def host(self) -> str:
        """URL host."""
        return self._host

    @property
    def port(self) -> int:
        """URL port."""
        return self._port

    @property
    def server_address(self) -> tuple[str, int]:
        """Python HTTPServer compatible address.

        Contains the host and the port.
        """
        return (self.host, self.port)
