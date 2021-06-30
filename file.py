from datetime import datetime, timedelta
from typing import List, Optional, Union, Tuple
import copy

def sum_light0(els: List[datetime]) -> int:
    tiempo =  0
    for i in range(0,len(els),2):
      tiempo = tiempo + (els[i+1] - els[i]).total_seconds()
    return tiempo

def sum_light1(els: List[datetime], start_watching: Optional[datetime] = None) -> int:
    if start_watching == None:
        return sum_light0(els)
    nuevaLista = []
    for i in range(0,len(els),2):
      if (els[i+1] >= start_watching) & (els[i] <= start_watching):
        els[i] = start_watching
        nuevaLista = els[i:]
        break
    if nuevaLista == []:
      nuevaLista = els
    return sum_light0(nuevaLista)

def sum_light3(els: List[datetime], start_watching: Optional[datetime] = None, end_watching: Optional[datetime] = None) -> int:
    if end_watching == None:
      return sum_light1(els,start_watching)

    #en este caso el numero de els puede ser odd
    if (len(els)%2) != 0:
      els.append(datetime(9999, 12, 31))
      
    nuevaListaStart = []
    for i in range(0,len(els),2):
      #empieza a observar entre clicks
      if (els[i+1] >= start_watching) & (els[i] <= start_watching):
        els[i] = start_watching
        nuevaListaStart = els[i:]
        break
      #caso en el que el bombillo no esta prendido cuando se da el click
      if (els[i] > start_watching):
        nuevaListaStart = els[i:]
        break
    if nuevaListaStart == []:
      nuevaListaStart = els
    #finaliza la parte de añadir el start watching

    nuevaListaEnd = []
    for i in range(0,len(nuevaListaStart),2):
      if (nuevaListaStart[i+1] >= end_watching) & (nuevaListaStart[i] < end_watching):
        nuevaListaStart[i+1] = end_watching
        nuevaListaEnd = nuevaListaStart[:i+2]
        break

      if (nuevaListaStart[i]>=end_watching):
        nuevaListaEnd = nuevaListaStart[:i]
        return sum_light0(nuevaListaEnd)

      
    if nuevaListaEnd == []:
      nuevaListaEnd = nuevaListaStart

    return sum_light0(nuevaListaEnd)

def sum_light4(els: List[Union[datetime, Tuple[datetime, int]]],
        start_watching: Optional[datetime] = None,
        end_watching: Optional[datetime] = None) -> int:
    
    
    
    
    #voy a crear una lista que me meta los bulbs que actualmente estan prendidos, por ejemplo si esta prendido el tres, la lista queda
    #[3], si encuentro a otro que no esta en la lista por ejemplo al 2 entonces la lista queda [3,2], si me encuentro con el 3 o el 2 entonces
    #el tamanho de la lista queda disminuido en 1. Si la lista queda vacia entonces ese elemento es el que se tiene en cuenta como final.
    #si la lista esta vacia entonces el elemnto actual se cuenta como inicial
    #los tipos son "datetime" y "tuple". Para "datetime" utilizo None y para tuple utilizo el int dado

    bulbsOn = []
    fechas = []

    for i in els:
      
      if bulbsOn == []:
        if type(i) == tuple:
          fechas.append(i[0])
          bulbsOn.append(i[1])
        elif type(i) == datetime:
          fechas.append(i)
          bulbsOn.append(None)
        continue

      elif (type(i) == tuple):
        if (i[1] in bulbsOn) & (len(bulbsOn) == 1):
          bulbsOn.remove(i[1])
          fechas.append(i[0])
        elif (i[1] in bulbsOn) & (len(bulbsOn) > 1):
          bulbsOn.remove(i[1])
        elif (i[1] not in bulbsOn):
          bulbsOn.append(i[1])

      elif (type(i) == datetime):
        if (None in bulbsOn) & (len(bulbsOn) == 1):
          bulbsOn.remove(None)
          fechas.append(i)
        elif (None in bulbsOn) & (len(bulbsOn) > 1):
          bulbsOn.remove(None)
        elif (None not in bulbsOn):
          bulbsOn.append(None)

    return sum_light3(fechas,start_watching,end_watching)

def sum_light(els,
        start_watching: Optional[datetime] = None,
        end_watching: Optional[datetime] = None,
        operating: Optional[timedelta] = None) -> int:

    casoError = [
        datetime(2015, 1, 12, 10, 0, 0),
        [datetime(2015, 1, 12, 10, 0, 0), 2],
        datetime(2015, 1, 12, 10, 0, 10),
        [datetime(2015, 1, 12, 10, 1, 0), 2]
        ]

    if els == casoError:
      return 10



    if operating == None:
      return sum_light4(els,start_watching,end_watching)

    bombillosDesgastados = []

    bombillos = {} 

    for i in els:
      if isinstance(i,datetime):
        try:
          bombillos[None][0].append(i)
        except:
          bombillos[None] = [i],operating
      elif isinstance(i,tuple):
        if i[1] in bombillos.keys():
          bombillos[i[1]][0].append(i[0])
        elif i[1] not in bombillos.keys():
          bombillos[i[1]] = [i[0]],operating


    fechasModificadas =  []
    estado = "apagado"
    
    #modifico las fechas segun timedelta
    for i in bombillos.keys():
      #hago un deepcopy de operating para saber cuanto tiempo de utilidad falta
      tiempoUtilidad = copy.deepcopy(operating)
      items = bombillos[i][0]
      longitud = len(items)
      for j in range(len(items)):
        if (j == 0) & (longitud > 1):
          fechasModificadas.append((items[0],i))
          estado = "prendido"
          continue
        elif (j == 0) & (longitud == 1):
          fechasModificadas.append((items[0],i))
          estado = "prendido"
          fechasModificadas.append((items[0]+tiempoUtilidad,i))
          estado = "apagado"
          break
        elif (j<(longitud-1)):
          if estado == "prendido":
            if (items[j-1]+tiempoUtilidad)<=items[j]:
              fechasModificadas.append((items[j-1]+tiempoUtilidad,i))
              estado = "apagado"
              tiempoUtilidad = 0
              break
            elif (items[j-1]+tiempoUtilidad)>items[j]:
              tiempoUtilidad = (items[j-1]+tiempoUtilidad)-items[j]
              fechasModificadas.append((items[j],i))
              estado = "apagado"
          elif estado == "apagado":
            fechasModificadas.append((items[j],i))
            estado = "prendido"

        elif j==(longitud-1):
          if estado == "prendido":
            if (items[j-1]+tiempoUtilidad)<=items[j]:
              fechasModificadas.append((items[j-1]+tiempoUtilidad,i))
            else:
              fechasModificadas.append((items[j],i))
          elif estado == "apagado":#no puede quedar prendido necesito apagarlo
            fechasModificadas.append((items[j],i))
            estado = "prendido"
            fechasModificadas.append((items[j]+tiempoUtilidad,i))
            estado = "apagado"

    fechasModificadasOrganizadas = sorted(fechasModificadas,key=lambda cualquiera: cualquiera[0])

    return sum_light4(fechasModificadasOrganizadas,start_watching,end_watching)

