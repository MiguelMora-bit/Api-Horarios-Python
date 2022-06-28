import datetime
import calendar
import requests
import random
from flask import Flask, jsonify

app = Flask(__name__)

def dataBase():
    estandarData = {}
    resp = requests.get(process.env.URL)
    data = resp.json()
    for dato in data:
        estandarData.setdefault(dato["NumeroEmpleado"], dato)
    return estandarData

def datosEmpleadosTienda(empleadosTien):
    datos = dataBase()
    empleados = []
    for empleado in empleadosTien:
        empleados.append(datos[empleado])
    return empleados

def obtenerTiendas():
    datos = dataBase()

    numerosEmpleados = []
    tiendas = []

    for i in datos:
        numerosEmpleados.append(i)

    for i in numerosEmpleados:
        if not(datos[i]["Tienda"].strip() in tiendas):
            tiendas.append(datos[i]["Tienda"].strip())

    return tiendas, numerosEmpleados

def obtenerGerentes(idGerente):
    datos = dataBase()
    idGerente = int(idGerente)
    gerentes = []
    for empleado in datos:
        if datos[empleado]["Puesto"].startswith("GT"):
            gerentes.append(empleado)

    if idGerente in gerentes:
        return datos[idGerente]

def empleadosTienda(tienda, numeroEmpleados):
    datos = dataBase()
    empleados = []
    for numero in numeroEmpleados:
      if (tienda.strip() == datos[numero]["Tienda"].strip()):
        empleados.append(numero)
    return empleados

def puestosEmpleados(empleadosTienda):
    datos = dataBase()
    #Obtener los puestos de la tienda
    puestos = []
    for empleado in empleadosTienda:
        puestos.append(datos[empleado]["Puesto"].strip())
    return puestos

def diasDelMes():
    fecha = datetime.date.today()
    monthRange = calendar.monthrange(fecha.year , fecha.month)
    dia,dias = monthRange
    return dia, dias

def diasLetra(dia, dias):
    fecha = datetime.date.today()

    diasSemana = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

    diasNumero = []
    diasNombre = []
    for i in range(dias):
        if dia == 7:
            dia = 0
        diasNumero.append(i+1)
        diasNombre.append(diasSemana[dia])
        dia += 1

    if fecha.day >= 15:
        diasNumero = diasNumero[15:]
        diasNombre = diasNombre[15:]
    else:
        diasNumero = diasNumero[:15]
        diasNombre = diasNombre[:15]

    return diasNumero, diasNombre

def alertaPrimeraCondicion():
    return ("No es posible operar con menos de 5 personas solicita a tu gerente de distrito movimiento de personal de otra tienda.")

def alertaSegundaCondicion():
    return ("Falta personal administrativo solicita movimiento de personal o autorización de horas extras para cubrir los descansos.")

def primerCondicion(empleadosTienda):
    # 4 personas o menos ---> no es posible operar con menos de 5 personas solicita a tu gerente de distrito movimiento de personal de otra tienda.

   return len(empleadosTienda) >= 5

def segundaCondicion(puestoEmpleados):
    #Cantidad de 1 Gt y 1 TR --- > Falta personal administrativo solicita movimiento de personal o autorización de horas extras para cubrir los descansos.
    numeroGerentes = 0
    numeroTr = 0
    for puesto in puestoEmpleados:
        if puesto.startswith('GT'):
            numeroGerentes += 1

        if puesto.startswith("TR"):
            numeroTr += 1

    return numeroGerentes >= 1 and numeroTr >= 2

def conteoEmpleados(empleadosTienda, estandarDataPlantilla):
    datos = estandarDataPlantilla
    empleadosGt = []
    empleadosTr = []
    empleadosFt = []
    empleadosPt = []

    for empleado in empleadosTienda:
        if "GT" in datos[empleado]["Puesto"]:
            empleadosGt.append(empleado)
        if "FT" in  datos[empleado]["Puesto"]:
            empleadosFt.append(empleado)
        if "TR" in datos[empleado]["Puesto"]:
            empleadosTr.append(empleado)
        if "PT" in datos[empleado]["Puesto"]:
            empleadosPt.append(empleado)

    return (empleadosGt, empleadosPt, empleadosFt, empleadosTr)

def generarHorario(diasDelMesNombre, diasNumero, diasDescansoLetra, estandarDataPlantilla, diasPedido, prioridadTurnos):

    respuestaLista = []
    respuestaJson = {}

    for i in range(len(diasDelMesNombre)):

        diaNumero = diasNumero[i]

        descansosPorDia = [0, 0, 0, 0, 0]

        empleadosTienda = []

        empleadosStatusVacaciones = []
        empleadosStatusIncapacidad = []
        empleadosStatusPtr = []

        empleadosVacaciones = []
        empleadosIncapacidad = []

        # Para los empleados con estatus distinto a activo

        for empleado in estandarDataPlantilla:
            if (estandarDataPlantilla[empleado]["estado"] == "Vacaciones"):
                empleadosStatusVacaciones.append(empleado)
            elif (estandarDataPlantilla[empleado]["estado"] == "Incapacidad"):
                empleadosStatusIncapacidad.append(empleado)
            elif (estandarDataPlantilla[empleado]["estado"] == "Ptr"):
                empleadosStatusPtr.append(empleado)
            else:
                empleadosTienda.append(empleado)

        # Comprobar si el empleado sigue de vacaciones
        for empleado in empleadosStatusVacaciones:
            inicioVacaciones, finVacaciones = estandarDataPlantilla[empleado]["vacationsDays"]

            diaInicioVacaciones = int(inicioVacaciones.split("-")[-1])
            diaFinVacaciones = int(finVacaciones.split("-")[-1])

            if (diaInicioVacaciones <= diaNumero and diaFinVacaciones >= diaNumero):
                empleadosVacaciones.append(empleado)
            else:
                empleadosTienda.append(empleado)

        # Comprobar si el empleado sigue de incapacidad
        for empleado in empleadosStatusIncapacidad:
            inicioIncapacidad, finIncapacidad = estandarDataPlantilla[empleado]["incapacidadDays"]

            diaInicioIncapacidad = int(inicioIncapacidad.split("-")[-1])
            diaFinIncapacidad = int(finIncapacidad.split("-")[-1])

            if (diaInicioIncapacidad <= diaNumero and diaFinIncapacidad >= diaNumero):
                empleadosIncapacidad.append(empleado)
            else:
                empleadosTienda.append(empleado)

        contadorAuxiliar = 0

        for _ in range(0, len(empleadosTienda)):
            descansosPorDia[contadorAuxiliar] = descansosPorDia[contadorAuxiliar] + 1
            if contadorAuxiliar == 4:
                contadorAuxiliar = 0
            else:
                contadorAuxiliar = contadorAuxiliar + 1

        descansoDisponible = True
        primeraSemana = False
        diaPedido = False

        diaLetra = diasDelMesNombre[i]

        if diaLetra == diasDescansoLetra[0][:3] or diaLetra == diasDescansoLetra[1][:3]:
            descansoDisponible = False

        if diaLetra in diasPedido:
            diaPedido = True

        if i <= 5:
            primeraSemana = True

        if descansoDisponible and primeraSemana:
            descansosCantidadAleatorio = random.randint(0, len(descansosPorDia) - 1)
            descansos = descansosPorDia.pop(descansosCantidadAleatorio)
        else:
            descansos = 1

        horarioDia = horarioUnDia(descansoDisponible, respuestaJson, primeraSemana, descansos, empleadosVacaciones, empleadosIncapacidad, empleadosStatusPtr, empleadosTienda, diaPedido, estandarDataPlantilla, prioridadTurnos)

        for i in horarioDia:
            for key in i.keys():
                contenido = respuestaJson.get(key)
                if contenido == None:
                    respuestaJson.setdefault(key,{"NumeroEmpleado": key,
                                      "Nombre": estandarDataPlantilla[key]["Paterno"] + " "+estandarDataPlantilla[key]["Materno"] + " "+estandarDataPlantilla[key]["Nombre"] ,
                                      "Puesto": estandarDataPlantilla[key]["Puesto"],
                                      "Horario": [i[key]]})
                else:
                    auxiliarHorario = contenido["Horario"]
                    auxiliarHorario.append(i[key])
                    respuestaJson[key]["Horario"]: auxiliarHorario


    for i in respuestaJson:
        respuestaLista.append(respuestaJson[i])

    return respuestaLista

def horarioUnDia(descansoDisponible, horarioActual, primeraSemana, descansos, empleadosVacaciones, empleadosIncapacidad, empleadosPtr, empleadosTienda, diaPedido, estandarDataPlantilla, prioridadTurnos):

    empleadosActivos = []
    horarioDia = []

    contadorApertura = 0
    contadorCierre = 0

    # Comprobar empleados vacaciones

    for empleado in empleadosVacaciones:
        horarioDia.append({empleado: "VAC"})

    for empleado in empleadosIncapacidad:
        horarioDia.append({empleado: "INCAP"})

    # Comprobar empleados ptr
    for empleado in empleadosPtr:
        horarioDia.append({empleado: "PTR"})

    turnoGt = {
        "apertura": "06:30 a 16:30",
        "intermedio": "10:00 a 20:00",
        "cierre": "12:30 a 22:30",
    }

    turnoPt = {
        "apertura": "07:00 a 11:00",
        "intermedio": "12:00 a 16:00",
        "intermedio2": "14:00 a 18:00",
        "intermedio3": "16:00 a 20:00",
        "cierre": "18:30 a 22:30"
    }

    turnoFt = {
        "apertura": "06:30 a 14:30",
        "intermedio": "12:00 a 20:00",
        "cierre": "14:30 a 22:30"
    }

    turnoTr = {
        "apertura": "06:30 a 14:30",
        "intermedio": "13:00 a 21:00",
        "cierre": "14:30 a 22:30"
    }
    # Dia de pedido Gt turno apertura

    gtDiaPedido = []

    if diaPedido:
        gtTemporal = []

        for empleado in empleadosTienda:
            if "GT" in estandarDataPlantilla[empleado]["Puesto"]:
                gtTemporal.append(empleado)

        if len(gtTemporal) > 0:
            aleatorio = random.randint(0, len(gtTemporal) - 1)
            aperturaGt = gtTemporal.pop(aleatorio)
            gtDiaPedido.append(aperturaGt)
            horarioDia.append({aperturaGt: turnoGt["apertura"]})
            contadorApertura += 1

    if horarioActual != {}:
        for empleado in empleadosTienda:
            if diaPedido:
                if empleado != gtDiaPedido[0]:
                    diasTrabajar = 6
                    contadorDiasLaborales = 0
                    for turno in horarioActual[empleado]["Horario"]:
                        if turno != "DESC":
                            contadorDiasLaborales = contadorDiasLaborales + 1
                        else:
                            contadorDiasLaborales = 0
                    if "PT" in (horarioActual[empleado]["Puesto"]):
                        diasTrabajar = 4

                    if contadorDiasLaborales == diasTrabajar:
                        horarioDia.append({empleado: "DESC"})
                    else:
                        empleadosActivos.append(empleado)
            else:
                diasTrabajar = 6
                contadorDiasLaborales = 0
                for turno in horarioActual[empleado]["Horario"]:
                    if turno != "DESC":
                        contadorDiasLaborales = contadorDiasLaborales + 1
                    else:
                        contadorDiasLaborales = 0
                if "PT" in (horarioActual[empleado]["Puesto"]):
                    diasTrabajar = 4

                if contadorDiasLaborales >= diasTrabajar:
                    horarioDia.append({empleado: "DESC"})
                else:
                    empleadosActivos.append(empleado)
    else:
        if diaPedido:
            for empleado in empleadosTienda:
                if empleado != gtDiaPedido[0]:
                    empleadosActivos.append(empleado)
        else:
            empleadosActivos = empleadosTienda.copy()

    #Primer semana de descansos aleatorios

    if primeraSemana and descansoDisponible:

        trDescansando = False
        for i in range(descansos):
            while True:
                descansoAleatorio = random.randint(0, len(empleadosActivos) - 1)
                empleadoDescansa = empleadosActivos[descansoAleatorio]

                empleadoDataPuesto = estandarDataPlantilla[empleadoDescansa]["Puesto"]

                if not(trDescansando and "TR" in empleadoDataPuesto) :

                    if empleadoDescansa in horarioActual:
                        horarioEmpleadoDescansa = horarioActual[empleadoDescansa]["Horario"]
                        if not("DESC" in horarioEmpleadoDescansa):
                            empleadosActivos.pop(descansoAleatorio)
                            puestoDescanso = estandarDataPlantilla[empleadoDescansa]["Puesto"]
                            if "TR" in puestoDescanso:
                                trDescansando = True
                            horarioDia.append({empleadoDescansa: "DESC"})
                            break

                    else:
                        empleadosActivos.pop(descansoAleatorio)
                        puestoDescanso = estandarDataPlantilla[empleadoDescansa]["Puesto"]
                        if "TR" in puestoDescanso:
                            trDescansando = True
                        horarioDia.append({empleadoDescansa: "DESC"})
                        break



    auxiliarGt, auxiliarPt, auxiliarFt, auxiliarTr = conteoEmpleados(empleadosActivos, estandarDataPlantilla)

    #Comprobamos el turno para los empleados PT
    for pt in auxiliarPt:
        if estandarDataPlantilla[pt]["horarioPt"] == "pm":
            horarioDia.append({pt: turnoPt["cierre"]})
            contadorCierre = 1
        if estandarDataPlantilla[pt]["horarioPt"] == "in":
            horarioDia.append({pt: turnoPt["intermedio"]})
        if estandarDataPlantilla[pt]["horarioPt"] == "in2":
            horarioDia.append({pt: turnoPt["intermedio2"]})
        if estandarDataPlantilla[pt]["horarioPt"] == "in3":
            horarioDia.append({pt: turnoPt["intermedio3"]})
        if estandarDataPlantilla[pt]["horarioPt"] == "am":
            horarioDia.append({pt: turnoPt["apertura"]})
            contadorApertura += 1

    # Para la apertura

    if contadorApertura != 2:

        # Para los rojos

        if len(auxiliarTr) > 0:
            aleatorio = random.randint(0, len(auxiliarTr) - 1)
            aperturaTr = auxiliarTr.pop(aleatorio)
            horarioDia.append({aperturaTr: turnoTr["apertura"]})
        elif len(auxiliarGt) > 0:
            aleatorio = random.randint(0, len(auxiliarGt) - 1)
            aperturaGt = auxiliarGt.pop(aleatorio)
            horarioDia.append({aperturaGt: turnoGt["apertura"]})

        #Para los verdes
        if len(auxiliarFt) > 0:
            aleatorio = random.randint(0, len(auxiliarFt)-1)
            aperturaFt = auxiliarFt.pop(aleatorio)
            horarioDia.append({aperturaFt: turnoFt["apertura"]})

    #Fin de la apertura

    #Cierre

    if len(auxiliarTr) > 0:
        aleatorio = random.randint(0, len(auxiliarTr) - 1)
        cierreTr = auxiliarTr.pop(aleatorio)
        horarioDia.append({cierreTr: turnoTr["cierre"]})
    elif len(auxiliarGt) > 0:
        aleatorio = random.randint(0, len(auxiliarGt) - 1)
        cierreGt = auxiliarGt.pop(aleatorio)
        horarioDia.append({cierreGt: turnoGt["cierre"]})

    #Para los verdes
    if len(auxiliarFt) > 0:
        aleatorio = random.randint(0, len(auxiliarFt)-1)
        cierreFt = auxiliarFt.pop(aleatorio)
        horarioDia.append({cierreFt: turnoFt["cierre"]})

    #Fin del cierre


    #Horarios intermedios y empleados restantes

    tamañoHorarios = len(horarioDia)

    contadorGT = 0
    contadorFt = 0
    contadorTr = 0
    contadorPt = 0

    while True:

        empleadosTiempoCompleto = [prioridadTurnos[0],prioridadTurnos[1], prioridadTurnos[2]]

        #Para el persona Gt

        if len(auxiliarGt ) > 0:
            aleatorio = random.randint(0, len(auxiliarGt) - 1)
            intermedioGt = auxiliarGt.pop(aleatorio)

            if contadorGT < len(empleadosTiempoCompleto) -1:
                contadorGT += 1
            else:
                contadorGT = 0

            horarioDia.append({intermedioGt: turnoGt[empleadosTiempoCompleto[contadorGT]]})

        #Para el personal Ft

        if len(auxiliarFt) > 0:
            aleatorio = random.randint(0, len(auxiliarFt) - 1)
            intermedioFt = auxiliarFt.pop(aleatorio)
            if contadorFt < len(empleadosTiempoCompleto)-1:
                contadorFt += 1
            else:
                contadorFt = 0
            horarioDia.append({intermedioFt: turnoFt[empleadosTiempoCompleto[contadorFt]]})
        #Para el personas Tr

        if len(auxiliarTr) > 0:
            aleatorio = random.randint(0, len(auxiliarTr) - 1)
            intermedioTr = auxiliarTr.pop(aleatorio)

            if contadorTr < len(empleadosTiempoCompleto)-1:
                contadorTr += 1
            else:
                contadorTr = 0

            horarioDia.append({intermedioTr: turnoTr[empleadosTiempoCompleto[contadorTr]]})

        if tamañoHorarios == len(horarioDia):
            break
        else:
            tamañoHorarios = len(horarioDia)

    #Fin Horarios intermedios

    return horarioDia

def algoritmo(tienda):

    resp = requests.get(process.env.URL)
    data = resp.json()

    llaves = list(data.keys())

    diasDescansoLetra = data[llaves[-1]]["dias"]

    estandarDataPlantilla = {}

    plantilla = data[llaves[-1]]["plantilla"]

    diasPedido = data[llaves[-1]]["diasPedido"]

    prioridadTurnos = data[llaves[-1]]["prioridadTurnos"]

    newPrioridadTurnos  = []

    for turno in prioridadTurnos["items"]:
        newPrioridadTurnos.append(turno["content"])

    newDiasPedido = []

    for dia in diasPedido:
        newDiasPedido.append(dia["value"])

    diasPedido = newDiasPedido

    for dato in plantilla:
        estandarDataPlantilla.setdefault(dato["NumeroEmpleado"], dato)

    horarioPorCadaEmpleado = {}

    tiendas, numeroEmpleados = obtenerTiendas()

    empleadosTien = empleadosTienda(tienda, numeroEmpleados)

    # Primera condicion
    primerPaso = primerCondicion(empleadosTien)

    if primerPaso:
        puestosEmplea = puestosEmpleados(empleadosTien)

        segundoPaso = segundaCondicion(puestosEmplea)
        if segundoPaso:

            # Generamos los primeros descansos
            dia, dias = diasDelMes()
            diasNumero, diasNombre = diasLetra(dia, dias)

            res= generarHorario(diasNombre, diasNumero, diasDescansoLetra, estandarDataPlantilla, diasPedido, newPrioridadTurnos)

            return res

        else:
            return alertaSegundaCondicion()
    else:
        return alertaPrimeraCondicion()


def listaDeTiendasSinGt():
    tiendasSinGt = []
    tiendas, numeroEmpleados = obtenerTiendas()
    for tienda in tiendas:
        numeroGerentes = 0
        empleadosTien = empleadosTienda(tienda, numeroEmpleados)
        puestosEmplea = puestosEmpleados(empleadosTien)

        for puesto in puestosEmplea:
            if puesto.startswith('GT'):
                numeroGerentes += 1
                break

        if numeroGerentes == 0:
            tiendasSinGt.append(tienda)

    return tiendasSinGt


def listaDeTiendasSinPersonalMinimo():
    tiendasSinMInimo = []

    tiendas, numeroEmpleados = obtenerTiendas()
    for tienda in tiendas:
        empleadosTien = empleadosTienda(tienda, numeroEmpleados)
        if len(empleadosTien) < 5:
            tiendasSinMInimo.append(tienda)

    return tiendasSinMInimo

def listaDeTiendasConMuchoPersonal():
    tiendasConMuchos = []

    tiendas, numeroEmpleados = obtenerTiendas()
    for tienda in tiendas:
        empleadosTien = empleadosTienda(tienda, numeroEmpleados)
        if len(empleadosTien) > 14:
            tiendasConMuchos.append(tienda)

    return tiendasConMuchos

def listaDeTiendasSinTrMinimos():
    tiendasSinTr = []

    tiendas, numeroEmpleados = obtenerTiendas()
    for tienda in tiendas:
        numeroTr = 0
        empleadosTien = empleadosTienda(tienda, numeroEmpleados)
        puestosEmplea = puestosEmpleados(empleadosTien)

        for puesto in puestosEmplea:
            if puesto.startswith('TR'):
                numeroTr += 1
            if numeroTr == 2:
                break

        if numeroTr< 2 :
            tiendasSinTr.append(tienda)

    return tiendasSinTr



def obtenerAdministrador(numeroEmpleado):
    estandarData = {}
    resp = requests.get(process.env.URL)
    data = resp.json()
    for dato in data:
        estandarData.setdefault(dato["NumeroEmpleado"], dato)
    return estandarData.get(int(numeroEmpleado))

def revisarHorario(tienda):
    pass


def tiendasConSinHorario():
    estandarData = {}
    resp = requests.get(process.env.URL)
    data = resp.json()
    tiendas, numeroEmpleados = obtenerTiendas()
    tiendasConHorario = []
    for tienda in data:
        tiendasConHorario.append(tienda)
        if (tienda in tiendas):
            indice = tiendas.index(tienda)
            tiendas.pop(indice)

    newData = {
        "tiendasSinHorario": tiendas,
        "tiendasConHorario": tiendasConHorario
    }

    return newData

@app.route("/tiendasHorarios", methods=["GET"])
def apiTiendasConSinHorario():
    data = tiendasConSinHorario()
    respuesta = jsonify({"data": data})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta


@app.route("/getAdmin/<idAdmin>", methods=["GET"])
def apiGetAdmin(idAdmin):
    administrador = obtenerAdministrador(idAdmin)
    respuesta = jsonify({"admin": administrador})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/empleados/<tienda>", methods=["GET"])
def apiEmpleadosTienda(tienda):
    tiendas, numeroEmpleados = obtenerTiendas()
    empleadosTien = empleadosTienda(tienda, numeroEmpleados)
    empleados = datosEmpleadosTienda(empleadosTien)
    respuesta = jsonify({"empleados": empleados})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/maxMinDate", methods=["GET"])
def apiMaxMinDate():
    fecha = datetime.date.today()
    monthRange = calendar.monthrange(fecha.year, fecha.month)
    dia, dias = monthRange
    respuesta = [fecha.month, fecha.year, dias, fecha.day]
    respuesta = jsonify({"date": respuesta})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/verificar/maxPersonal", methods=["GET"])
def apiVerificarMaxPersonal():
    tiendas = listaDeTiendasConMuchoPersonal()
    respuesta = jsonify({"tiendas": tiendas})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/verificar/tr", methods=["GET"])
def apiVerificarTr():
    tiendas = listaDeTiendasSinTrMinimos()
    respuesta = jsonify({"tiendas": tiendas})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/verificar/gt", methods=["GET"])
def apiVerificarGt():
    tiendas = listaDeTiendasSinGt()
    respuesta = jsonify({"tiendas": tiendas})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/verificar/empleados", methods=["GET"])
def apiVerificarMinimos():
    tiendas = listaDeTiendasSinPersonalMinimo()
    respuesta = jsonify({"tiendas": tiendas})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/tiendas", methods=["GET"])
def apiTiendas():
    tiendas, numeroEmpleados = obtenerTiendas()
    respuesta = jsonify({"tiendas": tiendas})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/horario/<Tienda>", methods=["GET"])
def apiHorario(Tienda):
    res = algoritmo(Tienda)
    respuesta = jsonify({"data": res})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/diasNumero", methods=["GET"])
def apiDiasNumero():
    dia, dias = diasDelMes()
    diasNumero, diasNombre = diasLetra(dia, dias)
    respuesta = jsonify({"diasNumero": diasNumero})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/dias", methods=["GET"])
def apiDiasLetra():
    dia, dias = diasDelMes()
    diasNumero, diasNombre = diasLetra(dia, dias)
    respuesta = jsonify({"diasLetra": diasNombre})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/obtener/<Gerente>", methods=["GET"])
def apiObtenerGerente(Gerente):
    res = obtenerGerentes(Gerente)
    respuesta = jsonify({"data": res})
    respuesta.headers.add('Access-Control-Allow-Origin', '*')
    return respuesta

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello"})

if __name__ == '__main__':
    app.run()