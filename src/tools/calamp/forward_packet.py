# ======================================================================================================================
# Copyright (c) 2013 Exzigo. All rights reserved.
#
# Author: Sean Kerr [sean@code-box.org]
# ======================================================================================================================

if __name__ != "__main__":
    raise Exception("This is a shell script and cannot be imported")

import ForwardWorker
import UDPServer

UDPServer(ForwardWorker, "NINO")