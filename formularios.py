# -*- coding: utf-8 -*-
import glob
import os
import time
from datetime import date, datetime
from fpdf import FPDF
from dateutil.relativedelta import relativedelta
from lib import *


def cuotaje(con,idvta):
    """Funcion que entrega la matriz de cuotas a pagar para una cuenta dada."""
    venta = pglistdict(con, f"select id,fecha,cc,ic,saldo,pagado,primera,p from \
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
    """Calcula la cantidad de renglones que ocuparan las ventas vigentes que
    apareceran en la ficha."""
    sql =  f"select id from ventas where idcliente={idcliente} and saldo>0"
    ventas = pglist(con, sql)
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


def ficha(con,ldni, total_cobrable=None, total_cobrado=None):
    if total_cobrado=='' or total_cobrado is None:
        total_cobrado = 0
    pdf=MyFPDF()
    pdf.set_margins(30,15)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    lpg ='('
    for dni in ldni:
        lpg+=str(dni)+','
    lpg = lpg[0:-1]+')'
    listdni = pglist(con,f"select dni from clientes where dni in {lpg} order by calle,num")

    i=1
    lisdatos = [] # lista que contendra los datos del resumen
    # dictPos = {} # diccionario de posisiones de ficha en paginas
    # dictNombre = {} # dicc que guarda los nombres para el resumen
    # dictDir = {} # dicc que guarda la direccion para el resumen
    listapmovtos = pglist(con,f"select pmovto from clientes where dni in {lpg}")
    pmovtos = [min(listapmovtos),max(listapmovtos)]
    for dni in listdni:
        #regla para que no comience un encabezado con poco espacio
        cliente = pgtuple(con,f"select nombre,calle,num,tel,wapp,pmovto,barrio,zona,acla,mjecobr,horario,id,seguir,cuota from clientes where dni='{dni}'")

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

        ventas=pglisttuples(con,f"select id,fecha,cc,ic,p,saldo from ventas where saldo>0 and idcliente={cliente[11]}")
        for venta in ventas:
            pdf.set_font_size(13)
            pdf.cell(15,6,f"{venta[0]}",1,0,'C')
            pdf.set_font_size(10)
            pdf.cell(25,6,f"{venta[1]}",1,0,'C')
            pdf.cell(50,6,f"{venta[2]} cuotas de ${venta[3]} {per(venta[4])}",1,0,'C')
            pdf.cell(35,6,f"Saldo ${venta[5]}",1,1,'C')
            detvtas=pglisttuples(con,f"select cnt,art,cc,ic from detvta where idvta={venta[0]}")
            for detvta in detvtas:
                pdf.set_font_size(8)
                pdf.cell(10,4,f"{detvta[0]}",1,0,'C')
                pdf.cell(80,4,f"{detvta[1]}",1,0)
                pdf.cell(35,4,f"{detvta[2]} cuotas de ${detvta[3]}",1,1,'C')

            cuotas = cuotaje(con,venta[0])
            pagadas = pglisttuples(con, f"select fecha,imp,rec,rbo,cobr from pagos where idvta={venta[0]} order by fecha")
            # Calculo el largo total que tendra la grilla de pagos
            if (len(cuotas)>len(pagadas)):
                max_el=len(cuotas)
            else:
                max_el=len(pagadas)

            # Formula para el calculo del espacio ocupable
            # if ((pdf.get_y()+max*7)>280):
            #     qpdf.add_page()
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
        pdf.set_font("Helvetica","B",18)
        pdf.cell(60,10,cliente[7],0,0,'L')
        pdf.set_font("Helvetica","",12)
        pdf.cell(40,8,f"Desde: {pmovtos[0]}",1,0,'C')
        pdf.cell(40,8,f"Hasta: {pmovtos[1]}",1,1,'C')
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
        if total_cobrado is None:
            total_cobrado = 0
        pdf.cell(165,10,f'Suma a cobrar esta planilla ${suma_a_cobrar}',1,1,'R')
        pdf.cell(165,10,f'Total a cobrar esta zona ${total_cobrable}',1,1,'R')
        pdf.cell(165,10,f'Total cobrado esta zona ${total_cobrado}',1,1,'R')
        pdf.cell(165,10,f'Porcentaje cobrado hasta ahora {total_cobrado/total_cobrable*100 :.2f}%',1,1,'R')
        pdf.cell(165,10,'Recordar que se debe cobrar el 90% del total para evitar redimensionamiento de zona',1,1,'R')



    pdf.output("/home/hero/ficha.pdf")


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
    # filelist = glob.glob('/home/hero/documentos/impresos/listapreciosGENERADA*.pdf')
    # for f in filelist:
    #     os.remove(f)
    # pdf.output(f"/home/hero/documentos/impresos/listapreciosGENERADA{aleatorio}.pdf")
    # No se la causa por la cual hice el nombre aleatorio
    pdf.output("/home/hero/documentos/impresos/listaprecios.pdf")
