import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = DigitalInOut(board.D8)
pn532 = PN532_SPI(spi, cs, debug=False)
ic, ver, rev, support = pn532.firmware_version

print("Found PN532")
print("Firmware: ", ver, rev)

pn532.SAM_configuration()

while True:
	uid = pn532.read_passive_target(timeout=0.5)
	if uid:
		print("Card UID")
		print([hex(i) for i in uid])
