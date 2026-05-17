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

FROM python:3.10.8

WORKDIR /app
RUN apt-get update && apt-get install -y git

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

COPY . /app/
CMD ["python", "-m", "Star"]


