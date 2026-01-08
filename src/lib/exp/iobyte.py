from src.lib import IoByteUtil
from src.lib import IoByte

if __name__ == "__main__":

	iobyte = IoByte(32)

	print("iobyte[0]: {}".format(iobyte.bit_0))
	print("iobyte[1]: {}".format(iobyte.bit_1))
	print("iobyte[2]: {}".format(iobyte.bit_2))
	print("iobyte[3]: {}".format(iobyte.bit_3))
	print("iobyte[4]: {}".format(iobyte.bit_4))
	print("iobyte[5]: {}".format(iobyte.bit_5))
	print("iobyte[6]: {}".format(iobyte.bit_6))
	print("iobyte[7]: {}".format(iobyte.bit_7))
