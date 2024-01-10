from pathlib import Path
import random
from re_edge_gpt import ImageGen, ImageGenAsync

output_dir = "./Cache"
COOKIES = open("cookies.txt", "r").readlines()
COOKIE_EMAIL = {}

WORKER = {}
USAGE = {}

for i in range(len(COOKIES)):
    email, cookie = COOKIES[i].strip().replace("\n", "").split(":")
    COOKIE_EMAIL[cookie] = email
    COOKIES[i] = cookie
    WORKER[cookie] = 0
    USAGE[cookie] = 0


def get_worker():
    global WORKER, USAGE
    AVAILABLE = []
    for cookie in WORKER:
        if WORKER[cookie] == 0:
            AVAILABLE.append(cookie)

    if len(AVAILABLE) == 0:
        return None
    else:
        LEAST_USED = None
        cookie = None

        for i in AVAILABLE:
            if LEAST_USED == None:
                LEAST_USED = USAGE[i]
                cookie = i
            else:
                if USAGE[i] < LEAST_USED:
                    LEAST_USED = USAGE[i]
                    cookie = i

        WORKER[cookie] = 1
        USAGE[cookie] += 1
        return cookie


async def generate_image(promt, cookie):
    async_gen = ImageGenAsync(auth_cookie=cookie)
    image_list = await async_gen.get_images(promt, 600, 600)

    if not image_list:
        return None

    images = []
    for image in image_list:
        if not image.endswith(".svg"):
            images.append(image)
    return images


def download_images(images, id, cookie):
    sync_gen = ImageGen(auth_cookie=cookie)
    sync_gen.save_images(images, output_dir, id)

    image_path = []
    for i in range(len(images)):
        image_path.append(output_dir + "/" + str(id) + "_" + str(i) + ".jpeg")
    return image_path


Path("./Cache").mkdir(exist_ok=True)
