from re_edge_gpt import ImageGen

COOKIES = open("cookies.txt", "r").readlines()
for i in range(len(COOKIES)):
    COOKIES[i] = COOKIES[i].strip().replace("\n", "")

for cookie in COOKIES:
    print(cookie.strip().replace("\n", "").split(":")[0])
    cookie = cookie.strip().replace("\n", "").split(":")[1]
    a = ImageGen(cookie)
    print(a.get_images("cat cycling on moutain"))
    print("working")
