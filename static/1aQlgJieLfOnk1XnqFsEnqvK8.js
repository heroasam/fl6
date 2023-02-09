  // main agregarcliente FfAJZZH0ytHuiD0aIFCFlNpfO
   function FfAJZZH0ytHuiD0aIFCFlNpfO(){
       return{
           cliente:{dni:'',nombre:'',calle:'',num:'',acla:'',barrio:'',tel:'',wapp:'',dnigarante:'',cuota_requerida:'',arts:''},
           calles:[],
           barrios:[],
           articulos:[],
           nombregarante:'',
           direcciongarante:'',
           obtenerCalles(){
               //nueva ruta para /ventas/getcalles CZI6X7BC6wNtseAN22HiXsmqc
	           axios.get('/CZI6X7BC6wNtseAN22HiXsmqc')
		            .then(res=>{this.calles=res.data.result})
           },
           obtenerBarrios(){
               //nueva ruta para /ventas/getbarrios w98LuAaWBax9c6rENQ2TjO3PR
	           axios.get('/w98LuAaWBax9c6rENQ2TjO3PR')
		            .then(res=>{this.barrios=res.data.result})
           },

           buscarDni(dni){
               //nueva ruta para /vendedor/buscaclientepordni MeHzAqFYsbb78KAVFAGTlZRW9
               axios.get('/MeHzAqFYsbb78KAVFAGTlZRW9/'+dni)
                    .then(res=>{
                        this.cliente = res.data.cliente;
                        msgSuccess('Cliente existente');
                    })
           },
           buscaGarante(dni){
               if(this.cliente.dnigarante!=''){
                   //nueva ruta para /ventas/obtenerdatosgarante 3ibzPLLq53RuFgIqkq6G3bSzO
                   axios.get('/3ibzPLLq53RuFgIqkq6G3bSzO/'+this.cliente.dnigarante)
                        .then(res=>{
                            this.nombregarante = res.data.garante[0].nombre;
                            this.direcciongarante = res.data.garante[0].direccion;
                        })
                        .catch(error=>msgError('El DNI no existe'))
               }
           },
           validarClienteNuevo(){
               if(this.cliente.dni==''){
                   msgError("Debe ingresar el DNI")
                   return;
               }
               if(this.cliente.nombre==''){
                   msgError("Debe ingresar el Nombre");
                   return;
               }
               if(this.cliente.calle==''||!this.calles.includes(this.cliente.calle)){
                   msgError("Verifique que ingreso una calle correcta");
                   return;
               }
               if(this.cliente.num==''){
                   msgError("Debe ingresar el numero de la casa");
                   return;
               }
               if(this.cliente.barrio==''||!this.barrios.includes(this.cliente.barrio)){
                   msgError("Verifique que ingreso un barrio correcto");
                   return;
               }
               if(this.cliente.cuota_requerida==''){
                   msgError("Debe ingresar la cuota que va a vender");
                   return;
               }
               if(this.cliente.arts==''){
                   msgError("Debe ingresar los articulos que va a vender");
                   return;
               }
               this.pedirAutorizacion();
           },
           pedirAutorizacion(){
               idButton = document.getElementById('buttonPedirAutorizacion')
               idButton.disabled=true
               axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value;
               // nueva ruta para /vendedor/envioclientenuevo pEmPj7NAUn0Odsru4aL2BhlOu
               axios.post('/pEmPj7NAUn0Odsru4aL2BhlOu',this.cliente)
                   .then(res=>{
                       if(res.data.otroasignado==1){
                           msgError('Error','Este cliente ya tiene un dato hecho y esta asignado a otro vendedor.',10000)
                           return
                       }
                        this.cliente.idautorizacion = res.data.idautorizacion
                                                                       msgSuccess('autorizacion enviada. Espere la repuesta.')
                                                                       //enviar un whatsapp al Fede informando del pedido de autorizacion
                                                                       let msg = `Solicito autorizacion para ${this.cliente.nombre}
como CLIENTE NUEVO.
uedo a la espera. Gracias.`;
                                                                       let tipo = "pedido-autorizacion";
                                                                       let data = {msg,tipo};
                                                                       axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value;
                                                                       // envia a /vendedor/wappaut
	                                                                   axios.post('/3ZbXanrRQalY6JL5eOBi49Nyc',data)
                                                                       // window.location envia a /vendedor/listadatos
                                                                            .then(res=>{
                                                                               let atendido = 0
                                                                               let interval =setInterval(()=>{
                                                                                   axios.get('/u0IEJT3i1INZpKoNKbyezlfRy/'+this.cliente.idautorizacion)
                                                                                   //nueva ruta para /vendedor/isatendido u0IEJT3i1INZpKoNKbyezlfRy
                                                                                       .then(res=>{
                                                                                           atendido = res.data.tomado
                                                                                           if(atendido==1){
                                                                                               msgDelay('la autorizacion se esta procesando. Puede tardar un poco...',300000)
                                                                                               clearTimeout(interval)
                                                                                               // setTimeout(()=>{
                                                                                               // window.location = "/2xxXix5cnz7IKcYegqs6qf0R6";
                                                                                               // },60010)
                                                                                               let intervalauth = setInterval(()=>{
                                                                                                   axios.get('/ymIVWKdjgnCeJvo2zcodwRTQM/'+this.cliente.idautorizacion)
                                                                                                   // nueva ruta para /vendedor/isrespondidoauth ymIVWKdjgnCeJvo2zcodwRTQM
                                                                                                   .then(res=>{
                                                                                                       switch(res.data.respuesta){
                                                                                                       case "autorizado":
                                                                                                           msgSuccess('Aprobado','El dato fue autorizado',10000)
                                                                                                           clearTimeout(intervalauth)
                                                                                                           setTimeout(()=>{
                                                                                                               window.location = "/2xxXix5cnz7IKcYegqs6qf0R6";},10100)
                                                                                                           break;
                                                                                                       case "sigueigual":
                                                                                                           msgWarning('La cuota fue rechazada','La cuota no fue autorizada. Se puede vender hasta la cuota basica.',10000)
                                                                                                           clearTimeout(intervalauth)
                                                                                                           setTimeout(()=>{
                                                                                                               window.location = "/2xxXix5cnz7IKcYegqs6qf0R6";},10100)
                                                                                                           break;
                                                                                                       case "rechazado":
                                                                                                           msgError('Rechazado','El dato ha sido rechazado. No se le puede vender',10000)
                                                                                                           clearTimeout(intervalauth)
                                                                                                           setTimeout(()=>{
                                                                                                               window.location = "/2xxXix5cnz7IKcYegqs6qf0R6";},10100)
                                                                                                           break;
                                                                                                       }
                                                                                                   })},10000) // cierro el then de isrespondido auth setInterval intervalauth
                                                                                           } // cierro el if de atendido==1
                                                                                       }) // cierra el then de isatendido
                                                                                   },10000) // cierra el setInterval Interval

                                                                            })}) // cierro el then de los datos enviados
           }, //cierro la function
       }}





function DRpCmN0kdtSCE2mWXi5CiVycj(){
       return{
           listaVisitasVendedor:[],
           listaVisitasVendedor_:[],
           listaFechas:[],
           listaFechas_:[],
           fecha:'',
           vdor:'',
           listaVendedores:[],
           getVisitasVendedor(){
               //nueva ruta para /vendedor/getvisitavdor F8cq9GzHJIG9hENBo0Xq7hdH7
               axios.get('/F8cq9GzHJIG9hENBo0Xq7hdH7')
                    .then(res=>{
                        this.listaVisitasVendedor = res.data.visitasvendedor;
                        this.listaVisitasVendedor.map(row=>row.fecha=dayjs.utc(row.fecha).format('YYYY-MM-DD'));
                        this.listaFechas = res.data.fechasvisitas;
                        this.listaFechas.map(row=>row.fecha=dayjs.utc(row.fecha).format('YYYY-MM-DD'));
                        this.listaFechas_ = this.listaFechas;

                    })
           },
           expandChildren(fecha){
               if(this.fecha==fecha && this.listaVisitasVendedor_.length>0){
                   this.listaVisitasVendedor_ = [];
                   return;
               }
               this.listaVisitasVendedor_ = this.listaVisitasVendedor.filter(row=>row.vdor==this.vdor);
               this.listaVisitasVendedor_=this.listaVisitasVendedor.filter(row=>row.fecha==fecha);
               this.fecha = fecha;
               setTimeout(()=>{
                   $tbody = document.querySelector('tbody');
                   $trfecha = document.getElementById(fecha);
                   let arrayrows = Array.from($tbody.children);
                   let children = arrayrows.filter(row=>row.classList.contains('children'));
                   children = children.reverse();
                   for(el of children){
                       $tbody.insertBefore(el,$trfecha.nextSibling);
               }},10)
           },
           filtrarVdor(vdor){
               this.vdor=vdor;
               this.listaFechas_ = this.listaFechas.filter(row=>row.vdor==vdor);
           },

       }
}

 function BuuZZCDVMyzK4I1OcGEvNeeob(){
     return{
         listadoDatos:[],
         listadoDatos_:[],
         listaItemsDatos:[],
         agrupar:'',
         listaArticulos:[],
         listaArtComprados:[],
         Articulos:[],
         Dato:{},
         Datos:{},
         cuota_basica:'',
         verCard:false,
         Venta:{cnt:'', art:''},
         dnivalidado:false,
         dnigarantevalidado:false,
         sumaCuota:'',
         verNotificacionAutorizacion:false,
         nombregarante:'',
         direcciongarante:'',
         getListadoDatosVendedor(){
             // nueva ruta: /VGIdj7tUnI1hWCX3N7W7WAXgU
             // para /vendedor/getlistadodatosvendedor
             axios.get('/VGIdj7tUnI1hWCX3N7W7WAXgU')
                  .then(res=>{
                      this.listadoDatos = res.data.listadodatos;
                      this.listadoDatos.map(row=>row.fecha=dayjs.utc(row.fecha).format('YYYY-MM-DD'));
                      this.listadoDatos.map(row=>row.fecha_visitar=dayjs.utc(row.fecha_visitar).format('YYYY-MM-DD'));
                      this.listadoDatos_ = this.listadoDatos;
                      this.agrupar = res.data.agrupar
                      this.getListaItems();
                      this.listadoDatos_.sort((a,b)=>{
                          let s1 = a.nombre.toLowerCase(),
                              s2 = b.nombre.toLowerCase()

                          if(s1>s2) return 1
                          if(s1<s2) return -1
                          if(s1==s2) return 0
                      })
                  })
         },
         getListaItems(){
             let arrayItems = []
             if(this.agrupar=='zonas'){
                 arrayItems = this.listadoDatos.filter(row=>row.resultado==null).map(row=>row.zona);
             }else{
                 arrayItems = this.listadoDatos.filter(row=>row.resultado==null).map(row=>row.calle);
             }
             let itemDatos = {};
             this.listaItemsDatos = [];
             arrayItems.forEach(item=>{
                 if (item in itemDatos){
                     itemDatos[item] += 1;
                 }else{
                     itemDatos[item] = 1;

                 }
             })
             for (let item in itemDatos){
                 this.listaItemsDatos.push(`${item}-${itemDatos[item]}`);
             }
             this.listaItemsDatos = this.listaItemsDatos.sort()
         },
         getListadoArt(){
             // nueva ruta /kHEhacFNmI2vflFHBbaT1AQ1Z
             // para /vendedor/getlistadoarticulos
             axios.get('/kHEhacFNmI2vflFHBbaT1AQ1Z')
                  .then(res=>{
                      this.Articulos = res.data.articulos;
                      this.listaArticulos = this.Articulos.map(row=>row.art);
                  })
         },
         filtraDatosPorVendedor(vdor){
             this.listadoDatos_ = this.listadoDatos.filter(row=>row.vendedor==vdor);
         },
         filtraDatosPorStatus(status){
             switch(status){
                 case 'vendidos':
                 this.listadoDatos_ = this.listadoDatos.filter(row=>row.resultado==1);
                 break;
                 case 'anulados':
                 this.listadoDatos_ = this.listadoDatos.filter(row=>row.resultado==0);
                 break;
                 case 'pendientes':
                 this.listadoDatos_ = this.listadoDatos.filter(row=>row.resultado==null);
                 break;
                 case 'todos':
                 this.listadoDatos_ = this.listadoDatos;
                 break;
             }
         },
         filtraPorItem(item){
             // la zona me viene en formato jid1-5 por eso tengo que limpiar
             pattern = /[^-]*/gi;
             item = pattern.exec(item);
             if(this.agrupar=='zonas'){
                 this.listadoDatos_ = this.listadoDatos.filter(row=>row.zona==item);
                 // ordeno por calle
                 this.listadoDatos_.sort((a,b)=>{
                     let fa = a.calle.toLowerCase(),
                         fb = b.calle.toLowerCase();

                     if (fa < fb) {
                         return -1;
                     }
                     if (fa > fb) {
                         return 1;
                     }
                     return 0;
                 })
             }else{
                 this.listadoDatos_ = this.listadoDatos.filter(row=>row.calle==item);
                 // ordeno por numero
                 this.listadoDatos_.sort((a,b)=>a.num - b.num)
             }
             this.verCard = false;
         },
         abrirCliente(id){
             this.Dato = this.listadoDatos.filter(row=>row.idcliente==id)[0];
             this.verCard = true;
         },
         editarWapp(){
             toggleModal("modal-edicion-wapp");
         },
         guardarWapp(){
             // nueva ruta para /vendedor/editarwapp
             // /uQ3gisetQ8v0n6tw81ORnpL1s
             toggleModal("modal-edicion-wapp");
             axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value;
             axios.post('/uQ3gisetQ8v0n6tw81ORnpL1s',this.Dato)
                                                                 .then(res=>{
                                                                     msgSuccess('WhatsApp editado correctamente');
                                                                 })
                                                                 .catch(error=>{
                                                                     msgError('Error. No se hizo la edicion');
                                                                 })
         },
         venderDato(iddato){
             //recargamos el Dato desde el servidor para asegurarnos ultimos valores
             // nueva ruta para /vendedor/getdato
             // pnZWxv9Nicwt6TQ6zxohzvats
             idButton = document.getElementById('buttonPasarVenta')
             idButton.disabled=false
             axios.get('/pnZWxv9Nicwt6TQ6zxohzvats/'+iddato)
                  .then(res=>{
                      this.Dato=res.data.dato;
                      this.Dato.fecha=dayjs.utc(this.Dato.fecha).format('YYYY-MM-DD');
                      this.Dato.fecha_visitar=dayjs.utc(this.Dato.fecha_visitar).format('YYYY-MM-DD');
                      this.listaArtComprados = [];
                      this.Venta = {cnt:'', art:'',primera:dayjs.utc().format('YYYY-MM-DD'),dnigarante:this.Dato.dnigarante};
                      this.sumaCuota = '';
                      this.verNotificacionAutorizacion = false;
                      if(this.Dato.nosabana==1){
                          //filtra this.listaArticulos y saca sabanas
                          this.listaArticulos = this.listaArticulos.filter(row=>!row.includes('Sab'))
                      }
                      toggleModal("modal-pasar-venta");
                  })
         },
         anularDato(iddato){
             // nueva ruta para /vendedor/anulardato
             // /UtVc3f6y5hfxu2dPmcrV9Y7mc
             axios.get('/UtVc3f6y5hfxu2dPmcrV9Y7mc/'+iddato)
                  .then(res=>{
                      msgSuccess('Dato anulado correctamente');
                      this.getListadoDatosVendedor();
                      this.verCard = false;
                  })
                  .catch(error=>{
                      msgError('Hubo un error. El dato no se pudo anular');
                  })
         },
         mudoDato(iddato){
             Swal.fire({
                 title: '¿Esta seguro?',
                 text: `Se pondra como mudado el dato`,
                 icon: 'warning',
                 showCancelButton: true,
                 confirmButtonColor: '#3085d6',
                 cancelButtonColor: '#d33',
                 confirmButtonText: 'Si, ponerlo!'
             }).then((result) => {
                 if (result.isConfirmed) {
                     // nueva ruta para /vendedor/mudodato
                     // /gJUmonE8slTFGZqSKXSVwqPJ1
                     axios.get('/gJUmonE8slTFGZqSKXSVwqPJ1/'+iddato)
                         .then(res=>{
                             msgSuccess('Dato informado correctamente');
                             this.getListadoDatosVendedor();
                             this.verCard = false;
                         })
                         .catch(error=>{
                             msgError('Hubo un error. El dato no se pudo procesar');
                         })
                 }})
         },
         fallecioDato(iddato){
              Swal.fire({
                  title: '¿Esta seguro?',
                  text: `Se pondra como fallecido el dato`,
                  icon: 'warning',
                  showCancelButton: true,
                  confirmButtonColor: '#3085d6',
                  cancelButtonColor: '#d33',
                  confirmButtonText: 'Si, ponerlo!'
              }).then((result) => {
                  if (result.isConfirmed) {
                      //nueva ruta para /vendedor/falleciodato
                      // /sLTFCMArYAdVsrEgwsz7utyRi
                      axios.get('/sLTFCMArYAdVsrEgwsz7utyRi/'+iddato)
                          .then(res=>{
                              msgSuccess('Dato informado correctamente');
                              this.getListadoDatosVendedor();
                              this.verCard = false;
                          })
                          .catch(error=>{
                              msgError('Hubo un error. El dato no se pudo procesar');
                          })
                  }})
         },
         fecharDato(iddato){
             toggleModal("modal-fechar-dato");
             this.verCard = false;
         },
         guardarDatoFechado(){
             //nueva ruta para /vendedor/guardardatofechado
             // /HvjJNtFgF71pRYafzcTC74nUt
             toggleModal("modal-fechar-dato");
             axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value;
             axios.post('/HvjJNtFgF71pRYafzcTC74nUt',this.Dato)
                                                                 .then(res=>{
                                                                     msgSuccess('Dato fechado con exito');
                                                                 })
                                                                 .catch(error=>{
                                                                     msgError('Hubo un error. El dato no se fecho');
                                                                 })
         },
         noEstabaDato(iddato){
             // nueva ruta para /vendedor/noestabadato
             // /G9S85pbqWVEX17nNQuOOnpxvn
             axios.get('/G9S85pbqWVEX17nNQuOOnpxvn/'+iddato)
             this.verCard = false;
         },
         validarDni(dni){
             //nueva ruta para /vendedor/validardni
             // /fc3vpQG6SzEH95Ya7kTJPZ48M
             datos = {dni:dni, id: this.Dato.idcliente};
             if(dni==undefined) {
                 console.log( 'dni inexistente')
                 return
             }
             console.log( datos)
             axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value;
             axios.post('/fc3vpQG6SzEH95Ya7kTJPZ48M',datos)
                                                                 .then(res=>{
                                                                     this.dnivalidado = true;
                                                                 })
                                                                 .catch(error=>{
                                                                     this.dnivalidado = false;
                                                                     msgError('el DNI ingresado no corresponde al cliente');
                                                                 })
         },
         agregarArticulo(cnt,art){
             if(cnt!=''&&art!=''){
                 let cuota = this.Articulos.filter(row=>row.art==art)[0].cuota;
                 let cc = 6;
                 let total = cnt * cuota * cc;
                 let id = this.listaArtComprados.length;
                 this.listaArtComprados.push({id,cnt,art,cc,cuota,total});
                 this.Venta.cnt = '';
                 this.Venta.art = '';
                 this.sumaCuota = this.listaArtComprados.map(row=>row.total).reduce((a,b)=>a+b,0)/6;
             }
         },
         borrarItem(iditem){
             let arrayId = this.listaArtComprados.map(row=>row.id);
             idBorrar = arrayId.indexOf(iditem);
             this.listaArtComprados.splice(idBorrar, 1);
             this.sumaCuota = this.listaArtComprados.map(row=>row.total).reduce((a,b)=>a+b,0)/6;
         },
         pedirAutorizacion(){
             this.verNotificacionAutorizacion = true;
             //registrar pedido autorizacion en tabla autorizacion
             this.Dato.cuota_requerida = this.sumaCuota;
             let arrayArts = [];
             this.listaArtComprados.map(row=>{
                 arrayArts.push(row.cnt+' '+row.art);
             })
             this.Dato.arts = arrayArts.toString();
             // nueva ruta para /vendedor/registrarautorizacion
             // /vaHQ2gFYLW2pIWSr5I0ogCL0k
             axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value;
             axios.post('/vaHQ2gFYLW2pIWSr5I0ogCL0k',this.Dato)
                 .then(res=>{
                     this.Dato.idautorizacion = res.data.idautorizacion
                 })
             //enviar un whatsapp al Fede informando del pedido de autorizacion
             let msg = `Solicito autorizacion para ${this.Dato.nombre}
con una compra de ${this.Dato.arts}
y una cuota de $${this.sumaCuota}.
Quedo a la espera. Gracias.`;
             let tipo = "autorizacion venta";
             let data = {msg,tipo};
             // nueva ruta para /vendedor/wappaut
             // /3ZbXanrRQalY6JL5eOBi49Nyc
             axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value
	         axios.post('/3ZbXanrRQalY6JL5eOBi49Nyc',data)
              .then(res=>{
                                                                               let atendido = 0
                                                                               let interval =setInterval(()=>{
                                                                                   axios.get('/u0IEJT3i1INZpKoNKbyezlfRy/'+this.Dato.idautorizacion)
                                                                                   //nueva ruta para /vendedor/isatendido u0IEJT3i1INZpKoNKbyezlfRy
                                                                                       .then(res=>{
                                                                                           atendido = res.data.tomado
                                                                                           if(atendido==1){
                                                                                               msgDelay('la autorizacion se esta procesando. Puede tardar un poco...',300000)
                                                                                               clearTimeout(interval)
                                                                                               // setTimeout(()=>{
                                                                                               // window.location = "/2xxXix5cnz7IKcYegqs6qf0R6";
                                                                                               // },60010)
                                                                                               let intervalauth = setInterval(()=>{
                                                                                                   axios.get('/ymIVWKdjgnCeJvo2zcodwRTQM/'+this.Dato.idautorizacion)
                                                                                                   // nueva ruta para /vendedor/isrespondidoauth ymIVWKdjgnCeJvo2zcodwRTQM
                                                                                                   .then(res=>{
                                                                                                       switch(res.data.respuesta){
                                                                                                       case "autorizado":
                                                                                                           msgSuccess('Aprobado','El dato fue autorizado',10000)
                                                                                                           clearTimeout(intervalauth)
                                                                                                           setTimeout(()=>{
                                                                                                               window.location = "/2xxXix5cnz7IKcYegqs6qf0R6";},10100)
                                                                                                           break;
                                                                                                       case "sigueigual":
                                                                                                           msgWarning('La cuota fue rechazada','La cuota no fue autorizada. Se puede vender hasta la cuota maxima que tenia antes.',10000)
                                                                                                           clearTimeout(intervalauth)
                                                                                                           setTimeout(()=>{
                                                                                                               window.location = "/2xxXix5cnz7IKcYegqs6qf0R6";},10100)
                                                                                                           break;
                                                                                                       case "rechazado":
                                                                                                           msgError('Rechazado','El dato ha sido rechazado. No se le puede vender',10000)
                                                                                                           clearTimeout(intervalauth)
                                                                                                           setTimeout(()=>{
                                                                                                               window.location = "/2xxXix5cnz7IKcYegqs6qf0R6";},10100)
                                                                                                           break;
                                                                                                       }
                                                                                                   })},10000) // cierro el then de isrespondido auth setInterval intervalauth
                                                                                           } // cierro el if de atendido==1
                                                                                       }) // cierra el then de isatendido
                                                                                   },10000) // cierra el setInterval Interval

                                                                           }) // cierro el then de los datos enviados
         }, //cierro la function
         pasarVenta(){
             if(this.dnivalidado==false){
                 msgError('El DNI del cliente debe coincidir con nuestros registros');
                 return;
             }
             if(this.listaArtComprados.length==0){
                 msgError('Debe agregar articulos comprados');
                 return;
             }
             if(!dayjs(this.Venta.primera).isAfter(dayjs.utc())){
                 msgError('La fecha de primer cuota debe ser posterior a hoy');
                 return;
             }
             if(this.sumaCuota>this.Dato.cuota_maxima){
                 msgError('La venta excede la cuota maxima aprobada');
                 return;
             }
             idButton = document.getElementById('buttonPasarVenta')
             idButton.disabled=true
             this.Dato.arts = this.listaArtComprados;
             this.Dato.primera = this.Venta.primera;
             this.Dato.cuota = this.sumaCuota;
             axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value;
             // nueva ruta para /vendedor/pasarventa
             // /xuNzBi4bvtSugd5KbxSQzD0Ey
             axios.post('/xuNzBi4bvtSugd5KbxSQzD0Ey',this.Dato)
                                                                 .then(res=>{
                                                                     this.getListadoDatosVendedor();
                                                                     msgSuccess('Venta pasada con exito');
                                                                     toggleModal("modal-pasar-venta");
                                                                     axios.get('/pnZWxv9Nicwt6TQ6zxohzvats/'+this.Dato.id)
                                                                         .then(res=>{
                                                                             this.Dato=res.data.dato;
                                                                             this.Dato.fecha=dayjs.utc(this.Dato.fecha).format('YYYY-MM-DD');
                                                                             this.Dato.fecha_visitar=dayjs.utc(this.Dato.fecha_visitar).format('YYYY-MM-DD');
                                                                             this.enviarWappCliente(this.Dato);
                                                                         })
                                                                 })
                                                                 .catch(error=>{
                                                                     msgError('Hubo un error y la venta no se proceso.');
                                                                 })

         },
         hacerLlamada(tel){
             re = /[0-9]*/;
             tel = re.exec(tel)[0];
             window.location.href = 'tel:' + tel;
         },
         buscaGarante(dni){
             if(this.Venta.dnigarante!=0 && this.Venta.dnigarante!=''){
                 // nueva ruta para /ventas/obtenerdatosgarante
                 // /3ibzPLLq53RuFgIqkq6G3bSzO
                 axios.get('/3ibzPLLq53RuFgIqkq6G3bSzO/'+this.Venta.dnigarante)
                      .then(res=>{
                          this.nombregarante = res.data.garante[0].nombre;
                          this.dnigarantevalidado = true;
                      })
                      .catch(error=>{
                          msgError('El DNI no existe');
                          this.dnigarantevalidado = false;
                      })
             }else{
                 this.nombregarante = '';
             }
         },
         enviarWappCliente(datos){
             let arts = '';
             let cuotas;
             for (let item of this.listaArtComprados){
                 arts += ` ${item.cnt} ${item.art} `;
                 cuotas = item.cc;
             }
             let msg = `Estimado cliente: ${datos.nombre}, agradecemos su compra de ${arts}.
Le recordamos que el plan de pagos elegido es de ${cuotas} cuotas mensuales de $${datos.monto_vendido/cuotas} y la primer cuota vence el dia ${this.Venta.primera} para cualquier consulta no dude en contactarnos, estamos a su disposición!.`;
             let wapp = datos.wapp;
             let idcliente = datos.idcliente;
             let file = 'informacion-importante';
             let data = {msg,wapp,idcliente,file};
             axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value;
             // nueva ruta para /vendedor/wapp
             // /hX53695XAOpaLY9itLgmghkhH
	         axios.post('/hX53695XAOpaLY9itLgmghkhH',data)
                                                                 .then(res=>{
                                                                     //nueva ruta para /vendedor/filewapp
                                                                     // /4qUK6eNZnCYjIiGTt3HSj2YDp
                                                                     axios.post('/4qUK6eNZnCYjIiGTt3HSj2YDp',data)
                                                                 })
         },
     }
 }
 function GnIVzsHTcsg1sQFsVD7xfw7Dc(){
     return{
         listaArtVendedor:[],
         getArtVendedor(){
             //nueva ruta para /vendedor/getcargavendedor k8E5hsVs4be3jsJJaob6OQmAX
             axios.get('/k8E5hsVs4be3jsJJaob6OQmAX')
                  .then(res=>{
                      this.listaArtVendedor = res.data.artvendedor
                  })
         },

     }
 }
 function IkKmqwFGcDGnhd8x1TvBO6C6p(){
     return{
         listaComisiones:[],
         listaComisiones_:[],
         totalComision:'',
         listaFechas:[],
         fecha:'',
         getComisionesVdor(){
             //nueva ruta para /vendedor/getcomisionesparavendedor
             axios.get('/IrV7gmqz4Wu8Q8rwmXMftphaB')
                  .then(res=>{
                      this.listaComisiones = res.data.comisiones
                      this.listaComisiones.map(row=>row.fecha=dayjs.utc(row.fecha).format('YYYY-MM-DD'))
                      this.listaComisiones.map(row=>row.com=parseFloat(row.com))
                      this.totalComision = parseFloat(this.listaComisiones.map(row=>row.com).reduce((a,b)=>a+b,0))
                      this.listaFechas = res.data.fechascomisiones
                      this.listaFechas.map(row=>row.fecha=dayjs.utc(row.fecha).format('YYYY-MM-DD'))
                      this.listaFechas.map(row=>row.comision=parseFloat(row.comision))
                  })
         },
         expandChildren(fecha){
              if(this.fecha==fecha && this.listaComisiones_.length>0){
                  this.listaComisiones_ = []
                  return
              }
             this.listaComisiones_ = this.listaComisiones.filter(row=>row.fecha==fecha)
             this.fecha = fecha
             setTimeout(()=>{
             $tbody = document.querySelector('tbody')
             $trfecha = document.getElementById(fecha)
             let arrayrows = Array.from($tbody.children)
             let children = arrayrows.filter(row=>row.classList.contains('children'))
             children = children.reverse()
             for(el of children){
                 $tbody.insertBefore(el,$trfecha.nextSibling)
             }},10)
         },
         avisarRetiroZona(){
             msgDelay("se estan enviando los mensajes...")
             let msg = `Retiro zona.`;
             let tipo = "retiro zona";
             let data = {msg,tipo};
             // nueva ruta para /vendedor/wappaut
             // /3ZbXanrRQalY6JL5eOBi49Nyc
             axios.defaults.headers.common['X-CSRF-TOKEN'] = this.$refs.token.value
	         axios.post('/3ZbXanrRQalY6JL5eOBi49Nyc',data)
                 .then(res=>{
                     msgSuccess("Avisado retiro zona.")
                 })
           },

     }
 }
