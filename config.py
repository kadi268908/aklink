# ============================================================================
# Copyright (c) 2025 Star. All Rights Reserved.
# 
# PROPRIETARY AND CONFIDENTIAL
# 
# This file is part of AKImaxLink.
# 
# Unauthorized copying, distribution, modification, public display, or public 
# performance of this file, via any medium, is strictly prohibited.
# 
# For licensing information, see the LICENSE file in the root directory.
# ============================================================================

import re
import os
from os import getenv, environ
from dotenv import load_dotenv

id_pattern = re.compile(r'^.\d+$')

class Var(object):
    # Bot Information
    API_ID = int(getenv('API_ID', '8230956'))
    API_HASH = str(getenv('API_HASH', 'caef5ebd9dd9801a9cefef18acca13a9'))
    BOT_TOKEN = str(getenv('BOT_TOKEN' , '8068778009:AAEW7sWYJXoGUEbq173kjobw3-NIO7yBBgE'))
    SLEEP_THRESHOLD = int(getenv('SLEEP_THRESHOLD', '60'))

    #Channel Information
    LOG_CHANNEL = int(getenv('LOG_CHANNEL', '-1003471979568'))
    BIN_CHANNEL = int(getenv('BIN_CHANNEL', '-1003471979568'))
    
    #Database Information
    DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://LodaLasan007:LodaLasan007@cluster0.qwb3rev.mongodb.net/?appName=Cluster0")
    DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
    COLLECTION_NAME = environ.get('COLLECTION_NAME', 'StarLight')

    # Users Information
    OWNER_ID = int(os.environ.get("OWNER_ID", "1303394531"))
    
    # Multi Client Information
    MULTI_CLIENT = True
    MULTI_TOKEN1 = "8028200690:AAFo2GAjYUqJiBTyrFDQVg5e4cr1rrnoKEo"
    MULTI_TOKEN2 = "7987461036:AAHaLMRfxX25rMW4kKecvJUAV9EL5x_IJAU"
    MULTI_TOKEN3 = "8583877086:AAEtHSU3tU-yDO-Y50eJpXb1J0aQGmO3mMg"
    MULTI_TOKEN4 = "8265711069:AAH9cg3ZjHp0bh0mR3U9BM9a7i-vYIGc4Pc"
    MULTI_TOKEN5 = "8538510124:AAFIT2jwNsV_Zw6E2kAId46hH3qWTjLuqxI"
    MULTI_TOKEN6 = "8384576467:AAGobiJRCp4LOZSU_-clKceeP-Jw5veBito"
    MULTI_TOKEN7 = "8385706787:AAE_5Rkrqc2Ij1ghAZQ6BdOGkHsg63Oo5p4"
    MULTI_TOKEN8 = "8352479423:AAFUhg-st-pnktnHSPbKMb0_cfleBf0DUig"
    MULTI_TOKEN9 = "8285372064:AAECuaqC-S-FcD7_r8fRCofLd1Bu0XSPHnE"
    MULTI_TOKEN10 = "8406376363:AAFYsbmpjLO7osVhG40g-h9-AoK1MHioK5k"
    MULTI_TOKEN11 = "8496270340:AAEwTzjQ5YG6PSkf_SmCu4e5QcJHksmvY5k"
    MULTI_TOKEN12 = "8316961662:AAHTRp-ZN8D4DxITvBieum8-0r-kVoVSyaQ"
    
    # Server Information
    PORT = int(getenv('PORT', '8080'))
    NO_PORT = bool(getenv('NO_PORT', False))
    BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0'))
    IF_DM = True
    FQDN = getenv('FQDN', 'akimax.site') if IF_DM else getenv('BIND_ADDRESS', '51.15.4.146:8080')
    HAS_SSL = bool(getenv('HAS_SSL', 'False'))
    if HAS_SSL:
        URL = "https://{}/".format(FQDN)
    else:
        URL = "https://{}/".format(FQDN)
