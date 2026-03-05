#SNAPTUBE de SEBASWEST
#se vana usar hilos para simular cuanto se tardan en descargar ua rolas en snaptube

import threading
import time
import random
banner = (
" **** *   *   *    ****  ***** *   * ****  *****\n"
"*     **  *  * *   *   *   *   *   * *   * *    \n"
" ***  * * * *****  ****    *   *   * ****  **** \n"
"    * *  ** *   *  *       *   *   * *   * *    \n"
"****  *   * *   *  *       *    ***  ****  *****\n"
)

print(banner)
def descargar_rolon(nombre):
    print(f"iniciando la descarga de {nombre}...")
    tiempo = random.randint(2,7)
    time.sleep(tiempo)
    print(f"{nombre} descargada en {tiempo} segs.")

archivos = ["CHICHABEBA - la obsesion.mp3", "WAVES - Kanye West" , "RHINESTONE COWBOY - madvillain" ]

hilos = []

for archivo in archivos:
    hilo = threading.Thread(target= descargar_rolon, args= (archivo,))
    hilos.append(hilo)
    hilo.start()

for hilo in hilos:
    hilo.join()

print("disfruta tu musica vale")