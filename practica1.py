from pysnmp.hlapi import *
from pysnmp.proto.errind import DataMismatch


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
    print("4.- Salir")
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
    inMulti = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.2.2.1.12.2",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    print("Multi: "+inMulti)
    ipPackets = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.4.9.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    print("Ip Packets: "+ipPackets)
    icmpMe = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.5.14.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    print("ICMP messageses out: "+icmpMe)
    #Los dispositivos no soportaban el oid indicado
    segOut = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.6.15.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    print("Segout: "+segOut)
    
    datgramsIn = consultaSNMP(lines[int(op)].split("\t")[2].split(" ")[1],lines[int(op)].split("\t")[0].split(" ")[1],"1.3.6.1.2.1.7.3.0",int(lines[int(op)].split("\t")[3].split(" ")[1]))
    print("Datagrams in: "+datgramsIn)

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
    else:
        break
