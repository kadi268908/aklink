

# 🔗 **AKImaxLink Bot**

### ⚡ *Lightning-Fast File Sharing for Telegram*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot_API-26A5E4?logo=telegram&logoColor=white)](https://python-telegram-bot.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](./LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Required-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**Transform your files into instant shareable links • No more cluttered channels 🚀**

---

## 🚀 **Commands**
```
start - Check If Bot Is Alive Or Not
add - Add A Word To Be Removed To The List
rem - Remove A Word From The List
addsudo - Add Sudo Users Ids Who Can Use The Bot
remsudo - Remove The Sudo Ids Who Can Use The Bot
add_channel - Add A Channel Id To The Database
rem_channel - Remove A Channel Id From The Database
list_channel - to check the file to link working channels
list_word - to check the list of removing words
restart - restart the service bot
```


## 🛠️ **Installation**

### 📥 Clone the Repo
```
git clone https://github.com/SriCoolBackup/AKImaxLink && cd AKImaxLink
```

### 🐳 Install Docker -- ``https://www.docker.com/get-started``

### 🚀 Build & Run (One Command)
```
docker build -t star . && docker rm -f star 2>/dev/null || true && docker run -d -p 8080:8080 --name star star
```

### 🛑 Stop & Remove
```
docker stop Star && docker rm Star
```

### 🧹 Clean Unused Docker Data
```
docker system prune -af --volumes
```

### 📄 View Logs
```
docker logs -f Star
```

---

## 📜 **License**

**🔒 Proprietory License — All Rights Reserved**

``Proprietary License — All Rights Reserved. Copyright © 2025 AKImax. This software is licensed for personal or authorized internal use only. You are NOT allowed to copy, share, redistribute, decompile, modify, sell, or host public clones of this project without explicit written permission from the owner. You ARE allowed to use the bot privately, study its behavior, and make changes strictly for your personal, non-commercial environment. Any unauthorized distribution, commercial use, or publication of this source code is strictly prohibited and may result in legal action. See the LICENSE file for full details.``

---

## 📞 **Support**

<div align="center">

[![Issues](https://img.shields.io/badge/Issues-GitHub-black?logo=github)](https://github.com/yourusername/akimaxlink-bot/issues)
[![Telegram](https://img.shields.io/badge/Support-Telegram-26A5E4?logo=telegram)](https://t.me/yoursupport)

💬 **Need help?** Open an issue or message on Telegram!  
⭐ **Star this repo if it helped you!**

Made with ❤️ by **AKImax**

</div>
