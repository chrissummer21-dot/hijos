import requests
import json
import time

# =========================
# CONFIGURACIÓN
# =========================

GROUP_ID = 456998661  # TU GROUP ID
TARGET_ROLE = "Hijos del Jefe"

ROBLOSECURITY = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhADIhwKBGR1aWQSFDE0MTUyMTk1NzM3MTA0Mzk5MDU5KAM.b-qwVcuTdzpZ7kg-ztGKRnpur5w2KF2usEZ0jnzbLVt3_CcMcRtE-CseGZ7YeUkgRGYmsYp--6X5X4pEOKyUiSqrZWiU-NUpWaKUfDc4HqQes3I6onpBYky8SAMmHBHoe0zr6XltSMbGwbWbaLw1AyKG0eLOKq441OcqaX_AYfhnISaty1lt7aEH02B0EQtK_cQnDYKTZCkwSqm8f_cv4RQUCIkkUFgbl8o_jS75nSJp_yjDvNmcmwhGl2nO2AgLUMqgKe8VPGLyKrAdhRK25Ke767NA3jf9H6XLxqre8VjB-Qr252v7ShvZ7vuPR2GL99HJpc_SmFPdEbDMFJifjnQ0vIAd6Oj03mNdbvKv59Y-ennNBE1wqRYgN0iiLsuQFMcteop9G8K1TFIuzZFQ2XdDUOBKSLYj-ukFg2jCQqBOAg0Ex753hozFB21pbjPqzgn7TaLKvxcb3dsuQmktAIwS_qqyPsopG51tItHNdDlNUfRAaWca10EDXgp3TQeLzTgBf_vletngAXEAt714JT0yop1U1nS-72IxlnkeYYmatXV972r9xH77ZKRNEKxByApWrBR4gmw7wSUuI-9Q-NK2W47rIB6BP9t767Zl35C0Xp_xF7v31_jBJfk2d0Pf0Ttlh_uRcWzzk6X2JKQM6TkgE59wNwpp-y5DpLcAGyf7ie19cJ76VrVApp3mP7vLzcQy-p-LSZInL95Rmu26pig9cP1YJQVbh5FjV9-fEDXlLYX2aV4ta8UgKPppjey0DXsA8CK2T9EUfN4dRKcV_bEaLzA"  # TU COOKIE

OUTPUT_JSON = "overlay_data.json"

# =========================
# SESIÓN AUTENTICADA
# =========================

session = requests.Session()

session.cookies[".ROBLOSECURITY"] = ROBLOSECURITY

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# obtener csrf automáticamente
def get_csrf():
    r = session.post("https://auth.roblox.com/v2/logout")
    return r.headers.get("x-csrf-token")

headers["X-CSRF-TOKEN"] = get_csrf()

# =========================
# OBTENER MIEMBROS
# =========================

def obtener_miembros():

    miembros = []
    cursor = None

    while True:

        url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/users?limit=100"

        if cursor:
            url += f"&cursor={cursor}"

        res = session.get(url, headers=headers)

        if res.status_code != 200:
            print("ERROR:", res.status_code, res.text)
            return []

        data = res.json()

        for user in data["data"]:

            if user["role"]["name"] == TARGET_ROLE:

                miembros.append(user["user"]["userId"])
                print("Encontrado:", user["user"]["username"])

        cursor = data["nextPageCursor"]

        if not cursor:
            break

        time.sleep(0.2)

    return miembros


# =========================
# AVATAR + DISPLAYNAME
# =========================

def obtener_info(user_ids):

    res1 = session.post(
        "https://users.roblox.com/v1/users",
        headers=headers,
        json={"userIds": user_ids}
    )

    res2 = session.get(
        "https://thumbnails.roblox.com/v1/users/avatar-headshot",
        headers=headers,
        params={
            "userIds": ",".join(map(str,user_ids)),
            "size": "420x420",
            "format": "Png",
            "isCircular": "true"
        }
    )

    display = {u["id"]: u["displayName"] for u in res1.json()["data"]}
    avatars = {a["targetId"]: a["imageUrl"] for a in res2.json()["data"]}

    resultado = []

    for uid in user_ids:

        resultado.append({

            "displayName": display.get(uid, ""),
            "avatar": avatars.get(uid, "")

        })

    return resultado


# =========================
# EJECUCIÓN
# =========================

print("Obteniendo miembros con cookie...")

ids = obtener_miembros()

if not ids:
    print("No se encontró nadie con ese rango.")
    exit()

print("Obteniendo avatars...")

data = obtener_info(ids)

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("JSON generado:", OUTPUT_JSON)


import http.server
import socketserver
import threading

PORT = 8000

def iniciar_servidor():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Servidor iniciado en http://localhost:{PORT}/overlay.html")
        httpd.serve_forever()

threading.Thread(target=iniciar_servidor, daemon=True).start()

input("Presiona ENTER para cerrar el servidor...\n")