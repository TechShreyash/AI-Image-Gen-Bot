# AI Image Generator Bot

AI Image Generator Bot Using Bing Image Generator

## Features

- Multiple Accounts Support
- User Queue System
- Limit No. of Generations Per User
- Advanced Statistics
- Owner Can Approve User To Use Bot Without Limits
- Users Can Request For Approval By Sending Their Account Email And Password To Owner
- Owner Can Send Message To User

## Setup

1. Install All Requirements
```bash
pip install -U -r requirements.txt
```

2. Add Your Config Vars in `config.py`

3. Add Your Microsoft Account Email and Password in `accounts.txt`

4. Add Your Account Cookies in `cookies.txt`

> Follow Steps Given Here : https://github.com/Integration-Automation/ReEdgeGPT?tab=readme-ov-file#getting-authentication

> Note : In order for the bot to work, you need to generate one image manually first from https://www.bing.com/images/create

5. Check If All Cookies Are Working or Not
```bash
python cookieChecker.py
```

6. Run The Bot
```bash
python bot.py
```

### Run On Docker

1. Follow Steps 1-5 From Above

2. Install Docker
```bash
bash installDocker.sh
```

3. Build/Run/Update Docker App
```bash
bash runDocker.sh
```

## Commands

- `/start` : Start The Bot
- `/help` : Show Help Message
- `/gen query` : Generate Image
- `/stats` : Show Stats
- `/add userid` : Remove limits of a user (Owner Only)
- `/send userid message` : Send Message To User (Owner Only)
- `/limited` : Show Limited Users (Owner Only)
- `/activate` : Request For Removal Of Limits