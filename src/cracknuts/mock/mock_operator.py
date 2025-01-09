# Copyright 2024 CrackNuts. All rights reserved.import loggingimport socketimport structimport sysimport threadingfrom cracknuts import loggerfrom cracknuts.cracker import protocol, operatorfrom cracknuts.utils import hex_util_handler_dict = {}def _handler(command: int, has_payload: bool = True):    def decorator(func):        def wrapper(*args, **kwargs):            if not has_payload:                del kwargs["payload"]            return func(*args, **kwargs)        _handler_dict[command] = wrapper        return wrapper    return decoratorclass MockOperator:    def __init__(        self,        host: str = "127.0.0.1",        port: int = protocol.DEFAULT_OPERATOR_PORT,        logging_level=logging.INFO,        init_status: int = 0,    ):        self._running = False        self._status = init_status.to_bytes()        self._logger = logger.get_logger(self, logging_level)        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        self._server_socket.settimeout(1)        self._server_socket.bind((host, port))        self._server_socket.listen()        self._logger.debug("MockCracker initialized")    def start(self):        try:            self._running = True            self._start_accept()        except KeyboardInterrupt:            self._logger.debug("exist by keyboard interrupt...")            sys.exit(0)    def stop(self):        self._running = False    def _start_accept(self):        while self._running:            try:                conn, addr = self._server_socket.accept()                conn.settimeout(5)                self._logger.debug(f"Get client request from {addr}.")                threading.Thread(target=self._handle, args=(conn,), daemon=True).start()                # self._handle(conn)            except TimeoutError:                continue    def _handle(self, conn):        while self._running:            try:                header_data = conn.recv(protocol.REQ_HEADER_SIZE)                if not header_data:                    self._logger.debug("disconnected...")                    break                self._logger.debug(f"Received header:\n{hex_util.get_bytes_matrix(header_data)}")                try:                    magic, version, direction, command, rfu, length = struct.unpack(                        protocol.REQ_HEADER_FORMAT, header_data                    )                except struct.error as e:                    err_msg = f"Message format error: {e.args[0]}\n"                    self._logger.error(err_msg)                    err_res = self._error(f"Header format error: {hex_util.get_hex(header_data)}")                    self._logger.debug(f"Send error:\n{hex_util.get_bytes_matrix(err_res)}")                    conn.sendall(err_res)                    continue                self._logger.info(f"Received command: 0x{command:02X}")                self._logger.debug(                    f"Received header: Magic={magic}, Version={version}, Direction={direction}, "                    f"Command={command}, Length={length}"                )                payload_data = conn.recv(length)                if len(payload_data) > 0:                    self._logger.debug(f"Received payload:\n{hex_util.get_bytes_matrix(payload_data)}")                if command not in _handler_dict:                    self._logger.warning(f'Get command not supported: 0x{format(command, '04x')}')                    unsupported_res = self._unsupported(command)                    self._logger.debug(f"Send unsupported:\n{hex_util.get_bytes_matrix(unsupported_res)}")                    conn.sendall(unsupported_res)                    continue                func_res = _handler_dict.get(command, None)(self, payload=payload_data)                if type(func_res) is tuple:                    status, res_payload = func_res                else:                    status, res_payload = protocol.STATUS_OK, func_res                res = protocol.build_response_message(status, res_payload)                self._logger.debug(f"Sending:\n{hex_util.get_bytes_matrix(res)}")                conn.sendall(res)            except TimeoutError:                continue            except ConnectionResetError:                break            except Exception as e:                self._logger.error(e)                raise e    @staticmethod    def _error(error: str) -> bytes:        return protocol.build_response_message(protocol.STATUS_ERROR, error.encode())    @staticmethod    def _unsupported(command):        return protocol.build_response_message(            protocol.STATUS_COMMAND_UNSUPPORTED, f'Command [0x{format(command, '04x')}] not supported'.encode()        )    @_handler(operator.Command.GET_STATUS, has_payload=False)    def get_status(self) -> bytes:        return self._status    @_handler(operator.Command.START_SERVER, has_payload=False)    def start_server(self) -> bytes:        return b""    @_handler(operator.Command.STOP_SERVER, has_payload=False)    def stop_server(self) -> bytes:        return b""    @_handler(operator.Command.UPDATE_SERVER)    def update_server(self, payload: bytes) -> bytes:        self._status = b"\x01"        return b""    @_handler(operator.Command.UPDATE_BITSTREAM)    def update_bitstream(self, payload: bytes) -> bytes:        return b""    @_handler(operator.Command.GET_MODEL, has_payload=False)    def get_model(self):        return b"mock_s1"