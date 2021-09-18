from pysnmp.hlapi import *

def consultaSNMP(comunidad,host,oid,port):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            varB=(' = '.join([x.prettyPrint() for x in varBind]))
            print(varB)
            resultado= varB.split()[2]
    return resultado
def printMenu():
    print("1.- Agregar un agente")
    print("2.- Eliminar un agente")
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
        print("Numero de dispositivos: " +str(len(lines)-1))
        if((len(lines)-1) > 0):
            for l in lines:
                if(l != '\n'):
                    atr = l.split("\t")
                    dir = atr[0].split(" ")[1]
                    com = atr[2].split(" ")[1]
                    port = atr[3].split(" ")[1]
                    print(consultaSNMP(com,dir,"1.3.6.1.2.1.2.1.0",port))
    except:
        print("Algo ocurrio")
        return

resumen()
while 1:
    printMenu()
    op = input()
    if(int(op) == 1):
        addAgent()
    elif(int(op) == 2):
        delAgent()
