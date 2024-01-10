from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
import asyncio
from config import MONGOURI

db = MongoClient(MONGOURI)["bingbot"]
usersdb = db.users
groupsdb = db.groups
statusdb = db.status

USERS = {}
GROUPS = {}
STATUS = []
APPROVED = []


async def DBUpdater():
    global USERS, GROUPS, STATUS, APPROVED

    print("[INFO]: Initializing Database Updater...")

    async for user in usersdb.find():
        USERS[user["userid"]] = [user.get("gen", 0), user.get("img", 0)]

    async for group in groupsdb.find():
        GROUPS[group["groupid"]] = [group.get("gen", 0), group.get("img", 0)]

    x = await statusdb.find_one({"status": "generation status"})
    STATUS.append(x.get("gen", 0))
    STATUS.append(x.get("img", 0))
    APPROVED = x.get("approved", [])

    print("[INFO]: Database Updater Initialized Successfully!")

    Ucache = USERS.copy()
    Gcache = GROUPS.copy()

    while True:
        await asyncio.sleep(60)

        for user in USERS:
            if user in Ucache:
                if USERS[user] != Ucache[user]:
                    await usersdb.update_one(
                        {"userid": user},
                        {"$set": {"gen": USERS[user][0], "img": USERS[user][1]}},
                        upsert=True,
                    )
            else:
                await usersdb.update_one(
                    {"userid": user},
                    {"$set": {"gen": USERS[user][0], "img": USERS[user][1]}},
                    upsert=True,
                )

            Ucache[user] = USERS[user]

        for group in GROUPS:
            if group in Gcache:
                if GROUPS[group] != Gcache[group]:
                    await groupsdb.update_one(
                        {"groupid": group},
                        {"$set": {"gen": GROUPS[group][0], "img": GROUPS[group][1]}},
                        upsert=True,
                    )
            else:
                await groupsdb.update_one(
                    {"groupid": group},
                    {"$set": {"gen": GROUPS[group][0], "img": GROUPS[group][1]}},
                )

            Gcache[group] = GROUPS[group]

        await statusdb.update_one(
            {"status": "generation status"},
            {"$set": {"gen": STATUS[0], "img": STATUS[1]}},
            upsert=True,
        )


async def addApproved(userid):
    global APPROVED

    if userid not in APPROVED:
        APPROVED.append(userid)

    await statusdb.update_one(
        {"status": "generation status"},
        {"$set": {"approved": APPROVED}},
        upsert=True,
    )


def isApproved(userid):
    global APPROVED

    if userid in APPROVED:
        return True
    else:
        return False


TASKS_DONE = {}
from datetime import datetime
from config import MAX_GEN


def getLimitedUsers():
    global TASKS_DONE
    today = str(datetime.today().date())

    limited_users = []

    for user in TASKS_DONE:
        if today in TASKS_DONE[user]:
            if TASKS_DONE[user][today] >= MAX_GEN:
                limited_users.append(user)

    return limited_users


def addTaskDone(userid):
    global TASKS_DONE
    today = str(datetime.today().date())

    if userid in TASKS_DONE:
        if today in TASKS_DONE[userid]:
            TASKS_DONE[userid][today] += 1
        else:
            TASKS_DONE[userid][today] = 1
    else:
        TASKS_DONE[userid] = {today: 1}


def getTasksDone(userid):
    if isApproved(userid):
        return 0

    global TASKS_DONE
    today = str(datetime.today().date())

    if userid in TASKS_DONE:
        if today in TASKS_DONE[userid]:
            return TASKS_DONE[userid][today]
        else:
            return 0
    else:
        return 0


def addGenStatus(user, group, imgs):
    global USERS, GROUPS, STATUS

    if user in USERS:
        USERS[user][0] += 1
        USERS[user][1] += imgs
    else:
        USERS[user] = [1, imgs]

    if user != group:
        if group in GROUPS:
            GROUPS[group][0] += 1
            GROUPS[group][1] += imgs
        else:
            GROUPS[group] = [1, imgs]

    STATUS[0] += 1
    STATUS[1] += imgs
    addTaskDone(user)


def addUserGroup(user, group):
    global USERS, GROUPS

    if user not in USERS:
        USERS[user] = [0, 0]
    if user != group:
        if group not in GROUPS:
            GROUPS[group] = [0, 0]


def getStatusData():
    global STATUS, USERS, GROUPS

    TOTAL_GEN = STATUS[0]
    TOTAL_IMG = STATUS[1]
    TOTAL_USERS = len(USERS)
    TOTAL_GROUPS = len(GROUPS)

    return TOTAL_GEN, TOTAL_IMG, TOTAL_USERS, TOTAL_GROUPS
