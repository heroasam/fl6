from fpdf import FPDF 
from lib import pgdict0, pgddict, per, desnull,pglflat
from datetime import date

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
    pdf.set_margins(30,30)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    lpg ='('
    for dni in ldni:
        lpg+=dni+','
    lpg = lpg[0:-1]+')'
    listdni = pglflat(con,f"select dni from clientes where dni in {lpg} order by calle,num")
    
    i=1
    lisdatos = [] # lista que contendra los datos del resumen
    # dictPos = {} # diccionario de posisiones de ficha en paginas
    # dictNombre = {} # dicc que guarda los nombres para el resumen
    # dictDir = {} # dicc que guarda la direccion para el resumen
    for dni in listdni:
        #regla para que no comience un encabezado con poco espacio
        if (pdf.get_y()>250):
            pdf.add_page()
            pdf.set_y(15)
        cliente = pgdict0(con,f"select nombre,calle,num,tel,wapp,pmovto,barrio,zona,acla,mjecobr,horario,id from clientes where dni='{dni}'")
        print(cliente[4])
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
        if cliente[5]<date.today():
            pmovto = date.today().strftime('%Y-%m-%d')
        else:
            pmovto = cliente[5]
        lisdatos.append((i,cliente[0][0:38],cliente[1]+' '+cliente[2],pdf.page_no(),pmovto))
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
            cur =con.cursor()
            #cur.execute(f"select gc({venta['id']})")
            cur.close()
            #cuotas = pgddict(con, f"select * from cuotas where debe>0 and idvta={venta['id']}")
            pagadas = pgddict(con, f"select fecha,imp,rec,rbo,cobr from pagos where idvta={venta[0]} order by fecha")
            # Calculo el largo total que tendra la grilla de pagos
            # if (len(cuotas)>len(pagadas)):
            #     max=len(cuotas)
            # else:
            #     max=len(pagadas)
            # Formula para el calculo del espacio ocupable
            # if ((pdf.get_y()+max*7)>280):
            #     pdf.add_page()
            #     pdf.set_y(15)

            pdf.ln(2)
            pdf.set_font_size(10)
            y0 = pdf.get_y()
            # pdf.cell(80,6,"Cuotas a Pagar",0,1)
            # pdf.set_font_size(8)
            # for cuota in cuotas:
            #     pdf.cell(5,4,f"{cuota['nc']}",1,0,'C')
            #     pdf.cell(25,4,f"{cuota['vto']}",1,0,'C')
            #     pdf.cell(15,4,f"${cuota['debe']}",1,1,'C')
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
            pdf.ln(10)
        pdf.line(10,pdf.get_y()-5,200,pdf.get_y()-5)
        i+=1
    
    if (len(ldni)>1):
        pdf.add_page()
        # for x in dictPos.keys():
        #     pdf.cell(10,5,str(x),1,0,'C')  
        #     pdf.cell(60,5,dictNombre[x],1,0,'L') 
        #     pdf.cell(60,5,dictDir[x],1,0,'L') 
        #     pdf.cell(20,5,'Pag N°'+str(dictPos[x]),1,1,'C')
        for row in lisdatos:
            pdf.cell(25,5,str(row[4]),1,0,'C')
            pdf.cell(10,5,str(row[0]),1,0,'C')
            pdf.cell(60,5,row[1],1,0,'L')
            pdf.cell(60,5,row[2],1,0,'L')
            pdf.cell(20,5,'Pag N°'+ str(row[3]),1,1,'C')
    pdf.output("ficha.pdf")

def loterbo(con, lrbo, fecha, cobr, idlote):
    pdf=FPDF()
    pdf.set_margins(15,15)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    pdf.set_y(5)
    pdf.cell(20,6,str(fecha),0,0,'C')
    pdf.cell(20,6,f"Cobr {cobr}",0,0,'C')
    pdf.cell(20,6,f"Lote N° {idlote}",0,1,'C')
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
    # pdf.set_y(-50)
    # pdf.set_x(150)
    pdf.cell(28,6,'Total',1,0,'R')
    pdf.cell(25,6,'$',1,1)
    # pdf.set_x(150)
    pdf.cell(28,6,'Comision',1,0,'R')
    pdf.cell(25,6,'$',1,1)
    # pdf.set_x(150)
    pdf.cell(28,6,'Viaticos',1,0,'R')
    pdf.cell(25,6,'$',1,1)
    # pdf.set_x(150)
    pdf.cell(28,6,'A RENDIR',1,0,'R')
    pdf.cell(25,6,'$',1,1)
    pdf.output("loterbo.pdf")


def listado(con, ldni):
    pdf = MyFPDF()
    pdf.set_margins(30,30)
    pdf.add_page()
    pdf.set_font("Helvetica","",10)
    lpg ='('
    for dni in ldni:
        lpg+=dni+','
    lpg = lpg[0:-1]+')'
    listdni = pglflat(con,f"select dni from clientes where dni in {lpg} order by calle,num")

    for dni in listdni:
        cliente = pgdict0(con, f"select nombre,calle,num,acla,dni from clientes where dni='{dni}'")
        pdf.cell(10,6,str(round(int(cliente[4])/1000000)),0,0)
        pdf.cell(80,6,cliente[0][0:38],0,0)
        pdf.cell(80,6,cliente[1]+' '+cliente[2], 0, 1)
        pdf.cell(160,6,cliente[3],0,1)
        pdf.line(10,pdf.get_y(),200,pdf.get_y())
    pdf.output("listado.pdf")

    

    

