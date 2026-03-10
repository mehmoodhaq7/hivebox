"""HiveBox application configuration."""

import os

APP_VERSION = "0.0.1"

SENSEBOX_IDS = os.getenv(
    "SENSEBOX_IDS",
    "5eba5fbad46fb8001b799786,5c21ff8f919bf8001adf2488,5ade1acf223bd80019a1011c"
).split(",")