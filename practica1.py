from pysnmp.hlapi import *
from pysnmp.proto.errind import DataMismatch
import time
import rrdtool
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
def checkdb(name):
    try:
        with open(name, 'r') as f:
            return True
    except FileNotFoundError as e:
        return False
    except IOError as e:
        return False
def createdb(name):
    ret = rrdtool.create(name,
                     "--start",'N',
                     "--step",'60',
                     "DS:inmulti:COUNTER:600:U:U",
                     "DS:ippackets:COUNTER:600:U:U",
                     "DS:icmpme:COUNTER:600:U:U",
                     "DS:segout:COUNTER:600:U:U",
                     "DS:datagramsin:COUNTER:600:U:U",
                     "RRA:AVERAGE:0.5:1:20",
                     "RRA:AVERAGE:0.5:1:20",
                     "RRA:AVERAGE:0.5:1:20",
                     "RRA:AVERAGE:0.5:1:20",
                     "RRA:AVERAGE:0.5:1:20")
    if ret:
        print (rrdtool.error())
def consultaSNMP(comunidad,host,oid,port):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
        #print(errorIndication)
        return 'timeout'
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            resultado = ''
            varB= (' = '.join([x.prettyPrint() for x in varBind]))
            #print(varB)
            resultado=  varB.split()[2]
            if((len(varB.split("Software")) > 1) | (resultado == 'Linux')):
                resultado = varB.split("=")[1]
            
            
    return resultado
def walk(comunidad,host,oid,port):
    for (errorIndication,
     errorStatus,
     errorIndex,
     varBinds) in nextCmd(SnmpEngine(), 
                          CommunityData(comunidad),
                          UdpTransportTarget((host, port)),
                          ContextData(),                                                           
                          ObjectType(ObjectIdentity(oid)),
                          lexicographicMode=False):
        if errorIndication:
            #print(errorIndication)
            return 'timeout'
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                resultado = ''
                varB= (' = '.join([x.prettyPrint() for x in varBind]))
                resultado=  varB.split()[2]
    return resultado
               

def printMenu():
    print("1.- Agregar un agente")
    print("2.- Eliminar un agente")
    print("3.- Generar reporte")
    print("4.- Capturar datos")
    print("5.-Salir")
def addAgent():
    print("Ingresa el nombre o direccion ip del host")
    ip = input()
    print("Ingresa la version del smnp (1,2,3)")
    v = input()
    print("Ingresa el nombre de la comunidad")
    com = input()
    print("Ingresa el puerto")
    p = input()
    file = open("data.txt",'a')
    file.write("\nDireccion: "+ip+"\tVersionSNMP: "+v+"\tComunidad: "+com+"\tPuerto: "+p)
    file.close()
    createdb(ip+".rrd")
def delAgent():
    agentes = []
    file = open("data.txt","r+")
    lines = file.readlines()
    for s in lines:
        if(s != '\n'):
            agentes.append(s.split())
            
    print("Seleccione el agente que desea eliminar:\n")
    i = 1
    for agent in agentes:
        print(str(i)+".- "+agent[1])
        i+=1
    delete = input()
    file.seek(0)
    file.truncate()
    if os.path.exists(lines[int(delete)].split("\t")[0].split(" ")[1]+".rrd"):
        os.remove(lines[int(delete)].split("\t")[0].split(" ")[1]+".rrd")
    if os.path.exists(lines[int(delete)].split("\t")[0].split(" ")[1]+".xml"):
        os.remove(lines[int(delete)].split("\t")[0].split(" ")[1]+".xml")
    del lines[int(delete)]
    print(lines)
    for l in lines:
        file.write(l)
    file.close()
    
def resumen():
    try:
        file = open("data.txt",'r')
        lines = file.readlines()
        file.close()
    except:
        print("Algo ocurrio")
        return
    print("Numero de dispositivos: " +str(len(lines)-1))
    if((len(lines)-1) > 0):
        for l in lines:
            if(l != '\n'):
                atr = l.split("\t")
                dir = atr[0].split(" ")[1]
                com = atr[2].split(" ")[1]
                port = atr[3].split(" ")[1]
                db = checkdb(dir+".rrd")
                if(not db):
                    createdb(dir+".rrd")
                res = consultaSNMP(com,str(dir),"1.3.6.1.2.1.2.2.1.8.2",int(port))
                if(res == '1'):
                    print(dir+': Up')
                else:
                    print(dir+': Down')
                    continue
                res = consultaSNMP(com,str(dir),"1.3.6.1.2.1.2.1.0",int(port))
                print("\tNo. de interfaces: "+res)
                for i in range(int(res)):
                    
                    res = consultaSNMP(com,str(dir),"1.3.6.1.2.1.2.2.1.7."+str(i+1),int(port))
                    estado = "Up" if int(res) == 1 else "Down"
                    print("\t AdminStatus inteface "+str(i+1)+": "+estado)
                    res = consultaSNMP(com,str(dir),"1.3.6.1.2.1.2.2.1.2."+str(i+1),int(port))
                    print("\tDescripcion: "+res)
def graph(name,ti,tf):
    print(str(ti))
    ret = rrdtool.graph( "multicast.png",
                     "--start",str(ti),
                     "--end",str(tf),
                     "--vertical-label=Paquetes/s",
                     "--title=Paquetes multicast recibidos",
                     "DEF:inmulti="+name+":inmulti:AVERAGE",
                     "AREA:inmulti#22577A:Paquetes recibidos")
    ret = rrdtool.graph( "ippackets.png",
                     "--start",str(ti),
                     "--end",str(tf),
                     "--vertical-label=Paquetes/s",
                     "--title=Paquetes recibidos exitosamente,entregados a\n protocolos IPv4",
                     "DEF:ippackets="+name+":ippackets:AVERAGE",
                     "LINE3:ippackets#38A3A5:Paquetes recibidos")
    ret = rrdtool.graph( "icmpme.png",
                     "--start",str(ti),
                     "--end",str(tf),
                     "--vertical-label=Mensajes/s",
                     "--title=Mensajes de respuesta ICMP que se han enviado",
                     "DEF:icmpme="+name+":icmpme:AVERAGE",
                     "AREA:icmpme#57CC99:Mensaje enviados")
    ret = rrdtool.graph( "segout.png",
                     "--start",str(ti),
                     "--end",str(tf),
                     "--vertical-label=Segmentos/s",
                     "--title=Segmentos enviados que contienen la bandera RST",
                     "DEF:segout="+name+":segout:AVERAGE",
                     "LINE3:segout#80ED99:Segmentos enviados")
    ret = rrdtool.graph( "datagramsin.png",
                     "--start",str(ti),
                     "--end",str(tf),
                     "--vertical-label=Datagramas/s",
                     "--title=Datagramas recibidos que no pudieron ser entregados\npor razones distintas a la falta de\naplicacion en el puerto destino",
                     "DEF:datagramsin="+name+":datagramsin:AVERAGE",
                     "AREA:datagramsin#22577A:Datagramas recibidos")
def generarReporte():

    file = open("data.txt","r")
    lines = file.readlines()
    print("Selecciona un dispositivo:")
    i = 1
    for l in lines:
        if( l != "\n"):
            dispositivo = l.split("\t")
            print(str(i)+".- "+dispositivo[0].split(" ")[1])
            
            i+=1
    op = input()
    print("Ingresa la fecha y hora de inicio (DD-MM-AAAA HH:MM)")
    timeini = input()
    timeini =time.mktime(time.strptime(timeini,"%d-%m-%Y %H:%M"))
    print(timeini)
    print("Ingresa la fecha y hora de termino ((DD-MM-AAAA HH:MM)")
    timefin = input()
    timefin =time.mktime(time.strptime(timefin,"%d-%m-%Y %H:%M"))
    print(timefin)
    res = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.1.1.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    if(len(res.split("Software")) > 1):
        sistema = res.split("Software")[1].split(" ")[1]
        version = res.split("Software")[1].split(" ")[3]
    else:
        sistema = res.split(" ")[1]
        version = res.split(" ")[3]
    print("Sistema: "+sistema)
    print("Version: "+version)
    ubicacion = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.1.6.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    print("Ubicacion: "+ubicacion)
    tiempo = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.1.3.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    tiempo ="{0:.2f}".format(((int(tiempo)*0.01)/60)/60)
    print("Tiempo desde el ultimo reinicio: "+str(tiempo)+"hrs")
    ip = walk(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.4.20.1.1",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    print("Ip: "+ip)
    
    graph(lines[int(op)].split("\t")[0].split(" ")[1]+".rrd",int(timeini),int(timefin))
    c = canvas.Canvas(lines[int(op)].split("\t")[0].split(" ")[1]+".pdf",pagesize=A4)
    w, h = A4
    if(sistema == "Linux"):
        c.drawImage("linux.jpg",10,h-60,width=50,height=50)
    else:
        c.drawImage("windows.jpeg",10,h-60,width=50,height=50)
    c.setFont("Helvetica", 10)
    c.drawString(65, h-25, "SO: "+sistema+"  Version: "+version+"  Ubicacion: "+ubicacion)
    c.drawString(65, h-50, "Tiempo de actividad antes del ultimo reinicio: "+tiempo+"hrs  Comunidad: "+lines[int(op)].split("\t")[2].split(" ")[1]+"  IP: "+ip)
    c.line(0,h-65,w,h-65)
    c.drawImage("multicast.png",10,h-185,width=w-20,height=110)
    c.drawImage("ippackets.png",10,h-305,width=w-20,height=110)
    c.drawImage("icmpme.png",10,h-425,width=w-20,height=110)
    c.drawImage("segout.png",10,h-545,width=w-20,height=110)
    c.drawImage("datagramsin.png",10,h-665,width=w-20,height=110)
    c.save()
   

def capturar():
    file = open("data.txt","r")
    lines = file.readlines()
    print("Selecciona un dispositivo:")
    i = 1
    for l in lines:
        if( l != "\n"):
            dispositivo = l.split("\t")
            print(str(i)+".- "+dispositivo[0].split(" ")[1])
            
            i+=1
    op = input()
    while(1):
        inMulti = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.2.2.1.12.2",int(lines[int(op)].split("\t")[3].split(" ")[1]))
        ipPackets = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.4.9.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
        icmpMe = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.5.14.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
        segOut = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.6.15.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
        datgramsIn = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.7.3.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
        valor = "N:" + str(inMulti) + ':' + str(ipPackets) + ':' + str(icmpMe) + ':' + str(segOut) + ':' + str(datgramsIn)
        print(valor)
        rrdtool.update(lines[int(op)].split("\t")[0].split(" ")[1]+'.rrd', valor)
        rrdtool.dump(lines[int(op)].split("\t")[0].split(" ")[1]+'.rrd',lines[int(op)].split("\t")[0].split(" ")[1]+'.xml')
        time.sleep(1)

resumen()

while 1:
    printMenu()
    op = input()
    if(int(op) == 1):
        addAgent()
    elif(int(op) == 2):
        delAgent()
    elif(int(op) == 3):
        generarReporte()
    elif(int(op) == 4):
        capturar()
    else:
        break
