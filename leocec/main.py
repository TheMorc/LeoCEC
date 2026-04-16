import os
import asyncio
import serial
import time
from concurrent.futures import ThreadPoolExecutor
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method

class CECService:
    def __init__(self):
        self.serial = None
        self.state = "off"
        self.last_off_time = 0
        self.serial_executor = ThreadPoolExecutor(max_workers=1)
        self.poll_executor = ThreadPoolExecutor(max_workers=1)
        self.loop = None
        self.pollingLineCount = 0

    def init_serial(self):
        self.serial = serial.Serial(
            port=os.getenv("LEOCEC_PORT", ""),
            baudrate=500000,
            timeout=0.1,
        )

    def power(self, mode):
        if mode:
            return self._send("1")
        else:
            return self._send("0")

    def status(self):
        return self._send("2")

    def toggle(self):
        if self.state == "on":
            self.power(False)
            self.state = "transition"
        else:
            self.power(True)
            self.state = "transition"

        return self.state

    def _send(self, msg: str):
        if self.serial:
            self.serial.write((msg).encode())
        return f"[LeoCEC] --> {msg}"

    async def _serial_loop(self):
        while True:
            try:
                line = await asyncio.to_thread(self.serial.readline)
                if not line:
                    continue
                self._handle_serial(line.decode("utf-8", errors="ignore").strip())
                self.pollingLineCount = self.pollingLineCount + 1
                self.last_off_time = time.time();

            except Exception as e:
                print("[uart kaput]", e)

    def _uart_message_handler(self, line):
        if "0f:85 [Request Active Source]" in line:
            self.state = "on"
        elif "Standby" in line:
            self.state = "off"
            self.last_off_time = time.time()

    def _handle_serial(self, line: str):
        print("[uart]", line)
        self._uart_message_handler(line)

    async def _poll_loop(self):
        while True:
            await asyncio.sleep(5)
            print("[LeoCEC] previous state:", self.state)
            if self.pollingLineCount == 0:
                self.state = "off"
            else:
                if "transition" not in self.state:
                    self.state = "on"

            print("[LeoCEC] current state:", self.state)

            if time.time() - self.last_off_time < 15:
                continue

            self.pollingLineCount = 0
            self.status()

    async def main_loop(self):
        self._tasks = [
            asyncio.create_task(self._serial_loop()),
            asyncio.create_task(self._poll_loop()),
        ]
        await asyncio.gather(*self._tasks)

class CECDBus(ServiceInterface):
    def __init__(self, service: CECService):
        super().__init__("com.LeoCEC.control")
        self.service = service

    @method()
    def Toggle(self) -> "s":
        return self.service.toggle()

    @method()
    def On(self) -> "s":
        return self.service.power(True)

    @method()
    def Off(self) -> "s":
        return self.service.power(False)

    @method()
    def Status(self) -> "s":
        return self.service.status()


async def main():
    service = CECService()
    service.init_serial()

    bus = await MessageBus().connect()
    iface = CECDBus(service)
    bus.export("/com/LeoCEC/control", iface)
    await bus.request_name("com.LeoCEC.control")

    print("[LeoCEC] DBus service running")
    await service.main_loop()

