import glob
import os
import time
from datetime import date, datetime
from fpdf import FPDF
from dateutil.relativedelta import relativedelta
from lib import pgdict0, pgddict, per, pglflat,pgdict,pgonecolumn, letras, listsql


def cuotaje(con,idvta):
    """Funcion que entrega la matriz de cuotas a pagar para una cuenta dada."""
    venta = pgdict(con, f"select id,fecha,cc,ic,saldo,pagado,primera,p from \
                           ventas where id={idvta}")[0]
    listcuotas = []
    saldo = venta['saldo']
    if saldo!=0:
        pagado=venta['pagado']
        cant_cuotas=venta['cc']
        imp_cuota=venta['ic']
        periodicidad=venta['p']
        primera=venta['primera']
        for i in range(1,cant_cuotas+1):
            if periodicidad==1:
                vto = primera + relativedelta(months=+(i-1))
            if periodicidad==3:
                vto = primera + relativedelta(weeks= +(i-1))
            if periodicidad==2:
                vto = primera + relativedelta(weeks= +((i-1)*2))
            listcuotas.append([i,vto,0 if pagado>=imp_cuota else \
                               (imp_cuota if pagado<=0 else imp_cuota-pagado)])
            pagado = pagado - imp_cuota
    return listcuotas


def calc(con, idcliente):
    sql =  f"select id from ventas where idcliente={idcliente} and saldo>0"
    cur = con.cursor()
    cur.execute(sql)
    ventas = cur.fetchall()[0]
    cnt = 0
    for v in ventas:
        dv = pgonecolumn(con, f"select count(*) from detvta where idvta={v}")
        pagadas = pgonecolumn(con, f"select count(*) from pagos where idvta={v}")
        cuotas = 6
        if pagadas>cuotas:
            c = pagadas
        else:
            c = cuotas
        cnt += dv + c + 1
    return cnt


class MyFPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', '', 10)
        self.set_y(5)
        self.cell(0, 6, 'Pag ' + str(self.page_no()), 0, 0, 'R')
        self.ln(10)
    def footer(self):
        pass


def ficha(con,ldni):
    pdf=MyFPDF()
    pdf.set_margins(30,15)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    lpg ='('
    for dni in ldni:
        lpg+=str(dni)+','
    lpg = lpg[0:-1]+')'
    listdni = pglflat(con,f"select dni from clientes where dni in {lpg} order by calle,num")

    i=1
    lisdatos = [] # lista que contendra los datos del resumen
    # dictPos = {} # diccionario de posisiones de ficha en paginas
    # dictNombre = {} # dicc que guarda los nombres para el resumen
    # dictDir = {} # dicc que guarda la direccion para el resumen
    for dni in listdni:
        #regla para que no comience un encabezado con poco espacio
        cliente = pgdict0(con,f"select nombre,calle,num,tel,wapp,pmovto,barrio,zona,acla,mjecobr,horario,id,seguir,cuota from clientes where dni='{dni}'")
        estimado = calc(con, cliente[11])
        estimado += 9 # estimado bruto de los distintos encabezados
        if (pdf.get_y()+(estimado*6)>285):
            pdf.add_page()
            pdf.set_y(15)
        pdf.set_font_size(12)
        pdf.set_x(10)
        pdf.cell(20,6,str(i),0,0)
        # dictPos[i]=pdf.page_no()
        pdf.cell(100,6,cliente[0][0:38],0,0)
        pdf.set_font_size(10)
        pdf.cell(30,6,cliente[3][0:8],1,0,'C')
        pdf.cell(30,6,cliente[4],1,1,'C')
        pdf.cell(80,6,cliente[1],1,0)
        pdf.cell(10,6,cliente[2][0:4],1,0)
        # arreglar esto
        cliente_pmovto = cliente[5]
        if cliente_pmovto is None:
            cliente_pmovto = date.today()
        if cliente_pmovto<date.today():
            pmovto = date.today().strftime('%Y-%m-%d')
        else:
            pmovto = cliente_pmovto
        lisdatos.append((i,cliente[0][0:38],cliente[1]+' '+cliente[2],pdf.page_no(),pmovto,cliente[12],cliente[13]))
        pdf.cell(70,6,cliente[6],1,1)
        if cliente[8]:
            pdf.set_font_size(7)
            pdf.cell(0,4,cliente[8],0,1)
        if cliente[9]:
            pdf.set_font_size(7)
            pdf.cell(0,4,cliente[9],0,1)
        if cliente[10]:
            pdf.set_font_size(7)
            pdf.cell(0,4,cliente[10],0,1)
        if len(cliente[2])>4:
            pdf.set_font_size(7)
            pdf.cell(0,4,f"En numero se registra lo siguiente:{cliente[2]}",0,1)
        if len(cliente[3])>8:
            pdf.set_font_size(7)
            pdf.cell(0,4,f"En telefono se registra lo siguiente:{cliente[3]}",0,1)
        pdf.ln(2)
        pdf.set_font_size(10)
        pdf.cell(40,6,f'Visitar el {pmovto}',1,1)

        ventas=pgddict(con,f"select id,fecha,cc,ic,p,saldo from ventas where saldo>0 and idcliente={cliente[11]}")
        for venta in ventas:
            pdf.set_font_size(10)
            pdf.cell(15,6,f"{venta[0]}",1,0,'C')
            pdf.cell(25,6,f"{venta[1]}",1,0,'C')
            pdf.cell(50,6,f"{venta[2]} cuotas de ${venta[3]} {per(venta[4])}",1,0,'C')
            pdf.cell(35,6,f"Saldo ${venta[5]}",1,1,'C')
            detvtas=pgddict(con,f"select cnt,art,cc,ic from detvta where idvta={venta[0]}")
            for detvta in detvtas:
                pdf.set_font_size(8)
                pdf.cell(10,4,f"{detvta[0]}",1,0,'C')
                pdf.cell(80,4,f"{detvta[1]}",1,0)
                pdf.cell(35,4,f"{detvta[2]} cuotas de ${detvta[3]}",1,1,'C')

            cuotas = cuotaje(con,venta[0])
            pagadas = pgddict(con, f"select fecha,imp,rec,rbo,cobr from pagos where idvta={venta[0]} order by fecha")
            # Calculo el largo total que tendra la grilla de pagos
            if (len(cuotas)>len(pagadas)):
                max=len(cuotas)
            else:
                max=len(pagadas)

            # Formula para el calculo del espacio ocupable
            # if ((pdf.get_y()+max*7)>280):
            #     pdf.add_page()
            #     pdf.set_y(15)

            pdf.ln(2)
            pdf.set_font_size(10)
            y0 = pdf.get_y()
            pdf.cell(80,6,"Cuotas a Pagar",0,1)
            pdf.set_font_size(8)
            for cuota in cuotas:
                if cuota[2]:
                    pdf.cell(5,4,f"{cuota[0]}",1,0,'C')
                    pdf.cell(25,4,f"{cuota[1]}",1,0,'C')
                    pdf.cell(15,4,f"${cuota[2]}",1,1,'C')
            pdf.ln(2)
            y1=pdf.get_y()
            pgy1 = pdf.page_no()
            pdf.set_y(y0)
            pdf.set_x(90)
            pdf.set_font_size(10)
            pdf.cell(80,6,"Cuotas Pagadas",0,1)
            pdf.set_font_size(8)
            for pagada in pagadas:
                pdf.set_x(90)
                pdf.cell(25,4,f"{pagada[0]}",1,0,'C')
                pdf.cell(20,4,f"${pagada[1]}",1,0,'C')
                pdf.cell(15,4,f"${pagada[2]}",1,0,'C')
                pdf.cell(20,4,f"{pagada[3]}",1,0,'C')
                pdf.cell(10,4,f"{pagada[4]}",1,1,'C')
            if (y1>pdf.get_y() and pgy1==pdf.page_no()):
                pdf.set_y(y1)
            if (y1<pdf.get_y() and pgy1<pdf.page_no()):
                pdf.set_y(pdf.get_y())
            pdf.set_x(30)
            pdf.ln(5)
        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        i+=1

    if (len(ldni)>1):
        pdf.add_page()
        # for x in dictPos.keys():
        #     pdf.cell(10,5,str(x),1,0,'C')
        #     pdf.cell(60,5,dictNombre[x],1,0,'L')
        #     pdf.cell(60,5,dictDir[x],1,0,'L')
        #     pdf.cell(20,5,'Pag N°'+str(dictPos[x]),1,1,'C')
        suma_a_cobrar = 0
        for row in lisdatos:
            suma_a_cobrar += row[6]
            if row[5]:
                pdf.set_font("Helvetica","B",10)
            else:
                pdf.set_font("Helvetica","", 10)
            pdf.cell(20,5,str(row[4]),1,0,'C')
            pdf.cell(10,5,str(row[0]),1,0,'C')
            pdf.cell(60,5,row[1][:24],1,0,'L')
            pdf.cell(40,5,row[2][:22],1,0,'L')
            pdf.cell(15,5,'Pag '+ str(row[3]),1,0,'C')
            pdf.cell(20,5,str(row[6]),1,1,'C')
        pdf.cell(165,10,f'Suma a cobrar ${suma_a_cobrar}',1,1,'R')
    pdf.output("/home/hero/ficha.pdf")

def libredeuda(con,dni):
    libre = """
    Por la presente certificamos que el cliente de referencia no adeuda nada en ningun concepto a nuestra Empresa. Que al dia de la fecha ha sido CANCELADA su cuenta."""
    seven = """
    La baja del SEVEN se producira en forma automatica dentro de los proximos CINCO DIAS HABILES"""
    today = datetime.today().strftime('%Y-%m-%d')
    pdf=FPDF()
    pdf.set_margins(30,30)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    cliente = pgdict0(con, f"select nombre, calle,num,barrio,sev from clientes where dni='{dni}'")
    pdf.set_font_size(22)
    pdf.image('/home/hero/imagenes/romitex.png', w=80, h=20)
    pdf.ln(5)
    pdf.cell(100,12,"LIBRE DEUDA",0,1,'L')
    pdf.set_font_size(12)
    pdf.cell(150,8,today,0,1,'R')
    pdf.cell(150,8,"Ref. LIBRE DEUDA CON ROMITEX", 0, 1, 'R')
    pdf.cell(100,6,cliente[0][0:38],0,1)
    pdf.cell(100,6,f"{cliente[1]} {cliente[2]} {cliente[3]}",0,1)
    pdf.ln(5)
    pdf.multi_cell(0, 8, libre , border = 0,
                align = 'J', fill = False)
    if cliente[4]:
        pdf.multi_cell(0, 8, seven , border = 0,
                align = 'J', fill = False)
    pdf.ln(7)
    pdf.cell(150,6,"DEPARTAMENTO DE COBRANZAS ROMITEX", 0, 1, 'R')
    pdf.set_y(260)
    pdf.set_font_size(18)
    pdf.cell(150,12,"Rioja 441 Planta Baja Of. F - Tel 155-297-472", 0, 1, 'L')
    pdf.set_font_size(12)
    pdf.output(f"/home/hero/libredeuda{dni}.pdf")


def recibotransferencia(con,fecha,cuenta,nc,ic,cobr,rbo,idcliente):
    today = datetime.today().strftime('%Y-%m-%d')
    cliente = pgdict0(con, f"select nombre, calle,num,barrio,sev from clientes where id='{idcliente}'")
    texto = f"""RECIBIMOS de {cliente[0]} con domicilio en {cliente[1]} {cliente[2]} {cliente[3]} la suma de pesos {letras(ic)} en concepto de pago de la cuota {nc} de la cuenta {cuenta}, por medio de una transferencia al CBU 0720556988000035614454."""
    advertencia = """Este recibo solo es valido si se adjunta con el comprobante de la transferencia que lo origino"""
    pdf=FPDF()
    pdf.set_margins(30,30)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    pdf.set_font_size(22)
    pdf.image('/home/hero/imagenes/romitex.png', w=80, h=20)
    pdf.ln(5)
    pdf.cell(100,12,"RECIBO",0,1,'L')
    pdf.set_font_size(12)
    pdf.cell(150,8,today,0,1,'R')
    pdf.cell(150,8,f"Recibo de pago por transferencia N°{rbo}", 0, 1, 'R')
    pdf.cell(150,8,f"Importe ${ic}", 0, 1, 'R')
    pdf.ln(2)
    pdf.multi_cell(0, 8, texto , border = 0,
                align = 'J', fill = False)
    pdf.ln(5)
    pdf.multi_cell(0, 8, advertencia , border = 0,
                align = 'J', fill = False)
    pdf.ln(5)
    pdf.cell(150,6,"DEPARTAMENTO DE COBRANZAS ROMITEX", 0, 1, 'R')
    pdf.set_y(260)
    pdf.set_font_size(18)
    pdf.cell(150,12,"Rioja 441 Planta Baja Of. F - Tel 155-297-472", 0, 1, 'L')
    pdf.set_font_size(12)
    pdf.output(f'/home/hero/recibotransferencia{cuenta}.pdf')



def intimacion(con,ldni):
    today = datetime.today().strftime('%Y-%m-%d')
    intim1 = """
    Por la presente le recordamos que segun nuestros registros mantiene una DEUDA VENCIDA E IMPAGA con nuestra empresa.
    A pesar de las numerosas visitas de cobro que hemos realizado no hemos podido obtener repuesta de su parte, por lo que nos vemos en la obligacion de concluir que no existe voluntad de su parte de pagar la cuenta segun lo acordado.
    Cumplimos en avisarle que su nombre sera informado al registro de morosos SEVEN en los proximos dias. El sistema de informacion de morosos SEVEN mantiene una base de datos de morosos de nuestra ciudad, por lo cual se inclusion en el mismo le trabara y/o dificultara cualquier operacion comercial presente o futura.
    """
    intim2 = """
    Por la presente le recordamos que segun nuestros registros mantiene una DEUDA VENCIDA E IMPAGA con nuestra empresa.
    A pesar de las numerosas visitas de cobro que hemos realizado no hemos podido obtener repuesta de su parte, por lo que nos vemos en la obligacion de concluir que no existe voluntad de su parte de pagar la cuenta segun lo acordado.
    Cumplimos en avisarle que su nombre fue informado al registro de morosos SEVEN. El sistema de informacion de morosos SEVEN mantiene una base de datos de morosos de nuestra ciudad, por lo cual se inclusion en el mismo le trabara y/o dificultara cualquier operacion comercial presente o futura.

    En el caso de querer regularizar su deuda puede solicitar un plan de pagos por WhatsApp al 351-5-297-472.
    Una vez cancelada la cuenta se informa inmediatamente al SEVEN para proceder a eliminar su nombre de dicho registro.
    """
    pdf=FPDF()
    pdf.set_margins(30,30)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    lpg ='('
    for dni in ldni:
        lpg+=str(dni)+','
    lpg = lpg[0:-1]+')'
    listdni = pglflat(con,f"select dni from clientes where dni in {lpg} order by calle,num")
    for dni in listdni:
        if (pdf.get_y()>250):
            pdf.add_page()
            pdf.set_y(15)
        cliente = pgdict0(con,f"select nombre,calle,num,barrio,sev from clientes where dni='{dni}'")
        pdf.set_font_size(22)
        pdf.cell(100,12,"INTIMACION DE PAGO", 0, 1, 'L')
        pdf.set_font_size(12)
        pdf.cell(150,8,today,0,1,'R')
        pdf.cell(150,8,"Ref. DEUDA CON ROMITEX", 0, 1, 'R')
        pdf.cell(100,6,cliente[0][0:38],0,1)
        pdf.cell(100,6,f"{cliente[1]} {cliente[2]} {cliente[3]}",0,1)
        pdf.ln(5)
        if cliente[4]:
            intim = intim2
        else:
            intim = intim1
        pdf.multi_cell(0, 8, intim , border = 0,
                align = 'J', fill = False)
        # pdf.image('/root/anonymous.jpg')
        pdf.ln(3)
        pdf.cell(150,6,"GESTION DE COBRO ROMITEX", 0, 1, 'R')
        pdf.set_y(260)
        pdf.set_font_size(18)
        pdf.cell(150,12,"Rioja 441 Planta Baja Of. F - Tel 155-297-472", 0, 1, 'L')
        pdf.set_font_size(12)
    if len(ldni) == 1:
        pdf.output(f"/home/hero/intimacion{dni}.pdf")
    else:
        pdf.output("/home/hero/intimacion_global.pdf")



def loterbo(con, lrbo, fecha, cobr, idlote, estimado, cobrado):
    pdf=FPDF()
    pdf.set_margins(15,15)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    pdf.set_y(5)
    pdf.cell(20,6,str(fecha),0,0,'C')
    pdf.cell(20,6,f"Cobr {cobr}",0,0,'C')
    pdf.cell(20,6,f"Lote N° {idlote}",0,0,'C')
    pdf.cell(60,6,f"Cobrado en el mes ${cobrado}",0,0,'C')
    pdf.cell(60,6,f"Falta estimado ${estimado}",0,1,'C')
    pdf.set_y(15)
    for n,rbo in enumerate(lrbo):
        if n==43:
            pdf.set_y(15)
            pdf.set_x(80)
        if n==86:
            pdf.set_y(15)
            pdf.set_x(150)
        if (n>43 and n<86):
            pdf.set_x(80)
        if n>86:
            pdf.set_x(150)
        pdf.cell(8,6,str(n+1),1,0,'C')
        pdf.cell(20,6,str(rbo),1,0,'C')
        pdf.cell(25,6,'',1,1)
    pdf.set_y(-50)
    pdf.set_x(150)
    pdf.cell(28,6,'Total',1,0,'R')
    pdf.cell(25,6,'$',1,1)
    pdf.set_x(150)
    pdf.cell(28,6,'Comision',1,0,'R')
    pdf.cell(25,6,'$',1,1)
    pdf.set_x(150)
    pdf.cell(28,6,'Viaticos',1,0,'R')
    pdf.cell(25,6,'$',1,1)
    pdf.set_x(150)
    pdf.cell(28,6,'A RENDIR',1,0,'R')
    pdf.cell(25,6,'$',1,1)
    pdf.output("/home/hero/loterbo.pdf")


def listado(con, ldni, formato):
    pdf = MyFPDF()
    pdf.set_margins(20,30)
    pdf.add_page()
    pdf.set_font("Helvetica","",14)
    listdni = pglflat(con,f"select dni from clientes where dni in {listsql(ldni)}")
    listcallenum = pglflat(con, f"select  distinct concat(calle, ' ' ,num) from clientes where dni in {listsql(listdni)} order by calle,num")

    for direccion in listcallenum:
        clientes = pgdict(con, f"select nombre,calle,num,acla,dni,year(ultcompra) as year,wapp,deuda,comprado from clientes where concat(calle,' ',num)='{direccion}'")
        if clientes[0]['acla']:
            pdf.set_font("Helvetica","B",14)
            pdf.cell(80,10,direccion,0,0,'center')
            pdf.set_font("Helvetica","",10)
            pdf.cell(80,10,clientes[0]['acla'],0,1,'left')
        else:
            pdf.set_font("Helvetica","B",14)
            pdf.cell(0,10,direccion,0,1,'center')
        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        for cliente in clientes:
            pdf.set_font("Helvetica","",10)
            pdf.cell(10,10,str(round(int(cliente['dni'])/1000000)),0,0)
            pdf.cell(70,10,cliente['nombre'][0:24],0,0)
            if cliente['deuda'] and cliente['deuda']>0:
                pdf.cell(60,10,f"whats:{cliente['wapp']}",0,0)
                pdf.set_font("Helvetica","B",10)
                if cliente['year']<2018:
                    pdf.cell(20,10,'consultar-',0,1)
                else:
                    pdf.cell(20,10,'No Vender',0,1)
                pdf.set_font("Helvetica","",10)
            elif not cliente['comprado']:
                pdf.cell(60,10,f"whats:{cliente['wapp']}",0,0)
                pdf.set_font("Helvetica","B",10)
                pdf.cell(20,10,'consultar',0,1)
                pdf.set_font("Helvetica","",10)
            else:
                pdf.cell(60,10,f"whats:{cliente['wapp']}",0,1)
            pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.ln('40')
        if formato=='fichas':
            y = pdf.get_y()
            if y<100:
                pdf.set_y(101)
            elif y>=100 and y<200:
                pdf.set_y(201)
            elif y>=201:
                pdf.add_page()
    pdf.output("/home/hero/listado.pdf")


def asuntos(con,ids):
    pdf=FPDF()
    pdf.set_margins(30,15)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    lpg ='('
    for id in ids:
        lpg+=str(id)+','
    lpg = lpg[0:-1]+')'
    listasuntos = pglflat(con,f"select asuntos.id as id,zona from asuntos,clientes where clientes.id=asuntos.idcliente and  asuntos.id in {lpg} order by zona")
    for id in listasuntos:
        asunto = pgdict(con, f"select asuntos.id as id, idcliente, tipo, fecha, vdor, asunto,nombre,calle,num,wapp,completado,zona from asuntos,clientes where clientes.id=asuntos.idcliente and asuntos.id={id}")[0]
        pdf.cell(60,6,asunto['nombre'][0:24],0,0)
        pdf.cell(50,6,asunto['calle']+' '+asunto['num'],0,0)
        pdf.cell(30,6,asunto['zona'],0,0)
        pdf.cell(30,6,asunto['wapp'],0,1)

        pdf.cell(30,6,str(asunto['fecha']),0,0)
        pdf.cell(30,6,asunto['tipo'],0,0)
        pdf.cell(140,6,asunto['asunto'],0,1)

        pdf.ln(2)
        pdf.line(10,pdf.get_y(),200,pdf.get_y())

    pdf.output("/home/hero/asuntos.pdf")


def cancelados(con, ids):
    pdf=FPDF()
    pdf.set_margins(30,15)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    lpg ='('
    for id in ids:
        lpg+=str(id)+','
    lpg = lpg[0:-1]+')'
    listacancelados = pgdict(con, f"select nombre, calle, num, acla, barrio, zona, tel, wapp from clientes where dni in {lpg} order by zona,barrio,calle,num")
    for c in listacancelados:
        pdf.cell(60,6,c['nombre'][0:24],0,0)
        pdf.cell(70,6,c['calle']+' '+c['num'],0,0)
        pdf.cell(40,6,c['barrio'],0,1)
        pdf.cell(30,6,c['zona'],0,0)
        pdf.cell(40,6,c['tel'],0,0)
        pdf.cell(30,6,c['wapp'],0,1)
        pdf.ln(2)
        pdf.line(10,pdf.get_y(),200,pdf.get_y())

    pdf.output("/home/hero/cancelados.pdf")



def listaprecios(lista,grupos):
    aleatorio = str(time.time_ns())[-4:]
    if 'liquidacion' in grupos:
        grupos.pop(grupos.index('liquidacion'))
        grupos.append('liquidacion')
    today = datetime.today().strftime('%d-%m-%Y')
    pdf=FPDF('P','mm','A4')
    pdf.set_margins(30,30)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    pdf.set_font_size(22)
    pdf.image('/home/hero/imagenes/romitex.png', w=80, h=20)
    pdf.ln(5)
    pdf.cell(100,12,"LISTA DE PRECIOS",0,1,'L')
    pdf.set_font_size(12)
    pdf.cell(150,8,today,0,1,'R')
    pdf.ln(5)
    for grupo in grupos:
        pdf.set_font_size(22)
        pdf.cell(0,12,grupo,0,1,'C')
        pdf.set_font_size(12)
        for item in lista:
            if item['grupo']==grupo:
                pdf.cell(10,8,item['codigo'],1,0,'C')
                pdf.cell(90,8,item['art'],1,0,'L')
                pdf.cell(50,8,f"     6 cuotas de ${item['cuota']:5}",1,1,'L')
        pdf.ln(3)
    # removemos todas las listas viejas generadas
    filelist = glob.glob('/home/hero/documentos/impresos/listapreciosGENERADA*.pdf')
    for f in filelist:
        os.remove(f)
    pdf.output(f"/home/hero/documentos/impresos/listapreciosGENERADA{aleatorio}.pdf")


def imprimir_stock(con, stock):
    """Impresion de planilla de stock para control."""
    today = datetime.today().strftime('%d-%m-%Y')
    pdf=FPDF('P','mm','A4')
    pdf.set_margins(30,30)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    pdf.set_font_size(22)
    pdf.ln(5)
    pdf.cell(100,12,f"STOCK {today}",0,1,'L')
    pdf.set_font_size(16)
    pdf.ln(5)
    for item in stock:
        if int(item['stock'])!=0:
            pdf.cell(100,12,item['art'],1,0,'L')
            pdf.cell(20,12,item['stock'],1,0,'C')
            pdf.cell(40,12,'',1,1)
    pdf.output("/home/hero/stock.pdf")

def listadocumentos(con, lista):
    """Imprimo lista documentos para purgar."""
    pdf=FPDF('P','mm','A4')
    pdf.set_margins(10,10)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    pdf.set_font_size(12)
    pdf.cell(0,10,'LISTADO DE DOCUMENTOS A CONSERVAR CON DEUDA',0,1,'C')
    pdf.set_font_size(10)
    for row in lista:
        pdf.cell(30,10,str(row['id']),0,0,'C')
        pdf.cell(80,10,row['nombre'],0,0,'L')
        pdf.cell(60,10,row['direccion'],0,0,'L')
        pdf.cell(30,10,str(row['saldo']),0,1,'C')
    pdf.output("/home/hero/documentos/listadocumentos.pdf")
